# Archive Checklist (Thesis Submission)

Use this checklist to freeze the exact software state and supporting outputs used in the thesis.

## 1) Tag the exact thesis commit

1. Ensure working tree is clean.
2. Create an annotated tag for the thesis snapshot.
3. Push commit and tag.

```bash
git status
git tag -a thesis-v0.1.0 -m "Thesis snapshot for Digitalization v0.1.0"
git push origin HEAD
git push origin thesis-v0.1.0
```

Tip: Use a stable naming pattern such as `thesis-v<version>` or `thesis-YYYY-MM-DD`.

## 2) Build and collect thesis artifacts bundle

Recommended contents:

- `exports/` (CSV, GEXF, summary markdown)
- `docs/thesis_artifacts/**/screenshots/`
- any chapter-specific Gephi project files (`*.gephi`)
- the exact `requirements-lock.txt`
- this checklist and `docs/REPRODUCIBILITY.md`

Example bundle command:

```bash
mkdir -p archive_bundle
cp -r exports archive_bundle/
cp -r docs/thesis_artifacts archive_bundle/
cp requirements-lock.txt archive_bundle/
cp docs/REPRODUCIBILITY.md docs/ARCHIVE_CHECKLIST.md archive_bundle/
tar -czf thesis-artifacts-v0.1.0.tar.gz archive_bundle
```

## 3) Record provenance metadata

Include in an `ARCHIVE_METADATA.md` file (inside the bundle):

- git commit SHA (`git rev-parse HEAD`)
- thesis tag name
- export generation date/time
- OS + Python version used for export
- any non-default environment variables

## 4) Store archive in durable locations

Suggested publication/backup targets (pick one or more):

- institutional repository
- OSF (Open Science Framework)
- Zenodo

Keep at least one copy in an institution-managed storage location.

## 5) Verify archive reproducibility

On a clean machine or VM:

1. Checkout the thesis tag.
2. Recreate environment from `requirements-lock.txt`.
3. Run tests + quality gate.
4. Compare regenerated exports to archived outputs.

```bash
git checkout thesis-v0.1.0
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
pip install -e .
pytest -q
python scripts/quality_gate.py
```
