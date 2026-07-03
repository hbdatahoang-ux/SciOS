# ============================================================
# SciOS Test Runner
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================="
Write-Host "          SciOS Test Runner"
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
# Verify tests directory
# ------------------------------------------------------------

if (!(Test-Path ".\tests"))
{
    Write-Error "tests/ directory not found."

    exit 1
}

# ------------------------------------------------------------
# Execute test suite
# ------------------------------------------------------------

Write-Host "[1/1] Running pytest..."

pytest tests -v

$exitCode = $LASTEXITCODE

Write-Host ""

if ($exitCode -eq 0)
{
    Write-Host "========================================="
    Write-Host " All tests passed."
    Write-Host "========================================="
}
else
{
    Write-Host "========================================="
    Write-Host " Test suite failed."
    Write-Host "========================================="
}

exit $exitCode