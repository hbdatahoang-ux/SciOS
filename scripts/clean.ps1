# ============================================================
# SciOS Clean Script (Windows)
# Removes build artifacts, caches and temporary files.
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================="
Write-Host "           SciOS Clean"
Write-Host "========================================="
Write-Host ""

$paths = @(
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".coverage",
    "htmlcov",
    "coverage.xml",
    "dist",
    "build",
    "*.egg-info",
    "**/__pycache__",
    "**/*.pyc",
    "**/*.pyo"
)

foreach ($pattern in $paths)
{
    Get-ChildItem `
        -Path . `
        -Recurse `
        -Force `
        -ErrorAction SilentlyContinue `
        -Filter (Split-Path $pattern -Leaf) |
    Where-Object {
        $_.FullName -like "*$(Split-Path $pattern -Leaf)"
    } |
    ForEach-Object {

        Write-Host "Removing $($_.FullName)"

        Remove-Item `
            $_.FullName `
            -Force `
            -Recurse `
            -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "SciOS workspace cleaned."