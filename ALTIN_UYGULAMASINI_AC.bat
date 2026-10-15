@echo off
setlocal
call "%~dp0gold_axis_2026\apps\portfolio_guard_v1\BASLAT.bat"
if errorlevel 1 (
  echo Uygulama baslatilamadi. Program klasorunu kontrol edin.
  pause
)
exit /b %errorlevel%
