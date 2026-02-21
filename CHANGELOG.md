# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Demo Mode and Reset Filters actions in the Graph sidebar.
- Dirty-state guardrails for unsaved CRUD edits and view transitions.
- Release documentation (`docs/RELEASE_CHECKLIST.md`, `docs/SCREENSHOTS.md`).

### Changed
- Graph filter updates now use a short debounce to reduce repeated re-renders.
- Added visible loading feedback during larger graph refreshes.

## [v0.1.0]

### Added
- Initial NiceGUI app with workbook load/validate/render/edit/export flow.
- Provenance metadata support (`source_ref`, `date`, `confidence`) for nodes and edges.
