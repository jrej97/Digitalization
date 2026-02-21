# Crime Network App

NiceGUI-based local app for loading, validating, rendering, editing, saving, and exporting crime-network workbook data.

**Current version:** `v0.1.0`

## Requirements

- Python 3.10+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pip install -e .
```

Notes:
- `requirements.txt` includes runtime dependencies (`nicegui`, `pandas`, `openpyxl`, `networkx`) and `pytest` for local testing.
- `pip install -e .` enables package-based imports so `python -m app.main` and `python app/main.py` resolve imports consistently.

## Run the app

Both entry styles are supported:

```bash
python app/main.py
python -m app.main
```

Then open the local URL shown in the terminal (typically `http://127.0.0.1:8080`).

## Documentation

- Data schema: [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- Thesis workflow: [`docs/WORKFLOW.md`](docs/WORKFLOW.md)
- Architecture summary: [`docs/PROJECT_SPEC.md`](docs/PROJECT_SPEC.md)
- Thesis appendix note: [`docs/THESIS_APPENDIX.md`](docs/THESIS_APPENDIX.md)
- Reproducibility guide: [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md)

## Starter workbook

Use the sidebar action **Create Sample Workbook** to generate `data/data.xlsx` with valid starter nodes/edges.

## Configuration (optional)

You can override default paths with environment variables:

- `DHVIZ_DATA_PATH`: default workbook path (default: `data/data.xlsx`)
- `DHVIZ_EXPORT_DIR`: default export directory (default: `exports/`)

Examples:

```bash
export DHVIZ_DATA_PATH=/absolute/path/to/data.xlsx
export DHVIZ_EXPORT_DIR=/absolute/path/to/exports
```

## Run tests

```bash
pytest -q
```

## Optional no-UI smoke check

```bash
python scripts/smoke_check.py
```

## Quality gate

Run the full pre-release check command:

```bash
python scripts/quality_gate.py
```

## Thesis citation template

Use this short format in thesis references:

> Crime Network App (v0.1.0). Digitalization project repository. Accessed YYYY-MM-DD.

### Restricted environments (e.g., proxy/air-gapped CI)

If some optional dependencies are unavailable, the test suite will skip only the tests that require them:

- Missing `pandas`: pandas-based test modules are skipped.
- Missing `networkx`: NetworkX-specific tests (graph build / GEXF export) are skipped.

This keeps `pytest` collection resilient instead of failing at import time.
