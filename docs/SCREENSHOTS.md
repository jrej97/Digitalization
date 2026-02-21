# Screenshot Capture Instructions (Text-Only)

## Required screenshots for release/demo

1. **Graph view**
   - Sidebar visible (filters + Demo Mode + Create Sample Workbook + Reset Filters).
   - Graph canvas visible with rendered nodes/edges.
2. **Manage Nodes view**
   - Table and CRUD buttons visible.
3. **Manage Edges view**
   - Table and CRUD buttons visible.

## Local capture steps

1. Run app locally:
   ```bash
   python -m app.main
   ```
2. Open browser at the local URL printed by NiceGUI.
3. Navigate to each required screen.
4. Capture screenshots using OS tools (Snipping Tool, macOS Screenshot, etc.).

## Storage policy

- Save screenshots outside the git repository, or attach them to release artifacts.
- **Do not commit binary files** (`.png`, `.jpg`, `.gif`, `.pdf`) into this repo.
