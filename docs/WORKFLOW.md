# Thesis Workflow

This workflow is designed for quick onboarding and repeatable thesis analysis.

## 1) Create or load workbook
- On app start, the app tries to load `data/data.xlsx`.
- If missing, use **Create Sample Workbook** in the sidebar to generate a starter dataset.
- You can also provide your own workbook with `nodes` and `edges` sheets.

## 2) Validate data
- Validation runs before graph build, save, and export.
- Typical errors mean:
  - Missing required column: workbook structure issue.
  - Duplicate/missing node ID: node identity problem.
  - Unknown edge endpoint: edge references node IDs not present in `nodes`.
- Fix errors in UI or workbook, then re-run the action.

## 3) Visualize + inspect
- Open Graph view to see the network.
- Click nodes/edges to inspect details in the right-side inspector.
- Use this stage to sanity-check structure and attributes.

## 4) Manage Nodes/Edges in UI
- Use **Manage Nodes** and **Manage Edges** for in-memory editing.
- Changes are immediate in app state and reflected in the graph once valid.
- Nothing is persisted until you save.

### Provenance best practices (optional but recommended)
- Fill `source_ref` with short, stable references (example: `Author 2020, p. 12`).
- Keep `date` in a single format (`YYYY-MM-DD`) across both nodes and edges.
- Use one confidence policy for the full workbook (`0..1`, where `1.0` is strongest confidence).
- Define a short rubric for confidence (for example: `0.2 weak`, `0.5 moderate`, `0.8 strong`) and apply it consistently.

## 5) Save to Excel (source of truth)
- Click **Save to Excel** to persist the current in-memory state back to `data/data.xlsx`.
- Treat this workbook as your canonical source data.

## 6) Export CSV/GEXF
- Use **Export CSV** for tabular analysis and reporting pipelines.
- Use **Export GEXF** for graph tooling interoperability.
- Optional provenance fields (`source_ref`, `date`, `confidence`) are included in exports when present.

## 7) Open in Gephi
- Import the exported `.gexf` file into Gephi.
- Apply a layout, size/color by relevant attributes, and inspect communities/centrality as needed.
- Keep Gephi styling decisions separate from source workbook edits.

## Recommended practice
- Version exported artifacts (for example `exports/run_2026-02-21/`).
- Keep regular backups of `data/data.xlsx`.
- Commit workbook schema/documentation changes together so collaborators can reproduce your steps.
