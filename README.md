# Body-Extension Archive Reader

Terminal reader for the **Body-Extension Archive**: read the thesis through a question-based interface, and optionally open source sections and version run logs.

**Bundled data:** `cli_reader_data/` already contains `query_to_top_thesis_chunk.md` and `thesis_chunks_inventory.md`. You do **not** need to regenerate anything to use the reader.

---

## Quick start (download → run)

### 1. Get this folder from GitHub

**Option A — ZIP (no Git)**

1. On the repository page, use **Code → Download ZIP**.
2. Unzip the archive.
3. Open a terminal and go into the unzipped folder that contains `read_body_extension_archive_cli.py` (GitHub’s ZIP is usually named like `body-extension-archive-reader-main`).

**Option B — Git**

```bash
git clone https://github.com/yingchenjoycelin/body-extension-archive-reader.git
cd body-extension-archive-reader
```

The clone directory name matches the repository name above.

### 2. Requirements

- **Python 3.10+** (3.11+ recommended; use `python3` on macOS/Linux if that is your default).

The reader script uses **only the Python standard library**. You do **not** need `pip install` or an internet connection **just to run** it.

### 3. Run the reader

```bash
python read_body_extension_archive_cli.py
```

On some systems:

```bash
python3 read_body_extension_archive_cli.py
```

Optional (only if you use custom paths):

```bash
python read_body_extension_archive_cli.py --database path/to/query_to_top_thesis_chunk.md --inventory path/to/thesis_chunks_inventory.md
```

Follow the on-screen prompts: numbers or full question text, **`s`** / **`source`** for extra thesis files, **`q`** / **`quit`** / **`exit`** to leave.

---

## What is in this folder

| Path | Role |
|------|------|
| `read_body_extension_archive_cli.py` | Interactive reader (uses bundled `cli_reader_data/`). |
| `cli_reader_data/` | **Pre-built** query → chunk index + full chunk inventory (read by the CLI). |
| `thesis_chunks/` | Chapter sources (how the inventory was produced; not required to run the reader). |
| `thesis_source/` | Method, archive intro, endnotes, references (opened from the CLI with **s**). |
| `version_run_logs/` | Run captures (optional menu in the CLI). |
| `thesis_query_pool.json` | Source list of questions (used when authors rebuild data). |
| `map_queries_to_top_thesis_chunks.py` | **Maintainer tool** — rebuilds `cli_reader_data/` with embeddings; not part of the normal reader flow. |

---

## Thesis structure

This order is **aligned with the research arc of the Body-Extension Archive**: how the question was framed, how the argument moves through the body and mediation, how the archive is introduced, how each system iteration was reflected on, and how the line of thought closes.

**Segmented thesis content** is organized under `thesis_chunks/`. **Front matter, the archive introduction, endnotes, and references** live under `thesis_source/`. **Raw outputs** for each system version are in `version_run_logs/`.

| # | File | Role |
|---|------|------|
| 01 | `01_EMBODIED_ITERATION_AS_METHOD.md` | *thesis_source* |
| 02 | `02_THE_EMERGENCE_OF_THE_CENTRAL_QUESTION.md` | *thesis_source* — How the guiding question takes shape. |
| 03 | `03_THE_VULNERABLE_BODY_UNDER_TECHNOLOGICAL_CONDITIONS.md` | *thesis_chunks* |
| 04 | `04_FROM_BODILY_INDETERMINACY_TO_THE_STRUCTURE_OF_MEDIATED_EXPERIENCE.md` | *thesis_chunks* |
| 05 | `05_TECHNOLOGICAL_MEDIATION_AND_THE_PRESUPPOSED_SUBJECT.md` | *thesis_chunks* |
| 06 | `06_BODY_EXTENSION_ARCHIVE_INTRO.md` | *thesis_source* — Introduction to the Body-Extension Archive as a construct and practice. |
| 07 | `07_Iteration_log_after_v1.0.0_On_no_longer_being_a_complete_form_251220.md` | *thesis_chunks* — Reflect on `v1.0.0_run_output_251220.md` in `version_run_logs/`. |
| 08 | `08_Iteration_log_after_v2.0.0_On_the_failure_of_subjectless_system_260120.md` | *thesis_chunks* — Reflect on `v2.0.0_run_output_260120.md`. |
| 09 | `09_Iteration_log_before_v3.0.0_On_the_emergence_of_the_observed_subject_260212.md` | *thesis_chunks* |
| 10 | `10_Iteration_log_during_v3.0.0_On_not_existing_before_the_relation_260330.md` | *thesis_chunks* — Alongside `v3.0.0_run_output_260422.md`. |
| 11 | `11_CONCLUSION.md` | *thesis_chunks* |
| 12 | `12_Endnotes.md` | *thesis_source* |
| 13 | `13_References.md` | *thesis_source* |

The bundled **query → chunk** mapping was built from `thesis_chunks/`; use **s / source** in the CLI for `thesis_source/` and `version_run_logs/` from the optional menu.

---

## For maintainers (rebuild `cli_reader_data`)

If you change `thesis_chunks/`, `<split>` markers, or `thesis_query_pool.json`, install dependencies and run:

```bash
pip install -r requirements.txt
python map_queries_to_top_thesis_chunks.py
```

That step downloads embedding weights on first use and overwrites the files in `cli_reader_data/`. **End users who only read the archive can ignore this section.**

---

## Prose and rights

Thesis text and iteration logs in this repository constitute the author's scholarly and artistic work. The MIT License applies to the code and repository structure only, and does not extend to the written content.

The written content is not covered by the MIT License. If you wish to reuse or share any part of the text, please contact the author.

## License

See `LICENSE` (MIT) for the code in this directory.
