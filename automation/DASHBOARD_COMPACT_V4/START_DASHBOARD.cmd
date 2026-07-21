@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0START_DASHBOARD.ps1"
if errorlevel 1 (
  echo Dashboard baslatilamadi.
  pause
  exit /b 1
)
