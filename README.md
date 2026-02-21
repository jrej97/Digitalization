# Crime Network App

NiceGUI-based local app for loading, validating, rendering, editing, saving, and exporting crime-network workbook data.

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

## Run tests

```bash
pytest
```

### Restricted environments (e.g., proxy/air-gapped CI)

If some optional dependencies are unavailable, the test suite will skip only the tests that require them:

- Missing `pandas`: pandas-based test modules are skipped.
- Missing `networkx`: NetworkX-specific tests (graph build / GEXF export) are skipped.

This keeps `pytest` collection resilient instead of failing at import time.
