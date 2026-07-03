# ============================================================
# SciOS Formatter
# ============================================================

$ErrorActionPreference = "Stop"

if (!(Test-Path ".\.venv\Scripts\Activate.ps1"))
{
    Write-Error "Virtual environment not found."
    exit 1
}

& ".\.venv\Scripts\Activate.ps1"

Write-Host "Formatting SciOS..."

ruff format .

ruff check . --fix

Write-Host "Formatting complete."