# Crime Network App (Phase 0 Scaffold)

This repository contains the initial scaffold for a local NiceGUI app that will later ingest Excel workbook data, validate integrity, render a network view, and export graph data.

## Requirements

- Python 3.11+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Run

```bash
python app/main.py
```

Then open the local URL shown in the terminal (typically `http://127.0.0.1:8080`).

## Current scope (Phase 0)

The UI is intentionally a layout skeleton with placeholder content:

- Left sidebar (placeholder controls)
- Center main panel (placeholder area where graph will render)
- Right inspector panel (placeholder node/edge inspection text)

## Not implemented yet (intentional)

- Excel workbook I/O (`data/data.xlsx`)
- Data integrity validation
- Cytoscape.js graph rendering
- CRUD interactions for nodes/edges
- CSV/GEXF exports

## Project structure

```text
app/
data/
exports/
assets/icons/
docs/
tests/
```
