# ============================================================
# SciOS Benchmark Runner
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================="
Write-Host "       SciOS Benchmark Runner"
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
# Verify benchmark directory
# ------------------------------------------------------------

if (!(Test-Path ".\benchmarks"))
{
    Write-Error "benchmarks/ directory not found."
    exit 1
}

# ------------------------------------------------------------
# Prepare output directory
# ------------------------------------------------------------

$outputDir = "benchmark-results"

if (!(Test-Path $outputDir))
{
    New-Item `
        -ItemType Directory `
        -Path $outputDir | Out-Null
}

# ------------------------------------------------------------
# Run benchmark suite
# ------------------------------------------------------------

Write-Host "[1/1] Running benchmarks..."

pytest `
    benchmarks `
    --benchmark-only `
    --benchmark-sort=mean `
    --benchmark-columns=min,max,mean,stddev,rounds `
    --benchmark-json="$outputDir\benchmark.json"

$exitCode = $LASTEXITCODE

if ($exitCode -ne 0)
{
    exit $exitCode
}

Write-Host ""
Write-Host "========================================="
Write-Host " Benchmarks completed successfully."
Write-Host "========================================="
Write-Host ""
Write-Host "Results:"
Write-Host "  benchmark-results\benchmark.json"

exit 0