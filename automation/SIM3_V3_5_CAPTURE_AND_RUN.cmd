@echo off
setlocal EnableExtensions
for %%I in ("%~dp0.") do set "SIM3_V3_ROOT=%%~fI"
set "AHK_EXE="

if exist "%ProgramFiles%\AutoHotkey\v2\AutoHotkey64.exe" set "AHK_EXE=%ProgramFiles%\AutoHotkey\v2\AutoHotkey64.exe"
if not defined AHK_EXE if exist "%ProgramFiles%\AutoHotkey\UX\AutoHotkeyUX.exe" set "AHK_EXE=%ProgramFiles%\AutoHotkey\UX\AutoHotkeyUX.exe"
if not defined AHK_EXE if exist "%LocalAppData%\Programs\AutoHotkey\v2\AutoHotkey64.exe" set "AHK_EXE=%LocalAppData%\Programs\AutoHotkey\v2\AutoHotkey64.exe"
if not defined AHK_EXE for /f "delims=" %%A in ('where AutoHotkey64.exe 2^>nul') do if not defined AHK_EXE set "AHK_EXE=%%A"
if not defined AHK_EXE for /f "delims=" %%A in ('where AutoHotkey.exe 2^>nul') do if not defined AHK_EXE set "AHK_EXE=%%A"

if not defined AHK_EXE goto :ahk_not_found

start "" "%AHK_EXE%" "%SIM3_V3_ROOT%\CAPTURE\SIM3_V3_5_WHITE_PANEL_CAPTURE.ahk" "%SIM3_V3_ROOT%"
echo SIM3_V3_5_WHITE_PANEL_CAPTURE_STARTED=TRUE
echo.
echo ChatGPT'deki beyaz panel acik kalsin.
echo Sistem mesajin altindaki Copy ikonunu arar.
echo Otomatik yakalama olmazsa Copy ikonuna bir kez tiklayin.
echo Durdurmak icin Ctrl+Alt+X.
exit /b 0

:ahk_not_found
echo AUTOHOTKEY_V2_NOT_FOUND
pause
exit /b 90
