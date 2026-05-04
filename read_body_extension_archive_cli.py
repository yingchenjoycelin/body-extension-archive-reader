from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class QueryChunkEntry:
    order: int
    query: str
    top_chunk_line: str
    body: str


def _parse_database(text: str) -> list[QueryChunkEntry]:
    header_re = re.compile(r"^##\s+(\d+)\.\s+Query\s*$", re.MULTILINE)
    matches = list(header_re.finditer(text))
    out: list[QueryChunkEntry] = []
    for i, m in enumerate(matches):
        order = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end].strip("\n")
        query = ""
        top_chunk_line = ""
        lines = block.splitlines()
        j = 0
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and lines[j].startswith("**Query:**"):
            query = lines[j][len("**Query:**") :].strip()
            j += 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and lines[j].startswith("**Top chunk:**"):
            top_chunk_line = lines[j].strip()
            j += 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        body = "\n".join(lines[j:]).strip()
        if not query:
            raise ValueError(f"Missing **Query:** in section order {order}")
        out.append(
            QueryChunkEntry(
                order=order,
                query=query,
                top_chunk_line=top_chunk_line,
                body=body,
            )
        )
    out.sort(key=lambda e: e.order)
    return out


def load_database(path: Path) -> list[QueryChunkEntry]:
    text = path.read_text(encoding="utf-8")
    return _parse_database(text)


_INVENTORY_HEADER_RE = re.compile(
    r"^##\s+\d+\.\s+`(chunk_\d+)`\s*$", re.MULTILINE
)
_CHUNK_ID_IN_TOP_LINE = re.compile(r"`(chunk_\d+)`")


def _parse_chunk_inventory_bodies(text: str) -> dict[str, str]:
    matches = list(_INVENTORY_HEADER_RE.finditer(text))
    out: dict[str, str] = {}
    for i, m in enumerate(matches):
        chunk_id = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end].strip("\n")
        lines = block.splitlines()
        j = 0
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and lines[j].startswith("**Source file:**"):
            j += 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        body = "\n".join(lines[j:]).strip()
        body = body.replace("\r\n", "\n").replace("\r", "\n")
        out[chunk_id] = body
    return out


def _chunk_id_from_top_chunk_line(line: str) -> str | None:
    m = _CHUNK_ID_IN_TOP_LINE.search(line)
    return m.group(1) if m else None


def load_reader_entries(query_path: Path, inventory_path: Path) -> list[QueryChunkEntry]:
    """Pair query index (query_to_top_thesis_chunk.md) with bodies from thesis_chunks_inventory.md."""
    q_text = query_path.read_text(encoding="utf-8")
    inv_text = inventory_path.read_text(encoding="utf-8")
    bodies = _parse_chunk_inventory_bodies(inv_text)
    parsed = _parse_database(q_text)
    out: list[QueryChunkEntry] = []
    for e in parsed:
        cid = _chunk_id_from_top_chunk_line(e.top_chunk_line)
        if not cid:
            raise ValueError(
                f"Could not parse chunk id from **Top chunk:** line (section {e.order})."
            )
        body = bodies.get(cid)
        if body is None:
            raise ValueError(
                f"No body for `{cid}` in thesis_chunks_inventory.md "
                f"(section {e.order}). Regenerate inventory or fix pairing."
            )
        out.append(
            QueryChunkEntry(
                order=e.order,
                query=e.query,
                top_chunk_line=e.top_chunk_line,
                body=body,
            )
        )
    return out


def _normalize_for_match(s: str) -> str:
    return " ".join(s.split())


_TOP_CHUNK_SIMILARITY_RE = re.compile(
    r"\s*\(\s*similarity:\s*`[^`]+`\s*\)\s*$", re.IGNORECASE
)


def _format_top_chunk_for_display(top_chunk_line: str) -> str:
    """Strip similarity tail; keep chunk id and source file from **Top chunk:** line."""
    s = top_chunk_line.strip()
    if s.startswith("**Top chunk:**"):
        s = s[len("**Top chunk:**") :].strip()
    s = _TOP_CHUNK_SIMILARITY_RE.sub("", s).strip()
    return f"Top chunk: {s}" if s else "Top chunk:"


DISPLAY_RULE = "=" * 85

_COMPLETION_HEART = """\
  ++     ++
 ++++   ++++
++++++ ++++++
 +++++++++++
  +++++++++
   +++++++
    +++++
     +++
      +"""


