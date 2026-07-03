# ============================================================
# SciOS Coverage Report
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================="
Write-Host "        SciOS Coverage Report"
Write-Host "========================================="
Write-Host ""

# ------------------------------------------------------------
# Activate Virtual Environment
# ------------------------------------------------------------

if (!(Test-Path ".\.venv\Scripts\Activate.ps1"))
{
    Write-Error "Virtual environment not found."
    Write-Host "Run scripts/bootstrap.ps1 first."

    exit 1
}

& ".\.venv\Scripts\Activate.ps1"

# ------------------------------------------------------------
# Clean Previous Reports
# ------------------------------------------------------------

Remove-Item `
    -Force `
    -Recurse `
    htmlcov `
    coverage.xml `
    .coverage `
    -ErrorAction SilentlyContinue

# ------------------------------------------------------------
# Run Coverage
# ------------------------------------------------------------

pytest `
    tests `
    --cov=scios `
    --cov-report=term-missing `
    --cov-report=html `
    --cov-report=xml `
    --cov-report=json

$exitCode = $LASTEXITCODE

if ($exitCode -ne 0)
{
    exit $exitCode
}

Write-Host ""
Write-Host "========================================="
Write-Host " Coverage completed."
Write-Host "========================================="
Write-Host ""
Write-Host "HTML : htmlcov/index.html"
Write-Host "XML  : coverage.xml"
Write-Host "JSON : coverage.json"

exit 0