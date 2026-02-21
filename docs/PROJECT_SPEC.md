# Project Spec (Current Architecture)

This document summarizes the current implementation modules for the crime-network workflow.

## Core data flow
1. Load workbook (`io_excel.load_workbook`)
2. Validate tabular data (`validate.validate_data`)
3. Build graph representations:
   - Cytoscape elements (`graph_build.build_cytoscape_elements`)
   - NetworkX graph (`graph_build.build_networkx_graph`)
4. Render graph (`graph_render.render_cytoscape`)
5. Edit in memory (CRUD helpers)
6. Save/export (`io_excel.save_workbook`, `export.export_csv`, `export.export_gexf`)

## Module summary

### `app/io_excel.py`
- Handles Excel I/O for `data/data.xlsx`.
- Enforces required sheets/columns at load.
- Saves with safe-write semantics and required-columns-first ordering.

### `app/validate.py`
- Central validation engine for nodes and edges DataFrames.
- Produces structured issue dictionaries for UI-friendly error reporting.

### `app/graph_build.py`
- Converts tabular input into:
  - Cytoscape-compatible element dictionaries
  - NetworkX graph object

### `app/graph_render.py`
- NiceGUI/Cytoscape rendering integration.
- Handles selection callback wiring used by the inspector.

### `app/export.py`
- Exports current validated state to CSV and GEXF artifacts.

### CRUD helper modules
- `app/crud_nodes.py`: node-specific checks (e.g., uniqueness, delete constraints)
- `app/crud_edges.py`: edge add/edit guardrails

### `app/main.py`
- UI composition and workflow orchestration.
- Coordinates load/validate/build/render/save/export actions.

### `app/sample_data.py`
- Generates a starter workbook for onboarding (`Create Sample Workbook`).
- Produces valid `nodes`/`edges` data including optional example columns.

## Intended usage
- Keep workbook schema stable and documented.
- Use UI edits for iterative curation.
- Persist to Excel as source of truth and export for downstream tools (e.g., Gephi).
