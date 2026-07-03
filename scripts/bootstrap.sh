#!/usr/bin/env bash

# ============================================================
# SciOS Bootstrap Script (Linux/macOS)
# ============================================================

set -euo pipefail

echo
echo "========================================="
echo "      SciOS Development Bootstrap"
echo "========================================="
echo

# ------------------------------------------------------------
# Check Python
# ------------------------------------------------------------

echo "[1/7] Checking Python..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3.11+ is required."
    exit 1
fi

python3 --version

# ------------------------------------------------------------
# Create Virtual Environment
# ------------------------------------------------------------

echo "[2/7] Preparing virtual environment..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Created .venv"
else
    echo ".venv already exists"
fi

# ------------------------------------------------------------
# Activate Environment
# ------------------------------------------------------------

echo "[3/7] Activating environment..."

# shellcheck disable=SC1091
source .venv/bin/activate

# ------------------------------------------------------------
# Upgrade Packaging Tools
# ------------------------------------------------------------

echo "[4/7] Updating packaging tools..."

python -m pip install --upgrade \
    pip \
    setuptools \
    wheel

# ------------------------------------------------------------
# Install Project
# ------------------------------------------------------------

echo "[5/7] Installing SciOS..."

pip install -e .

# ------------------------------------------------------------
# Install Development Dependencies
# ------------------------------------------------------------

echo "[6/7] Installing development dependencies..."

if [ -f requirements-dev.txt ]; then
    pip install -r requirements-dev.txt
fi

# ------------------------------------------------------------
# Verify Installation
# ------------------------------------------------------------

echo "[7/7] Running verification..."

python -c "import scios; print('SciOS import: OK')"

echo
echo "========================================="
echo " Bootstrap completed successfully."
echo "========================================="