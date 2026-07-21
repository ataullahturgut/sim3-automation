param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'SilentlyContinue'

$Root = ([string]$Root).Trim().Trim([char]34)
$Root = [System.IO.Path]::GetFullPath($Root).TrimEnd([char[]]@(92, 47))
$LogDir = Join-Path $Root 'LOGS'
$RuntimeRoot = Join-Path $Root 'RUNTIME'
$PauseFlag = Join-Path $Root 'PAUSE.flag'
$StopFlag = Join-Path $Root 'STOP.flag'
$SupervisorLog = Join-Path $LogDir 'SIM3_AUTOMATION_SUPERVISOR.log'
$StartedAt = Get-Date

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$createdNew = $false
$mutex = New-Object System.Threading.Mutex($true, 'Global\SIM3_AUTOMATION_SUPERVISOR_FIXED_V1', [ref]$createdNew)
if (-not $createdNew) { exit 0 }

function Log([string]$Message) {
    try { Add-Content -LiteralPath $SupervisorLog -Value ("{0} | {1}" -f (Get-Date -Format o), $Message) -Encoding UTF8 } catch {}
}

function Stop-Tree([int]$ProcessId) {
    try { & taskkill.exe /PID $ProcessId /T /F *> $null } catch {}
}

function Get-AllProcesses { @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue) }
function Get-RootProcesses($All) {
    $escaped = [Regex]::Escape($Root)
    @($All | Where-Object { $_.CommandLine -and $_.CommandLine -match $escaped })
}

function Get-LatestRuntime {
    if (-not (Test-Path -LiteralPath $RuntimeRoot -PathType Container)) { return $null }
    Get-ChildItem -LiteralPath $RuntimeRoot -Directory -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
}

function Get-RuntimeProcesses($All, [string]$RuntimePath) {
    $escaped = [Regex]::Escape($RuntimePath)
    @($All | Where-Object { $_.CommandLine -and $_.CommandLine -match $escaped })
}

function Stop-RuntimeTree($All, [string]$Reason) {
    $runtime = Get-LatestRuntime
    if (-not $runtime) { return }
    $runtimeProcesses = @(Get-RuntimeProcesses $All $runtime.FullName)
    if ($runtimeProcesses.Count -eq 0) { return }
    $ids = @($runtimeProcesses.ProcessId)
    $roots = @($runtimeProcesses | Where-Object { $_.ParentProcessId -notin $ids })
    foreach ($process in $roots) {
        Log ("RUNTIME_TREE_KILL reason={0} pid={1} name={2}" -f $Reason, $process.ProcessId, $process.Name)
        Stop-Tree ([int]$process.ProcessId)
    }
}

function Enforce-SingleAhk($RootProcesses) {
    $groups = @{}
    foreach ($process in @($RootProcesses | Where-Object { $_.Name -match '^AutoHotkey.*\.exe$' })) {
        $key = $null
        if ($process.CommandLine -match '(?i)"?([^\"]+\.ahk)"?') { $key = [IO.Path]::GetFileName($Matches[1]).ToLowerInvariant() }
        if (-not $key) { continue }
        if (-not $groups.ContainsKey($key)) { $groups[$key] = New-Object System.Collections.Generic.List[object] }
        $groups[$key].Add($process)
    }
    foreach ($key in $groups.Keys) {
        $items = @($groups[$key] | Sort-Object CreationDate -Descending)
        foreach ($duplicate in ($items | Select-Object -Skip 1)) {
            Log ("DUPLICATE_AHK_KILL_OLDER script={0} pid={1}" -f $key, $duplicate.ProcessId)
            Stop-Tree ([int]$duplicate.ProcessId)
        }
    }
}

function Get-TimeoutSeconds([string]$RuntimePath) {
    foreach ($taskFile in @((Join-Path $RuntimePath 'task_exact_utf8.txt'), (Join-Path $Root 'INBOX\TASK.txt'))) {
        if (-not (Test-Path -LiteralPath $taskFile -PathType Leaf)) { continue }
        try {
            $taskText = [IO.File]::ReadAllText($taskFile)
            $match = [Regex]::Match($taskText, '(?m)^\s*#\s*HARD_TIMEOUT_SECONDS\s*=\s*(\d+)\s*$')
            if ($match.Success) { return [Math]::Max(60, [Math]::Min(1800, [int]$match.Groups[1].Value)) }
        } catch {}
    }
    $metadataPath = Join-Path $RuntimePath 'run_metadata.json'
    if (Test-Path -LiteralPath $metadataPath -PathType Leaf) {
        try {
            $metadata = Get-Content -LiteralPath $metadataPath -Raw | ConvertFrom-Json
            if ($metadata.mode -eq 'CODEX_READ_ONLY') { return 600 }
        } catch {}
    }
    return 900
}

