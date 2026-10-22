param(
    [string]$OutputDirectory = ".\\dist-community"
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$root = (git rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0) { throw "Not inside a Git repository." }
Set-Location $root
$branch = (git branch --show-current).Trim()
if ($branch -ne "feature/community-csv-mvp") {
    throw "Switch to feature/community-csv-mvp before packaging."
}
$dirty = git status --porcelain
if ($dirty) { throw "Working tree is not clean; packaging refused." }
$sha = (git rev-parse HEAD).Trim()
$testPaths = @(
    "tests/community",
    "tests/api/test_csv_analyze.py",
    "tests/application/test_csv_end_to_end.py",
    "tests/runtime/tools/test_csv_analysis.py"
)
python -m pytest @testPaths -q
if ($LASTEXITCODE -ne 0) { throw "Regression tests failed; no package created." }
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$target = (Resolve-Path $OutputDirectory).Path
$zip = Join-Path $target "SciOS-Community-v0.1.1-source.zip"
git archive --format=zip --prefix="SciOS-Community-v0.1.1/" --output="$zip" HEAD
if ($LASTEXITCODE -ne 0) { throw "git archive failed." }
$hash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
@(
    "Package: SciOS-Community-v0.1.1-source.zip"
    "Git commit: $sha"
    "Branch: $branch"
    "SHA-256: $hash"
    "Scope: repository source archive, not a signed executable or validated public release"
) | Set-Content -LiteralPath (Join-Path $target "SHA256.txt") -Encoding UTF8
Write-Host "PACKAGE: $zip"
Write-Host "COMMIT: $sha"
Write-Host "SHA256: $hash"
