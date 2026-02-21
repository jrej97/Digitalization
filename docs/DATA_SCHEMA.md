# Data Schema

## Workbook location
- Default Excel file path: `data/data.xlsx`
- The workbook must contain exactly these required sheet names:
  - `nodes`
  - `edges`

## Required sheets and columns

### `nodes` sheet
Required columns (in canonical order):
1. `id`
2. `label`
3. `type`
4. `description`

### `edges` sheet
Required columns (in canonical order):
1. `source`
2. `target`
3. `relationship_type`
4. `description`

## Optional / extra columns
- Additional columns are allowed in both sheets.
- Extra columns are preserved when loading/saving.
- Exports include extra attributes where the export format supports them (for example CSV/GEXF attributes).
- When writing workbooks, required columns are written first, followed by any extra columns.

## Validation rules (human-friendly)
The app validates data before graph build/save/export:

1. Required columns must exist in each sheet.
2. Node IDs must be present (`nodes.id` cannot be empty).
3. Node IDs must be unique.
4. Edge endpoints must be present (`edges.source`, `edges.target` cannot be empty).
5. Every edge endpoint must reference an existing node ID.

If validation fails, the app reports row-level errors so you can fix the workbook or in-memory edits before continuing.