function Check-WorkerTimeout($All) {
    $runtime = Get-LatestRuntime
    if (-not $runtime) { return }
    $final = Join-Path $runtime.FullName 'codex_final_message.txt'
    if (Test-Path -LiteralPath $final -PathType Leaf) {
        try { if ((Get-Item -LiteralPath $final).Length -gt 0) { return } } catch {}
    }
    $runtimeProcesses = @(Get-RuntimeProcesses $All $runtime.FullName)
    $codexAlive = @($runtimeProcesses | Where-Object { $_.Name -in @('codex.exe','codex-code-mode-host.exe') -or $_.CommandLine -match 'codex\.CMD' })
    if ($codexAlive.Count -eq 0) { return }
    $limit = Get-TimeoutSeconds $runtime.FullName
    $elapsed = [int]((Get-Date) - $runtime.CreationTime).TotalSeconds
    if ($elapsed -le $limit) { return }
    Log ("WATCHDOG_TIMEOUT runtime={0} elapsed={1} limit={2}" -f $runtime.Name, $elapsed, $limit)
    [IO.File]::WriteAllText((Join-Path $runtime.FullName 'SIM3_WATCHDOG_TIMEOUT.txt'), "FINAL_STATUS=WATCHDOG_TIMEOUT`r`nELAPSED_SECONDS=$elapsed`r`nHARD_TIMEOUT_SECONDS=$limit`r`n", (New-Object Text.UTF8Encoding($false)))
    [IO.File]::WriteAllText($PauseFlag, "WATCHDOG_TIMEOUT:$($runtime.Name)", (New-Object Text.UTF8Encoding($false)))
    Stop-RuntimeTree $All 'WATCHDOG_TIMEOUT'
}

function Check-DeliverySafety($RootProcesses) {
    $path = Join-Path $Root 'DELIVERY\LAST_DELIVERY_RESULT.txt'
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return }
    try {
        $item = Get-Item -LiteralPath $path
        if ($item.LastWriteTime -lt $StartedAt) { return }
        $content = [IO.File]::ReadAllText($path)
        if ($content -match 'FILE_DIALOG_CLOSED=True' -and $content -match 'ATTACHMENT_READY=False' -and $content -match 'SEND_CLICKED=False') {
            if ($content -match 'FINAL_STATUS=(PAUSED|FAILED)') {
                Log 'DELIVERY_ATTACHMENT_NOT_READY_STOP'
                foreach ($process in @($RootProcesses | Where-Object { $_.Name -match '^AutoHotkey.*\.exe$' -and $_.CommandLine -match 'SIM3_V4_1_REPORT_DELIVERY\.ahk' })) {
                    Stop-Tree ([int]$process.ProcessId)
                }
            }
        }
    } catch {}
}

function Check-Pause($All, $RootProcesses) {
    if (-not (Test-Path -LiteralPath $PauseFlag -PathType Leaf)) { return }
    $reason = ''
    try { $reason = [IO.File]::ReadAllText($PauseFlag) } catch {}
    if ($reason -match 'USER_EMERGENCY_STOP|WATCHDOG_TIMEOUT|AHK_RUNTIME_ERROR|AHK_SOFT_ERROR|DELIVERY_ATTACHMENT_NOT_READY') {
        Stop-RuntimeTree $All $reason
        foreach ($process in @($RootProcesses | Where-Object { $_.Name -match '^AutoHotkey.*\.exe$' })) {
            Stop-Tree ([int]$process.ProcessId)
        }
    }
}

function Handle-Stop($RootProcesses) {
    if (-not (Test-Path -LiteralPath $StopFlag -PathType Leaf)) { return $false }
    Log 'STOP_FLAG_DETECTED'
    $ids = @($RootProcesses.ProcessId)
    foreach ($process in @($RootProcesses | Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -notmatch 'SIM3_AUTOMATION_SUPERVISOR' -and $_.ParentProcessId -notin $ids })) {
        Stop-Tree ([int]$process.ProcessId)
    }
    return $true
}

Log 'SUPERVISOR_START'
try {
    while ($true) {
        $all = Get-AllProcesses
        $rootProcesses = @(Get-RootProcesses $all)
        Enforce-SingleAhk $rootProcesses
        Check-WorkerTimeout $all
        Check-DeliverySafety $rootProcesses
        Check-Pause $all $rootProcesses
        if (Handle-Stop $rootProcesses) { break }
        Start-Sleep -Seconds 2
    }
}
finally {
    Log 'SUPERVISOR_STOP'
    try { $mutex.ReleaseMutex() } catch {}
    $mutex.Dispose()
}
