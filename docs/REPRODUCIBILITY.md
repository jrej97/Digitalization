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

Expected result: printed artifact paths and final `OK`.

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