def resolve_choice(
    raw: str, entries: list[QueryChunkEntry]
) -> QueryChunkEntry | None:
    s = raw.strip()
    if not s:
        return None
    if s.isdigit():
        n = int(s)
        for e in entries:
            if e.order == n:
                return e
        # allow stripping leading zeros conceptually e.g. "01", "02", etc.
        return None
    norm = _normalize_for_match(s)
    for e in entries:
        if _normalize_for_match(e.query) == norm:
            return e
        if e.query.strip() == s.strip():
            return e
    return None


DEF_HEADER = """<3 <3 <3 <3 <3 <3 <3 <3 <3 <3
Body-Extension Archive reader
<3 <3 <3 <3 <3 <3 <3 <3 <3 <3"""

DEF_INSTRUCTION = """\
Questions used in this research are listed below. Three are from the thesis research questions; the rest emerged through interaction with the system. Each question maps to one thesis chunk (pairing in .\\cli_reader_data\\query_to_top_thesis_chunk.md; full chunk text is read from .\\cli_reader_data\\thesis_chunks_inventory.md).

To read a thesis chunk, enter one of:
- a number from the list (1–{n}), or
- the full question text

You may choose any order. Continue entering questions until you exit.

Commands:
"s" or "source" to view other thesis text in .\\thesis_source
"q", "quit", or "exit" to exit"""


# (folder header line, subdir relative to body_extension_archive_reader, (letter, filename))
OPTIONAL_CONTEXT_SECTIONS: tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...] = (
    (
        ".\\thesis_source\\",
        "thesis_source",
        (
            ("A", "01_EMBODIED_ITERATION_AS_METHOD.md"),
            ("B", "02_THE_EMERGENCE_OF_THE_CENTRAL_QUESTION.md"),
            ("C", "06_BODY_EXTENSION_ARCHIVE_INTRO.md"),
            ("D", "12_Endnotes.md"),
            ("E", "13_References.md"),
        ),
    ),
    (
        ".\\version_run_logs\\",
        "version_run_logs",
        (
            ("F", "v1.0.0_run_output_251220.md"),
            ("G", "v2.0.0_run_output_260120.md"),
            ("H", "v3.0.0_run_output_260422.md"),
        ),
    ),
)


def _optional_context_paths(thesis_system_root: Path) -> dict[str, Path]:
    m: dict[str, Path] = {}
    for _, subdir, items in OPTIONAL_CONTEXT_SECTIONS:
        for letter, name in items:
            m[letter.upper()] = thesis_system_root / subdir / name
    return m


def _print_optional_context_menu() -> None:
    print()
    print("Source — Body-Extension Archive")
    print("-" * 72)
    for header, _, items in OPTIONAL_CONTEXT_SECTIONS:
        print(header)
        for letter, name in items:
            print(f"\t[{letter}] {name}")
        print()
    print("-" * 72)


def _wait_any_key() -> None:
    print("Press any key to return to the question session...")
    sys.stdout.flush()
    if sys.platform == "win32":
        import msvcrt

        msvcrt.getch()
    else:
        try:
            import termios
            import tty

            fd = sys.stdin.fileno()
            if not sys.stdin.isatty():
                input("Press Enter to continue...")
            else:
                old = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except (ImportError, OSError, AttributeError):
            input("Press Enter to continue...")
    print()


def _open_optional_context_file(path: Path) -> None:
    sep = DISPLAY_RULE
    print()
    if not path.is_file():
        print(f"File not found: {path.name}")
        print(sep)
        return
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Could not read file: {e}")
        print(sep)
        return
    print(sep)
    print(path.name)
    print(sep)
    print(text.rstrip("\n"))
    print(sep)


def _run_optional_context_session(thesis_system_root: Path) -> None:
    letter_map = _optional_context_paths(thesis_system_root)
    _print_optional_context_menu()
    while True:
        try:
            line = input(
                "*** Type A—H to read a file, Enter to return >>> "
            ).strip()
        except EOFError:
            print()
            return
        if not line:
            print()
            return
        if len(line) != 1:
            print("Enter a single letter A through H, or Enter alone to return.\n")
            continue
        key = line.upper()
        path = letter_map.get(key)
        if path is None:
            print("Use only letters A through H, or Enter to return.\n")
            continue
        _open_optional_context_file(path)
        _wait_any_key()
        return


def _print_after_query_list(
    *,
    footer: str = "short",
    show_completion_heart: bool = False,
    print_press_s: bool = True,
) -> None:
    if print_press_s:
        print("Press 's' to view other thesis text in .\\thesis_source")
    if show_completion_heart:
        print()
        print(_COMPLETION_HEART)
        print()
    if footer == "long":
        print("---------------------<3")
    else:
        print("---------<3")
    print()


