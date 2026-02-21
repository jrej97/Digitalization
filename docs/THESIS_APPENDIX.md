# Thesis Appendix: Crime Network App Technical Note

## What the tool does

Crime Network App is a local, workbook-driven analysis tool for building and maintaining investigative network datasets. It loads node and edge tables from an Excel workbook, validates required fields and references, renders an interactive graph, and supports iterative edits through table-based management views.

The app is designed for a thesis workflow where reproducibility and exportability matter. The same dataset can be saved back to Excel (source-of-truth format) and exported for downstream analysis: CSV for tabular/statistical processing and GEXF for graph exploration in tools such as Gephi.

## Data model

The core model has two tables:

- **Nodes** (`nodes` sheet)
  - Required fields: `id`, `label`, `type`, `description`
- **Edges** (`edges` sheet)
  - Required fields: `source`, `target`, `relationship_type`, `description`

Optional provenance-style fields can be included in either table (for example `source_ref`, `date`, `confidence`) and are preserved in save/export flows.

## Validation rules

Validation is applied before graph build/save/export operations:

- Required columns must exist in both sheets.
- Node `id` must be present.
- Node `id` values must be unique.
- Edge `source` and `target` must be present.
- Edge endpoints must reference existing node IDs.

Validation feedback is row-aware so data issues can be corrected in the workbook or management tables.

## UI workflow

1. **Load workbook** (or generate starter data with **Create Sample Workbook**).
2. Review graph in the **Graph** view.
3. Use **Manage Nodes** and **Manage Edges** for CRUD operations.
4. Save edits back to Excel (**Save to Excel**).
5. Export analysis artifacts (**Export CSV**, **Export GEXF**, **Export Summary**).

## Export formats and intended use

- **CSV (`nodes.csv`, `edges.csv`)**: best for reproducible tables, coding sheets, and statistical pipelines.
- **GEXF (`graph.gexf`)**: best for graph layout, community exploration, and visual analytics in Gephi.
- **Export summary (`EXPORT_SUMMARY.md`)**: compact run metadata and counts for appendix evidence.

## Limitations

- Practical interactive scale target is a few hundred nodes/edges.
- Graph semantics are currently undirected (`MultiGraph`), so direction-sensitive interpretation is out of scope.
- Excel is the canonical storage format; manual multi-user merge workflows in Excel are limited and can require careful coordination.

## Citation template

Use this short format in thesis references:

> Crime Network App (v0.1.0). Digitalization project repository. Accessed YYYY-MM-DD.
