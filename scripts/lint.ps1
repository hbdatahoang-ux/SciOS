# ============================================================
# SciOS Linter
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================="
Write-Host "            SciOS Linter"
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
# Ruff
# ------------------------------------------------------------

Write-Host "[1/2] Running Ruff..."

ruff check .

if ($LASTEXITCODE -ne 0)
{
    exit $LASTEXITCODE
}

# ------------------------------------------------------------
# MyPy
# ------------------------------------------------------------

Write-Host "[2/2] Running MyPy..."

mypy .

if ($LASTEXITCODE -ne 0)
{
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "========================================="
Write-Host " Lint completed successfully."
Write-Host "========================================="