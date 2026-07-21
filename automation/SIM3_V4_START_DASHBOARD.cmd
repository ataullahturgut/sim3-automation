@echo off
setlocal EnableExtensions
for %%I in ("%~dp0.") do set "SIM3_ROOT=%%~fI"
set "COMPACT_DASHBOARD=%SIM3_ROOT%\START_SIM3_COMPACT_DASHBOARD_V4.cmd"

if not exist "%COMPACT_DASHBOARD%" (
    echo COMPACT_DASHBOARD_NOT_FOUND=%COMPACT_DASHBOARD%
    exit /b 90
)

call "%COMPACT_DASHBOARD%"
exit /b %ERRORLEVEL%
