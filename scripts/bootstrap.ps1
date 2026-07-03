# ============================================================
# SciOS Bootstrap Script (Windows)
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================="
Write-Host "      SciOS Development Bootstrap"
Write-Host "========================================="
Write-Host ""

# ------------------------------------------------------------
# Check Python
# ------------------------------------------------------------

Write-Host "[1/7] Checking Python..."

try {
    python --version
}
catch {
    Write-Error "Python 3.11+ is required."
    exit 1
}

# ------------------------------------------------------------
# Create Virtual Environment
# ------------------------------------------------------------

Write-Host "[2/7] Preparing virtual environment..."

if (!(Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "Created .venv"
}
else {
    Write-Host ".venv already exists"
}

# ------------------------------------------------------------
# Activate Environment
# ------------------------------------------------------------

Write-Host "[3/7] Activating environment..."

& ".\.venv\Scripts\Activate.ps1"

# ------------------------------------------------------------
# Upgrade Packaging Tools
# ------------------------------------------------------------

Write-Host "[4/7] Updating packaging tools..."

python -m pip install --upgrade `
    pip `
    setuptools `
    wheel

# ------------------------------------------------------------
# Install Project
# ------------------------------------------------------------

Write-Host "[5/7] Installing SciOS..."

pip install -e .

# ------------------------------------------------------------
# Install Development Dependencies
# ------------------------------------------------------------

Write-Host "[6/7] Installing development dependencies..."

if (Test-Path "requirements-dev.txt") {
    pip install -r requirements-dev.txt
}

# ------------------------------------------------------------
# Verify Installation
# ------------------------------------------------------------

Write-Host "[7/7] Running verification..."

python -c "import scios; print('SciOS import: OK')"

Write-Host ""
Write-Host "========================================="
Write-Host " Bootstrap completed successfully."
Write-Host "========================================="