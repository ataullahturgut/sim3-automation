param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

$target = Join-Path $PSScriptRoot 'sim3_v4_prestart_cleanup.ps1'
if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
    Write-Error "PRESTART_TARGET_NOT_FOUND=$target"
    exit 90
}
& powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $target -Root $Root
exit $LASTEXITCODE
