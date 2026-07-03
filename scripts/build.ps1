# ============================================================
# SciOS-NG Package Builder
#
# Builds Python distributions (wheel + sdist)
# and verifies them before release.
#
# Usage:
#     .\scripts\build.ps1
# ============================================================

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# ------------------------------------------------------------
# Banner
# ------------------------------------------------------------

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "             SciOS-NG Package Builder" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

function Step {
    param([string]$Message)

    Write-Host ""
    Write-Host ">> $Message" -ForegroundColor Yellow
}

function Success {
    param([string]$Message)

    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Fail {
    param([string]$Message)

    Write-Error $Message
    exit 1
}

# ------------------------------------------------------------
# Activate Virtual Environment
# ------------------------------------------------------------

Step "Activating virtual environment"

$activate = ".\.venv\Scripts\Activate.ps1"

if (!(Test-Path $activate))
{
    Fail "Virtual environment not found.

Run:

    .\scripts\bootstrap.ps1"
}

& $activate

Success "Virtual environment activated"

# ------------------------------------------------------------
# Verify Project
# ------------------------------------------------------------

Step "Checking project"

if (!(Test-Path "pyproject.toml"))
{
    Fail "pyproject.toml not found."
}

Success "Project configuration found"

# ------------------------------------------------------------
# Verify Python
# ------------------------------------------------------------

Step "Checking Python"

if (!(Get-Command python -ErrorAction SilentlyContinue))
{
    Fail "Python executable not found."
}

python --version

# ------------------------------------------------------------
# Verify Required Packages
# ------------------------------------------------------------

Step "Checking build dependencies"

python -c "import build" 2>$null

if ($LASTEXITCODE -ne 0)
{
    Fail "Python package 'build' is not installed.

Install:

    pip install build"
}

python -c "import twine" 2>$null

if ($LASTEXITCODE -ne 0)
{
    Fail "Python package 'twine' is not installed.

Install:

    pip install twine"
}

Success "Build dependencies verified"

# ------------------------------------------------------------
# Clean Previous Builds
# ------------------------------------------------------------

Step "Cleaning previous build artifacts"

foreach ($dir in @("build", "dist"))
{
    if (Test-Path $dir)
    {
        Remove-Item `
            $dir `
            -Recurse `
            -Force
    }
}

Get-ChildItem `
    -Directory `
    -Filter "*.egg-info" `
    -ErrorAction SilentlyContinue |
ForEach-Object {

    Remove-Item `
        $_.FullName `
        -Recurse `
        -Force

}

Success "Build directory cleaned"

# ------------------------------------------------------------
# Build
# ------------------------------------------------------------

Step "Building package"

python -m build

if ($LASTEXITCODE -ne 0)
{
    Fail "Package build failed."
}

Success "Package built"

# ------------------------------------------------------------
# Verify dist/
# ------------------------------------------------------------

Step "Checking generated artifacts"

if (!(Test-Path "dist"))
{
    Fail "dist directory was not generated."
}

$artifacts = Get-ChildItem dist

if ($artifacts.Count -eq 0)
{
    Fail "No distribution artifacts were produced."
}

Success "Artifacts generated"

# ------------------------------------------------------------
# Verify Package
# ------------------------------------------------------------

Step "Running twine validation"

python -m twine check dist/*

if ($LASTEXITCODE -ne 0)
{
    Fail "Package validation failed."
}

Success "Package verification passed"

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "                BUILD SUCCEEDED" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Generated Artifacts:" -ForegroundColor Cyan
Write-Host ""

Get-ChildItem dist |
Format-Table `
    Name,
    Length,
    LastWriteTime `
    -AutoSize

Write-Host ""

Write-Host "Output Directory:" -ForegroundColor Cyan
Write-Host "    dist\" -ForegroundColor White

Write-Host ""

exit 0