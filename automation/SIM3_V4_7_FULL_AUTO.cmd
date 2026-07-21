@echo off
setlocal EnableExtensions
for %%I in ("%~dp0.") do set "SIM3_ROOT=%%~fI"

set "MAX_LOOPS=30"
if not "%~1"=="" set "MAX_LOOPS=%~1"

set "PRESTART_PS1=%SIM3_ROOT%\LOOP\sim3_v4_prestart_cleanup.ps1"
set "SUPERVISOR_PS1=%SIM3_ROOT%\LOOP\SIM3_AUTOMATION_SUPERVISOR.ps1"

if not exist "%PRESTART_PS1%" (
    echo PRESTART_CLEANUP_NOT_FOUND=%PRESTART_PS1%
    pause
    exit /b 90
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PRESTART_PS1%" -Root "%SIM3_ROOT%"
set "PRESTART_RC=%ERRORLEVEL%"

if not "%PRESTART_RC%"=="0" (
    echo.
    echo SIM3_PRESTART_BLOCKED_RC=%PRESTART_RC%
    echo Ayrinti: %SIM3_ROOT%\LOOP\LAST_PRESTART_CLEANUP.txt
    pause
    exit /b %PRESTART_RC%
)

if exist "%SUPERVISOR_PS1%" (
    start "" /min powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%SUPERVISOR_PS1%" -Root "%SIM3_ROOT%"
)

call "%SIM3_ROOT%\SIM3_V4_7_FULL_AUTO_BACKGROUND.cmd" "%MAX_LOOPS%"
set "AUTOMATION_RC=%ERRORLEVEL%"

if not "%AUTOMATION_RC%"=="0" (
    echo.
    echo SIM3_AUTOMATION_EXIT_CODE=%AUTOMATION_RC%
    echo Ayrinti: %SIM3_ROOT%\LOOP\LAST_LOOP_CONSOLE.txt
    pause
)

exit /b %AUTOMATION_RC%
