# Release Checklist

## 1) Validate code quality

```bash
pytest -q
```

If tests pass, proceed.

## 2) Launch app smoke check

```bash
python -m app.main
```

Verify:
- Graph view loads.
- Demo Mode loads sample data.
- Manage Nodes / Manage Edges CRUD still works.
- Save to Excel succeeds.

## 3) Generate/verify sample data and outputs

- Use **Demo Mode** to populate `data/data.xlsx` if needed.
- Use sidebar export actions:
  - Export CSV
  - Export GEXF
  - Export Summary
- Confirm files are generated in expected output locations.

## 4) Documentation and release notes

- Update `CHANGELOG.md`:
  - Move `Unreleased` entries into the new tagged version.
- Confirm `README.md` version and citation text are up to date.

## 5) Git hygiene before tagging

```bash
git status
```

Confirm no binary screenshots/assets are staged.

## 6) Create release tag

Example:

```bash
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

## Known limitations

- Target interactive performance is optimized for graphs up to a few hundred nodes/edges.
- Very large graphs may still require additional pagination/clustering work in future phases.
