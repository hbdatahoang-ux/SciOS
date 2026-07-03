# ============================================================
# SciOS Application Runner
# ============================================================

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================="
Write-Host "           SciOS Runner"
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
# Verify project
# ------------------------------------------------------------

if (!(Test-Path ".\pyproject.toml"))
{
    Write-Error "pyproject.toml not found."
    exit 1
}

# ------------------------------------------------------------
# Run SciOS
# ------------------------------------------------------------

python -m scios.apps.cli.main @Arguments

exit $LASTEXITCODE