def run_interactive(entries: list[QueryChunkEntry], thesis_system_root: Path) -> None:
    n = len(entries)
    seen: set[int] = set()

    print()
    print(DEF_HEADER)
    print()
    print(DEF_INSTRUCTION.format(n=n))
    print()
    print("Questions")
    print("---------<3")
    for e in entries:
        print(f"  {e.order:02d}. {e.query}")
    _print_after_query_list(footer="short")

    completion_banner_shown = False
    while True:
        remaining = [e for e in entries if e.order not in seen]
        all_complete = not remaining
        if all_complete:
            if not completion_banner_shown:
                print("You have finished every questions ;)")
                print("Press 's' to view other thesis text in .\\thesis_source")
                print("Press 'q' to exit")
                _print_after_query_list(
                    footer="long",
                    show_completion_heart=True,
                    print_press_s=False,
                )
                completion_banner_shown = True
        elif seen:
            # After the first chunk, list only what is left (initial "Questions" already listed all once).
            print("Still have questions")
            print("---------------------<3")
            for e in remaining:
                print(f"  {e.order:02d}. {e.query}")
            _print_after_query_list(footer="long")

        try:
            if all_complete:
                line = input("*** Enter (s / source, q / quit / exit) >>> ").strip()
            else:
                line = input("*** Enter (number or question, s / source) >>> ").strip()
        except EOFError:
            print()
            if all_complete:
                print("Goodbye <3")
            else:
                print("Goodbye :'(")
            break

        lower = line.lower()
        if lower in ("q", "quit", "exit"):
            if all_complete:
                print("Goodbye <3")
            else:
                print("Goodbye :'(")
            break

        if not line:
            if all_complete:
                print(
                    "Enter 's' / 'source' for .\\thesis_source, "
                    "or 'q' / 'quit' / 'exit'.\n"
                )
            else:
                print(
                    "Enter a number (1–%d), the full question text, "
                    "'s' / 'source' for .\\thesis_source, or 'q' to exit.\n"
                    % (max(e.order for e in entries),)
                )
            continue

        if lower == "s" or lower == "source":
            _run_optional_context_session(thesis_system_root)
            continue

        entry = resolve_choice(line, entries)
        if entry is None:
            if all_complete:
                print(
                    "No match. Enter 's' / 'source' then A–H for optional files, "
                    "or 'q' / 'quit' / 'exit'.\n"
                )
            else:
                print(
                    "No match. Use a listed number (1–%d), the exact question text, "
                    "or 's' / 'source' then A–H for optional files.\n"
                    % (max(e.order for e in entries),)
                )
            continue

        seen.add(entry.order)
        sep = DISPLAY_RULE
        print()
        print(sep)
        print(f"Question ({entry.order:02d}): {entry.query}")
        if entry.top_chunk_line:
            print(_format_top_chunk_for_display(entry.top_chunk_line))
        print(sep)
        print(entry.body.replace("\r\n", "\n").replace("\r", "\n"))
        print(sep)
        print()


def main() -> None:
    here = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(
        prog="read_body_extension_archive_cli.py",
        description="Body-Extension Archive terminal reader: query list and top-chunk "
        "metadata from cli_reader_data/query_to_top_thesis_chunk.md; chunk prose from "
        "cli_reader_data/thesis_chunks_inventory.md.",
    )
    p.add_argument(
        "--database",
        type=Path,
        default=here / "cli_reader_data" / "query_to_top_thesis_chunk.md",
        help="Path to query_to_top_thesis_chunk.md (queries + top chunk ids).",
    )
    p.add_argument(
        "--inventory",
        type=Path,
        default=here / "cli_reader_data" / "thesis_chunks_inventory.md",
        help="Path to thesis_chunks_inventory.md (full chunk bodies).",
    )
    args = p.parse_args()
    db = args.database.expanduser().resolve()
    inv = args.inventory.expanduser().resolve()
    if not db.is_file():
        print(f"Database file not found: {db}", file=sys.stderr)
        sys.exit(1)
    if not inv.is_file():
        print(f"Chunk inventory not found: {inv}", file=sys.stderr)
        sys.exit(1)
    try:
        entries = load_reader_entries(db, inv)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    if not entries:
        print("No entries parsed from database.", file=sys.stderr)
        sys.exit(1)
    run_interactive(entries, here)


if __name__ == "__main__":
    main()
