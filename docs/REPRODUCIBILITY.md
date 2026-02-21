# Reproducibility Statement

## Environment requirements

- Python **3.10+**
- Dependencies from `requirements.txt` (notably `nicegui`, `pandas`, `openpyxl`, `networkx`, `pytest`)

Recommended setup:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Frozen environment (thesis path)

Use `requirements-lock.txt` as the single pinned dependency snapshot for archival reproduction.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-lock.txt
pip install -e .
```

If `requirements-lock.txt` still contains placeholder instructions, regenerate it on a connected machine:

```bash
pip install -r requirements.txt
pip freeze > requirements-lock.txt
```

Optional path overrides:

- `DHVIZ_DATA_PATH` (default: `data/data.xlsx`)
- `DHVIZ_EXPORT_DIR` (default: `exports/`)

## Reproduce a graph from scratch (Demo/Sample flow)

1. Start the app:
   ```bash
   python -m app.main
   ```
2. Open the local URL shown in terminal (default `http://127.0.0.1:8080`).
3. Click **Create Sample Workbook** in the sidebar.
4. Confirm graph nodes/edges are rendered.
5. Optional: inspect and edit records in **Manage Nodes** / **Manage Edges**.

## Regenerate exports and confirm outputs

From the UI sidebar, run:

- **Export CSV** → produces `exports/nodes.csv` and `exports/edges.csv`
- **Export GEXF** → produces `exports/graph.gexf`
- **Export Summary** → produces `exports/EXPORT_SUMMARY.md`

Verify outputs exist:

```bash
test -f exports/nodes.csv && test -f exports/edges.csv && test -f exports/graph.gexf && test -f exports/EXPORT_SUMMARY.md
```

## Verify validation is passing

- In UI: ensure no validation errors are shown before save/export actions.
- In tests:

```bash
pytest -q
```

For a no-UI smoke flow:

```bash
python scripts/smoke_check.py
```

For the full pre-release quality gate:

```bash
python scripts/quality_gate.py
```

Expected result: printed artifact paths and final `OK`.

## Convenience commands

A `Makefile` is provided for common flows:

```bash
make venv
make install
make run
make test
make quality
```

Windows PowerShell alternative (if `make` is unavailable):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest -q
python scripts/quality_gate.py
```

## Suggested thesis artifact structure

Use a chapter-scoped layout so each figure/table can be traced to source exports:

```text
docs/thesis_artifacts/
  chapter_01/
    exports/
    gephi/
    screenshots/
  chapter_02/
    exports/
    gephi/
    screenshots/
```

Keep immutable snapshots per chapter milestone (for example by date or version tag).
