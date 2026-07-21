$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$server=Join-Path $root 'dashboard_server.pyw'
$url='http://127.0.0.1:8767/dashboard.html'
$profile=Join-Path $root 'EDGE_PROFILE'

function Test-Server {
  try {
    $r=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8767/health' -TimeoutSec 1
    return ($r.StatusCode -eq 200)
  } catch {
    return $false
  }
}

$pythonw=@(
  (Join-Path $env:USERPROFILE 'AppData\Local\Python\pythoncore-3.14-64\pythonw.exe'),
  (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python314\pythonw.exe'),
  (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\pythonw.exe'),
  (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\pythonw.exe')
) | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1

if(-not $pythonw){
  $cmd=Get-Command pythonw.exe -ErrorAction SilentlyContinue
  if($cmd){$pythonw=$cmd.Source}
}

if(-not (Test-Server)){
  if($pythonw){
    Start-Process -FilePath $pythonw -ArgumentList @($server) -WorkingDirectory $root
  }
  else {
    $py=Get-Command py.exe -ErrorAction SilentlyContinue
    if(-not $py){throw 'Python bulunamadi.'}
    Start-Process -FilePath $py.Source -ArgumentList @('-3',$server) -WindowStyle Hidden -WorkingDirectory $root
  }

  $ok=$false
  foreach($i in 1..30){
    Start-Sleep -Milliseconds 200
    if(Test-Server){
      $ok=$true
      break
    }
  }

  if(-not $ok){
    throw 'Dashboard sunucusu baslatilamadi.'
  }
}

$edge=@(
  (Join-Path ${env:ProgramFiles(x86)} 'Microsoft\Edge\Application\msedge.exe'),
  (Join-Path $env:ProgramFiles 'Microsoft\Edge\Application\msedge.exe')
) | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1

if(-not $edge){
  $e=Get-Command msedge.exe -ErrorAction SilentlyContinue
  if($e){$edge=$e.Source}
}

if(-not $edge){
  Start-Process $url
  exit 0
}

$existing=Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" -ErrorAction SilentlyContinue |
  Where-Object { $_.CommandLine -like '*127.0.0.1:8767/dashboard.html*' } |
  Select-Object -First 1

if(-not $existing){
  Start-Process -FilePath $edge -ArgumentList @(
    "--user-data-dir=$profile",
    "--app=$url",
    '--window-size=460,720',
    '--window-position=2,40',
    '--no-first-run',
    '--disable-features=msEdgeSidebarV2'
  )
}

Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Sim3WindowControl {
  [DllImport("user32.dll")]
  public static extern bool SetWindowPos(
    IntPtr hWnd,
    IntPtr hWndInsertAfter,
    int X,
    int Y,
    int cx,
    int cy,
    uint flags
  );

  [DllImport("user32.dll")]
  public static extern bool SetForegroundWindow(IntPtr hWnd);

  [DllImport("user32.dll")]
  public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@

$hwnd=[IntPtr]::Zero

foreach($i in 1..50){
  Start-Sleep -Milliseconds 200

  $windowProcess=Get-Process msedge -ErrorAction SilentlyContinue |
    Where-Object {
      $_.MainWindowTitle -like 'GPT-Codex Otomasyonu*' -and
      $_.MainWindowHandle -ne 0
    } |
    Select-Object -First 1

  if($windowProcess){
    $hwnd=[IntPtr]$windowProcess.MainWindowHandle
    break
  }
}

if($hwnd -eq [IntPtr]::Zero){
  throw 'Dashboard penceresi bulunamadi.'
}

$HWND_TOPMOST=[IntPtr](-1)
$SWP_SHOWWINDOW=0x0040

[void][Sim3WindowControl]::ShowWindow($hwnd,9)
[void][Sim3WindowControl]::SetWindowPos(
  $hwnd,
  $HWND_TOPMOST,
  2,
  40,
  460,
  720,
  $SWP_SHOWWINDOW
)
[void][Sim3WindowControl]::SetForegroundWindow($hwnd)

Start-Sleep -Milliseconds 300

[void][Sim3WindowControl]::SetWindowPos(
  $hwnd,
  $HWND_TOPMOST,
  2,
  40,
  460,
  720,
  $SWP_SHOWWINDOW
)

exit 0
