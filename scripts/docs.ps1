# ============================================================
# SciOS Documentation Generator
# Builds project documentation using MkDocs.
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================="
Write-Host "    SciOS Documentation Generator"
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
# Verify configuration
# ------------------------------------------------------------

if (!(Test-Path ".\mkdocs.yml"))
{
    Write-Error "mkdocs.yml not found."
    exit 1
}

# ------------------------------------------------------------
# Clean previous build
# ------------------------------------------------------------

if (Test-Path ".\site")
{
    Remove-Item -Recurse -Force ".\site"
}

# ------------------------------------------------------------
# Build documentation
# ------------------------------------------------------------

Write-Host "[1/1] Building documentation..."

mkdocs build --strict

$exitCode = $LASTEXITCODE

if ($exitCode -ne 0)
{
    exit $exitCode
}

Write-Host ""
Write-Host "========================================="
Write-Host " Documentation generated successfully."
Write-Host " Output: site/"
Write-Host "========================================="

exit 0