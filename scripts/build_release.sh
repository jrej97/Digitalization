#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/3] Running quality gate"
python scripts/quality_gate.py

echo "[2/3] Preparing dist directory"
mkdir -p dist

echo "[3/3] Building source distribution (if build module is available)"
if python -c "import build" >/dev/null 2>&1; then
  python -m build --sdist --outdir dist
  echo "Source distribution written to dist/"
else
  echo "python-build is not installed; skipping sdist build."
  echo "To enable packaging, install it and rerun:"
  echo "  python -m pip install build"
fi
