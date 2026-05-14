from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class ThesisChunk:
    chunk_id: str
    source_file: str
    text: str


def load_query_pool(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    out: list[tuple[str, str]] = []
    try:
        raw = json.loads(text)
        # New format: plain list of queries, no theme.
        if isinstance(raw, list):
            for q in raw:
                s = str(q).strip()
                if s:
                    out.append(("", s))
            return out
        # Legacy format: {"themes": {...}} or {"Theme": [...]}
        if isinstance(raw, dict) and isinstance(raw.get("themes"), dict):
            raw = raw["themes"]
        if isinstance(raw, dict):
            for theme, queries in raw.items():
                if not isinstance(queries, list):
                    continue
                for q in queries:
                    s = str(q).strip()
                    if s:
                        out.append((str(theme).strip(), s))
            return out
        raise ValueError("Unsupported query pool JSON format.")
    except json.JSONDecodeError:
        # Fallback for lightly malformed files: extract quoted lines.
        for line in text.splitlines():
            s = line.strip()
            if not s:
                continue
            m = re.match(r'^"(.+?)"\s*,?$', s)
            if m:
                q = m.group(1).strip()
                if q:
                    out.append(("", q))
        if out:
            return out
        raise


_SPLIT_MARKER = re.compile(r"\s*<split_chunck>\s*", re.IGNORECASE)


def _normalize_chunk_preserving_paragraphs(raw: str) -> str:
    """Strip edges; keep blank-line breaks between paragraphs; collapse whitespace inside each paragraph."""
    raw = raw.strip()
    if not raw:
        return ""
    paragraphs = re.split(r"\n\s*\n", raw)
    norm: list[str] = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        norm.append(" ".join(para.split()))
    return "\n\n".join(norm)


def split_at_split_markers(text: str) -> list[str]:
    """Split thesis source on `<split_chunck>` markers; preserve paragraph breaks within each chunk."""
    parts = _SPLIT_MARKER.split(text.strip())
    cleaned = [_normalize_chunk_preserving_paragraphs(p) for p in parts]
    return [c for c in cleaned if c]


def load_thesis_chunks(chunks_dir: Path) -> list[ThesisChunk]:
    files = sorted(chunks_dir.glob("*.md"))
    chunks: list[ThesisChunk] = []
    chunk_no = 1
    for fp in files:
        text = fp.read_text(encoding="utf-8")
        for block in split_at_split_markers(text):
            chunks.append(
                ThesisChunk(
                    chunk_id=f"chunk_{chunk_no:03d}",
                    source_file=fp.name,
                    text=block,
                )
            )
            chunk_no += 1
    return chunks


def map_queries_to_top_chunks(
    queries: list[tuple[str, str]],
    chunks: list[ThesisChunk],
    model_name: str = EMBED_MODEL,
) -> list[dict]:
    if not queries:
        return []
    if not chunks:
        return []

    model = SentenceTransformer(model_name)
    q_texts = [q for _, q in queries]
    c_texts = [c.text for c in chunks]

    q_vecs = np.asarray(
        model.encode(q_texts, normalize_embeddings=True, show_progress_bar=False),
        dtype=np.float32,
    )
    c_vecs = np.asarray(
        model.encode(c_texts, normalize_embeddings=True, show_progress_bar=False),
        dtype=np.float32,
    )

    sims = q_vecs @ c_vecs.T
    out: list[dict] = []
    for qi, (theme, query) in enumerate(queries):
        best_ci = int(np.argmax(sims[qi]))
        best_score = float(sims[qi, best_ci])
        best = chunks[best_ci]
        out.append(
            {
                "theme": theme,
                "query": query,
                "top_chunk_id": best.chunk_id,
                "top_chunk_source_file": best.source_file,
                "similarity": round(best_score, 4),
                "top_chunk_text": best.text,
            }
        )
    return out


def write_markdown(rows: list[dict], out_path: Path) -> None:
    lines: list[str] = [
        "# Query to Top Thesis Chunk",
        "",
        "Top-1 chunk per query using cosine similarity on normalized embeddings",
        f"(`{EMBED_MODEL}`, same embedding style as `parable_pipeline.py`).",
        "",
        "Chunk prose is not duplicated here; it lives in `cli_reader_data/thesis_chunks_inventory.md`.",
        "",
    ]
    for i, row in enumerate(rows, start=1):
        header = row["theme"] if row["theme"] else "Query"
        lines.append(f"## {i:02d}. {header}")
        lines.append("")
        lines.append(f"**Query:** {row['query']}")
        lines.append("")
        lines.append(
            f"**Top chunk:** `{row['top_chunk_id']}` from `{row['top_chunk_source_file']}` "
            f"(similarity: `{row['similarity']}`)"
        )
        lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def write_chunk_inventory_markdown(chunks: list[ThesisChunk], out_path: Path) -> None:
    lines: list[str] = [
        "# Thesis Chunk Inventory",
        "",
        "Chunks split at `<split_chunck>` markers under `body_extension_archive_reader/thesis_chunks`; "
        "blank lines between paragraphs are kept inside each chunk.",
        "",
    ]
    for i, chunk in enumerate(chunks, start=1):
        lines.append(f"## {i:02d}. `{chunk.chunk_id}`")
        lines.append("")
        lines.append(f"**Source file:** `{chunk.source_file}`")
        lines.append("")
        lines.append(chunk.text)
        lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> None:
    here = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(
        description="Map each query in thesis_query_pool to the top thesis chunk by embedding similarity."
    )
    p.add_argument(
        "--chunks-dir",
        type=Path,
        default=(here / "thesis_chunks").resolve(),
        help="Directory containing thesis chunk markdown files.",
    )
    p.add_argument(
        "--query-pool",
        type=Path,
        default=(here / "thesis_query_pool.json").resolve(),
        help="Query pool JSON path.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=(here / "cli_reader_data" / "query_to_top_thesis_chunk.md").resolve(),
        help="Output markdown path.",
    )
    p.add_argument(
        "--chunks-out",
        type=Path,
        default=(here / "cli_reader_data" / "thesis_chunks_inventory.md").resolve(),
        help="Output markdown path for all split thesis chunks.",
    )
    args = p.parse_args()

    queries = load_query_pool(args.query_pool.expanduser().resolve())
    chunks = load_thesis_chunks(args.chunks_dir.expanduser().resolve())
    rows = map_queries_to_top_chunks(queries, chunks, model_name=EMBED_MODEL)
    write_markdown(rows, args.out.expanduser().resolve())
    write_chunk_inventory_markdown(chunks, args.chunks_out.expanduser().resolve())
    print(f"Wrote {args.out.expanduser().resolve()}")
    print(f"Wrote {args.chunks_out.expanduser().resolve()}")
    print(f"Queries: {len(queries)} | Chunks: {len(chunks)}")


if __name__ == "__main__":
    main()
