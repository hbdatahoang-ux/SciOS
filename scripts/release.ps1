# ============================================================
# SciOS Release Pipeline
# ============================================================

[CmdletBinding()]
param(
    [switch]$SkipBenchmark,
    [switch]$SkipDocs,
    [switch]$SkipCoverage
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================="
Write-Host "       SciOS Release Pipeline"
Write-Host "========================================="
Write-Host ""

# ------------------------------------------------------------
# Activate Virtual Environment
# ------------------------------------------------------------

if (!(Test-Path ".\.venv\Scripts\Activate.ps1"))
{
    Write-Error "Virtual environment not found."
    exit 1
}

& ".\.venv\Scripts\Activate.ps1"

# ------------------------------------------------------------
# Verify Git Working Tree
# ------------------------------------------------------------

git diff --quiet

if ($LASTEXITCODE -ne 0)
{
    Write-Error "Working tree contains uncommitted changes."
    exit 1
}

# ------------------------------------------------------------
# Quality Gates
# ------------------------------------------------------------

Write-Host "[1/7] Formatting..."
& ".\scripts\format.ps1"

Write-Host "[2/7] Linting..."
& ".\scripts\lint.ps1"

Write-Host "[3/7] Running Tests..."
& ".\scripts\test.ps1"

if (-not $SkipCoverage)
{
    Write-Host "[4/7] Coverage..."
    & ".\scripts\coverage.ps1"
}

if (-not $SkipDocs)
{
    Write-Host "[5/7] Documentation..."
    & ".\scripts\docs.ps1"
}

if (-not $SkipBenchmark)
{
    Write-Host "[6/7] Benchmarks..."
    & ".\scripts\benchmark.ps1"
}

Write-Host "[7/7] Building Package..."
& ".\scripts\build.ps1"

Write-Host ""
Write-Host "========================================="
Write-Host " Release Candidate Created Successfully"
Write-Host "========================================="

exit 0