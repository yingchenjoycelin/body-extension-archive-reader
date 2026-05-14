# Body-Extension Archive Reader

Terminal reader for the **Body-Extension Archive**: read thesis "Body-Extension Archive: Recursive Reconfiguration of Subjectivity" by Ying-Chen Joyce Lin through a question-based interface, and optionally open source sections and version run logs.

**Bundled data:** `cli_reader_data/` already contains `query_to_top_thesis_chunk.md` and `thesis_chunks_inventory.md`. You do **not** need to regenerate anything to use the reader.

---

## Quick start (no coding background required)

You only need to **install two small programs once** (Python and Git), **open a window called “Terminal”** on your computer, and **copy-paste a few lines** that this section gives you. You do not need to write any code; you are running a ready-made reader so you can explore the thesis interactively.

**Simplest path:** install Python → install Git → open terminal → paste the **Option A** commands in [step 1](#1-get-this-folder-from-github) → then run the command in [step 3](#3-run-the-reader) → follow the on-screen instructions.

### 0. Open a terminal (command line window)

A **terminal** is a text window where you can type commands and press Enter. You need it for the steps below.

| Your system | How to open it |
|-------------|----------------|
| **Windows** | Press **Win**, type **PowerShell** or **Command Prompt**, press **Enter**. (Or press **Win + R**, type `powershell`, press **Enter**.) |
| **macOS** | Press **Cmd + Space**, type **Terminal**, press **Enter**. |
| **Linux** | Open your app menu and launch **Terminal** (name may vary by distribution). |

Keep this window open; you will paste commands here.

### Install Python (one time)

Python is the runtime that runs the reader script. You only install it once.

1. Go to **[python.org/downloads](https://www.python.org/downloads/)** and download the installer for your system.
2. Run the installer. On **Windows**, check **“Add python.exe to PATH”** (or similar wording) before finishing, then complete the install.
3. **Close and reopen** the terminal, then check that it worked:

```bash
python --version
```

If that fails, try:

```bash
python3 --version
```

You should see a version like **3.10** or higher (3.11+ is fine). If neither command works, repeat the install with PATH enabled or use the “Python Launcher” from the Start menu documentation on [python.org](https://www.python.org/downloads/).

### Install Git (one time, for Option A)

**Git** is a small tool that can **download this project** with one command (`git clone`). If you use **Option A** in step 1 below, install Git once.

1. Go to **[git-scm.com/downloads](https://git-scm.com/downloads)** and install Git for your system. Accept the default options unless you know you need something different.
2. **Close and reopen** the terminal, then check:

```bash
git --version
```

You should see a version number. If you prefer **not** to install Git, use **Option B** in step 1 instead.

---

### 1. Get this folder from GitHub

#### Option A — Git (recommended)

Copy these lines **one block at a time** into your terminal, pressing **Enter** after each line (or paste the whole block if your terminal allows it).

```bash
git clone https://github.com/yingchenjoycelin/body-extension-archive-reader.git
cd body-extension-archive-reader
```

The second command moves you **into** the project folder. Your prompt should show `body-extension-archive-reader` (or similar). That folder must contain `read_body_extension_archive_cli.py`.

#### Option B — ZIP (no Git)

1. On the GitHub repository page, click **Code → Download ZIP**.
2. Unzip the archive (double-click the ZIP, then “Extract” or “Extract all”).
3. In the terminal, **go to** the folder that contains `read_body_extension_archive_cli.py`. GitHub’s ZIP is often named like `body-extension-archive-reader-main`. On Windows, you can type `cd ` (with a space), then **drag the folder** from File Explorer into the terminal and press **Enter** to fill in the path.

---

### 2. Requirements (summary)

- **Python 3.10+** (3.11+ recommended). On macOS or some Linux setups, use `python3` instead of `python` when you run the reader.

The reader uses **only the Python standard library**. You do **not** need `pip install` or an internet connection **just to run** it (after you already have the folder).

### 3. Run the reader

Make sure your terminal’s **current folder** is the project folder (the one with `read_body_extension_archive_cli.py`), then run:

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

### Troubleshooting: GitHub looks updated, but running the reader still feels old

If `body-extension-archive-reader` **already exists** where you run `git clone`, the clone command **does not overwrite it** — you stay on an older copy without noticing.

**Fresh clone — Windows PowerShell:**

```powershell
cd $HOME\Desktop
Remove-Item -Recurse -Force .\body-extension-archive-reader -ErrorAction SilentlyContinue
git clone https://github.com/yingchenjoycelin/body-extension-archive-reader.git
cd body-extension-archive-reader
```

Then run [step 3](#3-run-the-reader). You can confirm you have the newest commit with `git log -1 --oneline` and compare it to the latest commit on GitHub (**main** branch).

**Fresh clone — macOS / Linux** (adjust the folder if your Desktop path differs):

```bash
cd ~/Desktop
rm -rf body-extension-archive-reader
git clone https://github.com/yingchenjoycelin/body-extension-archive-reader.git
cd body-extension-archive-reader
```

`rm -rf` permanently deletes that folder — only run it when you intend to replace the clone with a new download.

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
| 12 | `ENDNOTES.md` | *thesis_source* |
| 13 | `REFERENCES.md` | *thesis_source* |

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
