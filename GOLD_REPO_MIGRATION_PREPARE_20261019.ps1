param(
    [string]$Destination = ""
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Run from the original sim3-automation checkout after GitHub Desktop Pull origin.
$SourceRoot = Split-Path -Parent $PSCommandPath
if (-not $Destination) {
    $Destination = Join-Path (Split-Path -Parent $SourceRoot) "gold-adaptive-model"
}
$Destination = [System.IO.Path]::GetFullPath($Destination)
$Allowlist = Join-Path $SourceRoot "GOLD_REPO_MIGRATION_ALLOWLIST_20261019.txt"
$RequiredBranch = "research-gold-core-timeless-selective-learning-20261016"

if (-not (Test-Path -LiteralPath $Allowlist -PathType Leaf)) {
    throw "Missing migration allowlist. Fetch origin and Pull origin first."
}
if (Test-Path -LiteralPath $Destination) {
    throw "Destination already exists. Nothing changed: $Destination"
}
if ($Destination.StartsWith($SourceRoot + [System.IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Destination cannot be inside the old repository."
}
$Git = Get-Command git -ErrorAction SilentlyContinue
if ($Git) {
    $Current = (& git -C $SourceRoot branch --show-current | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $Current -ne $RequiredBranch) {
        throw "Switch GitHub Desktop to $RequiredBranch before migration."
    }
    & git -C $SourceRoot diff --quiet
    if ($LASTEXITCODE -ne 0) { throw "Tracked source changes are uncommitted. Commit or discard them before copying." }
    & git -C $SourceRoot diff --cached --quiet
    if ($LASTEXITCODE -ne 0) { throw "Staged source changes are uncommitted. Commit them before copying." }
}
$Files = @(Get-Content -LiteralPath $Allowlist -Encoding UTF8 | Where-Object { $_ -and -not $_.StartsWith("#") })
if ($Files.Count -lt 350 -or $Files.Count -gt 500) { throw "Unexpected allowlist length: $($Files.Count)" }
foreach ($File in $Files) {
    if (-not $File.StartsWith("gold_axis_2026/", [StringComparison]::Ordinal) -or $File.Contains("..")) {
        throw "Unsafe allowlist item: $File"
    }
    $Original = Join-Path $SourceRoot ($File -replace "/", "\")
    if (-not (Test-Path -LiteralPath $Original -PathType Leaf)) {
        throw "Source file missing. Pull origin first: $File"
    }
}
Write-Host "Found $($Files.Count) verified listed files; source untouched."
New-Item -ItemType Directory -Path $Destination -Force | Out-Null
foreach ($File in $Files) {
    $Original = Join-Path $SourceRoot ($File -replace "/", "\")
    $Copy = Join-Path $Destination ($File -replace "/", "\")
    New-Item -ItemType Directory -Path (Split-Path -Parent $Copy) -Force | Out-Null
    Copy-Item -LiteralPath $Original -Destination $Copy -ErrorAction Stop
    $OldHash = (Get-FileHash -LiteralPath $Original -Algorithm SHA256).Hash
    $NewHash = (Get-FileHash -LiteralPath $Copy -Algorithm SHA256).Hash
    if ($OldHash -ne $NewHash) { throw "SHA256 copy mismatch: $File" }
}
$Readme = @'
# gold-adaptive-model

Migration staging of GOLD-ADAPTIVE-MODEL-APP-01 from
ataullahturgut/sim3-automation, source branch
research-gold-core-timeless-selective-learning-20261016 (19 October 2026).

Scope: mathematical S1/S2/S3 research modules; OLAY-02, OGREN-03,
ETKI-05; historical 2023-2025 price and news studies; portfolio_guard_v1
research application. Old experimental Git branches were NOT copied.

IMPORTANT: RESEARCH ONLY. Not a live investment advice or bank order system.
Original model and evidence source files were copied byte for byte. Their
gold_axis_2026 relative paths remain intact to preserve application imports,
pinned source checksums, and regression test behavior.

The old repository remains the provenance archive. The migration is not
complete until startup verification AND regression tests pass. Consult:
gold_axis_2026/GOLD_ADAPTIVE_TRADING_MODEL_APPLICATION_PROJECT_MANIFEST.md

Start local Windows app:
gold_axis_2026/apps/portfolio_guard_v1/BASLAT.bat

Application: http://127.0.0.1:8787
'@
Set-Content -LiteralPath (Join-Path $Destination "README.md") -Value $Readme -Encoding UTF8
$Ignore = @'
node_modules/
.env
.env.*
*.pem
*.key
*.p12
*.pfx
__pycache__/
*.pyc
.DS_Store
Thumbs.db
*.log
'@
Set-Content -LiteralPath (Join-Path $Destination ".gitignore") -Value $Ignore -Encoding UTF8
Copy-Item -LiteralPath $Allowlist -Destination (Join-Path $Destination "MIGRATION_SOURCE_ALLOWLIST.txt")
$AppPath = Join-Path $Destination "gold_axis_2026\apps\portfolio_guard_v1"
$Node = Get-Command node -ErrorAction SilentlyContinue
$Npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $Node -or -not $Npm) {
    throw "Files staged but Node.js or npm.cmd not found. Install Node.js 18+ and run verification before publishing. Staged folder: $Destination"
}
Push-Location $AppPath
try {
    Write-Host "Checking pinned sources and app startup..."
    & node server.js --verify
    if ($LASTEXITCODE -ne 0) { throw "App source verification failed. Do not publish yet." }
    Write-Host "Running application regression tests..."
    & npm.cmd test
    if ($LASTEXITCODE -ne 0) { throw "Regression tests failed. Do not publish yet." }
}
finally { Pop-Location }
Write-Host ""
Write-Host "PASS: $($Files.Count) files copied, SHA256 copies checked, app verified, tests passed."
Write-Host "Staged new repository folder: $Destination"
Write-Host "NEXT: GitHub Desktop > File > Add local repository > select folder > Create a repository here > Publish repository > Keep this code private."
