$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')

Write-Host '[1/3] Running quality gate'
python scripts/quality_gate.py

Write-Host '[2/3] Preparing dist directory'
New-Item -ItemType Directory -Force -Path dist | Out-Null

Write-Host '[3/3] Building source distribution (if build module is available)'
python -c "import build" *> $null
if ($LASTEXITCODE -eq 0) {
    python -m build --sdist --outdir dist
    Write-Host 'Source distribution written to dist/'
} else {
    Write-Host 'python-build is not installed; skipping sdist build.'
    Write-Host 'To enable packaging, install it and rerun:'
    Write-Host '  python -m pip install build'
}
