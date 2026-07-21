param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = ([string]$Root).Trim().Trim([char]34)
$rootPath = [System.IO.Path]::GetFullPath($Root).TrimEnd([char[]]@(92, 47))
$loopDir = Join-Path $rootPath 'LOOP'
$runtimeDir = Join-Path $rootPath 'RUNTIME'
$lockPath = Join-Path $runtimeDir 'SIM3_V3_RUNNER.lock'
$logPath = Join-Path $loopDir 'LAST_PRESTART_CLEANUP.txt'
$obsLogPath = Join-Path $rootPath 'LOGS\SIM3_OBS_RUNTIME_STATUS.txt'

New-Item -ItemType Directory -Path $loopDir -Force | Out-Null
New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path -Parent $obsLogPath) -Force | Out-Null

$log = [System.Collections.Generic.List[string]]::new()
$log.Add('STEP=SIM3_V4_7_PRESTART_CLEANUP_FIXED')
$log.Add("STARTED_AT=$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
$log.Add("ROOT=$rootPath")

function Write-PrestartLog {
    param([string]$Status, [string]$Reason)
    $log.Add("FINAL_STATUS=$Status")
    $log.Add("RESULT_REASON=$Reason")
    $log.Add("FINISHED_AT=$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    $log | Set-Content -LiteralPath $logPath -Encoding UTF8
}

function Get-RootProcesses {
    @(
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object {
                $_.CommandLine -and
                $_.CommandLine.IndexOf(
                    $rootPath,
                    [System.StringComparison]::OrdinalIgnoreCase
                ) -ge 0
            } |
            Select-Object ProcessId, ParentProcessId, Name, CommandLine
    )
}

try {
    $rootProcesses = Get-RootProcesses

    $activeWorkers = @(
        $rootProcesses |
            Where-Object {
                $_.CommandLine -match 'sim3_v3_worker\.py' -or
                (
                    $_.Name -match '^codex(\.exe)?$' -and
                    $_.CommandLine -match '\bexec\b'
                )
            }
    )

    if ($activeWorkers.Count -gt 0) {
        foreach ($process in $activeWorkers) {
            $log.Add("ACTIVE_WORKER=PID_$($process.ProcessId);NAME_$($process.Name)")
        }
        Write-PrestartLog 'BLOCKED' 'ACTIVE_CODEX_OR_WORKER'
        Write-Host 'ACTIVE_CODEX_OR_WORKER_FOUND' -ForegroundColor Red
        $activeWorkers | Format-Table ProcessId, Name, CommandLine -AutoSize
        exit 23
    }

    $staleProcesses = @(
        $rootProcesses |
            Where-Object {
                $_.CommandLine -match 'sim3_v4_loop_controller\.py' -or
                $_.CommandLine -match 'SIM3_V3_5_WHITE_PANEL_CAPTURE\.ahk' -or
                $_.CommandLine -match 'SIM3_V4_1_REPORT_DELIVERY\.ahk' -or
                $_.CommandLine -match 'SIM3_V4_2_RESPONSE_WAIT_IMAGE\.ahk' -or
                $_.CommandLine -match 'SIM3_AUTOMATION_SUPERVISOR\.ps1' -or
                $_.CommandLine -match 'SIM3_V4_SMOKE_DASHBOARD\.ahk' -or
                $_.CommandLine -match 'dashboard_server\.pyw' -or
                $_.CommandLine -match 'DASHBOARD_COMPACT_V4\\EDGE_PROFILE' -or
                $_.CommandLine -match '127\.0\.0\.1:8767/dashboard\.html' -or
                $_.CommandLine -match '127\.0\.0\.1:8765/dashboard\.html'
            }
    )

    foreach ($process in $staleProcesses) {
        try {
            & taskkill.exe /PID ([int]$process.ProcessId) /T /F *> $null
            $log.Add("STALE_PROCESS_CLOSED=PID_$($process.ProcessId);NAME_$($process.Name)")
        }
        catch {
            $log.Add("STALE_PROCESS_CLOSE_WARNING=PID_$($process.ProcessId);$($_.Exception.Message)")
        }
    }

    Start-Sleep -Milliseconds 700

    if (Test-Path -LiteralPath $lockPath -PathType Leaf) {
        $lockPid = 0
        $lockValid = $false
        try {
            $lockData = Get-Content -LiteralPath $lockPath -Raw -Encoding UTF8 | ConvertFrom-Json
            $lockPid = [int]$lockData.pid
            $lockValid = $lockPid -gt 0
        }
        catch {
            $lockValid = $false
        }

        $lockOwner = $null
        if ($lockValid) {
            $lockOwner = Get-CimInstance Win32_Process -Filter "ProcessId=$lockPid" -ErrorAction SilentlyContinue
        }

        $realWorkerOwner = (
            $null -ne $lockOwner -and
            $lockOwner.CommandLine -and
            $lockOwner.CommandLine.IndexOf($rootPath, [System.StringComparison]::OrdinalIgnoreCase) -ge 0 -and
            $lockOwner.CommandLine -match 'sim3_v3_worker\.py'
        )

        if ($realWorkerOwner) {
            $log.Add("RUNNER_LOCK_ACTIVE_OWNER_PID=$lockPid")
            Write-PrestartLog 'BLOCKED' 'RUNNER_LOCK_ACTIVE_WORKER'
            exit 24
        }

        $lockBackup = "$lockPath.stale_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Move-Item -LiteralPath $lockPath -Destination $lockBackup -Force
        $log.Add("STALE_RUNNER_LOCK_MOVED=$lockBackup")
    }

    foreach ($flagName in @('STOP.flag', 'PAUSE.flag', 'STOP_HARD.flag')) {
        $flagPath = Join-Path $rootPath $flagName
        if (Test-Path -LiteralPath $flagPath -PathType Leaf) {
            $flagBackup = Join-Path $loopDir ("$flagName.cleared_$(Get-Date -Format 'yyyyMMdd_HHmmss')")
            Move-Item -LiteralPath $flagPath -Destination $flagBackup -Force
            $log.Add("STALE_FLAG_MOVED=$flagBackup")
        }
    }

    foreach ($tokenRelative in @(
        'CAPTURE\CURRENT_CAPTURE_TOKEN.txt',
        'DELIVERY\CURRENT_DELIVERY_TOKEN.txt',
        'DELIVERY\CURRENT_DELIVERY_REPORT.txt',
        'RESPONSE\CURRENT_RESPONSE_TOKEN.txt'
    )) {
        $tokenPath = Join-Path $rootPath $tokenRelative
        if (Test-Path -LiteralPath $tokenPath -PathType Leaf) {
            try {
                Remove-Item -LiteralPath $tokenPath -Force
                $log.Add("STALE_STAGE_TOKEN_REMOVED=$tokenPath")
            }
            catch {
                $log.Add("STALE_STAGE_TOKEN_WARNING=$tokenPath")
            }
        }
    }

    foreach ($folderName in @('CAPTURE', 'DELIVERY', 'RESPONSE', 'LOOP')) {
        $folder = Join-Path $rootPath $folderName
        if (-not (Test-Path -LiteralPath $folder -PathType Container)) { continue }
        Get-ChildItem -LiteralPath $folder -File -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Name -match '\.tmp(\.|$)|\.sim3tmp\.|\.pending\.|\.write_failed\.|\.lock$' -and
                $_.LastWriteTime -lt (Get-Date).AddMinutes(-5)
            } |
            ForEach-Object {
                try {
                    Remove-Item -LiteralPath $_.FullName -Force
                    $log.Add("STALE_TEMP_REMOVED=$($_.FullName)")
                }
                catch {
                    $log.Add("STALE_TEMP_WARNING=$($_.FullName)")
                }
            }
    }

    $remainingControllers = @(
        Get-RootProcesses |
            Where-Object {
                $_.CommandLine -match 'sim3_v4_loop_controller\.py' -or
                $_.CommandLine -match 'sim3_v3_worker\.py'
            }
    )

    if ($remainingControllers.Count -gt 0) {
        foreach ($process in $remainingControllers) {
            $log.Add("REMAINING_PROCESS=PID_$($process.ProcessId);NAME_$($process.Name)")
        }
        Write-PrestartLog 'FAILED' 'OLD_PROCESS_STILL_PRESENT'
        exit 25
    }

    $dashboardStatePath = Join-Path $rootPath 'DASHBOARD_COMPACT_V4\state.json'
    $dashboardStateTemp = "$dashboardStatePath.tmp.$PID"
    $freshDashboardState = [ordered]@{
        overall_status = 'running'
        active_task_id = 'YENI GOREV'
        active_task_title = 'ChatGPT komutu bekleniyor'
        cycle_stage = 1
        cycle_stage_label = 'GPT görevi/cevabı bekleniyor'
        elapsed_text = '00 dk 00 sn'
        stop_reason = ''
        diagnostic_file = ''
        report_path = ''
        state_label = 'RUNNING'
        needs_attention = $false
        steps = @(
            'GPT görevi/cevabı bekleniyor',
            'Görev yakalanıyor',
            'Codex''e gönderiliyor',
            'Codex çalışıyor',
            'Rapor üretiliyor',
            'Rapor GPT''ye yükleniyor'
        )
    }

    $freshDashboardState | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $dashboardStateTemp -Encoding UTF8
    Move-Item -LiteralPath $dashboardStateTemp -Destination $dashboardStatePath -Force
    $log.Add('DASHBOARD_STATE_RESET=RUNNING_STAGE_1')

    $obs = @(Get-Process obs64 -ErrorAction SilentlyContinue)
    $obsRunning = if ($obs.Count -gt 0) { 'True' } else { 'False' }
    $obsLines = @(
        "CREATED_AT=$(Get-Date -Format o)",
        "OBS_RUNNING=$obsRunning",
        'OBS_DIRECT_ERROR32_CAUSE_PROVEN=NO',
        'OBS_INDIRECT_HOTKEY_FOCUS_GPU_TIMING_RISK=YES',
        'AVOID_HOTKEYS=Ctrl+Alt+X;Ctrl+End;End;PageDown;PageUp;Enter',
        'PREFERRED_CAPTURE=DISPLAY_CAPTURE',
        'KEEP_OBS_MINIMIZED=YES',
        'DISABLE_ALWAYS_ON_TOP_PROJECTOR=YES'
    )
    [System.IO.File]::WriteAllLines($obsLogPath, $obsLines, (New-Object System.Text.UTF8Encoding($false)))
    $log.Add("OBS_RUNNING=$obsRunning")

    Write-PrestartLog 'OK' 'STALE_AUTOMATION_STATE_CLEARED'
    Write-Host 'PRESTART_CLEANUP=OK'
    Write-Host "PRESTART_LOG=$logPath"
    exit 0
}
catch {
    $log.Add("UNHANDLED_ERROR=$($_.Exception.Message)")
    Write-PrestartLog 'FAILED' 'PRESTART_UNHANDLED_ERROR'
    Write-Host "PRESTART_UNHANDLED_ERROR=$($_.Exception.Message)" -ForegroundColor Red
    exit 26
}
