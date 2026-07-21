@echo off
setlocal EnableExtensions
for %%I in ("%~dp0.") do set "SIM3_ROOT=%%~fI"

set "MAX_LOOPS=30"
if not "%~1"=="" set "MAX_LOOPS=%~1"

if not exist "%SIM3_ROOT%\LOOP" mkdir "%SIM3_ROOT%\LOOP"
set "CONSOLE_LOG=%SIM3_ROOT%\LOOP\LAST_LOOP_CONSOLE.txt"

echo STEP=SIM3_V4_7_FULL_AUTO_BACKGROUND>"%CONSOLE_LOG%"
echo STARTED_AT=%DATE% %TIME%>>"%CONSOLE_LOG%"
echo ROOT=%SIM3_ROOT%>>"%CONSOLE_LOG%"
echo MAX_LOOPS=%MAX_LOOPS%>>"%CONSOLE_LOG%"

where py.exe >nul 2>&1
if errorlevel 1 goto :try_python

py.exe -3 "%SIM3_ROOT%\LOOP\sim3_v4_loop_controller.py" --root "%SIM3_ROOT%" --max-loops "%MAX_LOOPS%" >>"%CONSOLE_LOG%" 2>&1
set "RC=%ERRORLEVEL%"
goto :done

:try_python
where python.exe >nul 2>&1
if errorlevel 1 goto :python_not_found

python.exe "%SIM3_ROOT%\LOOP\sim3_v4_loop_controller.py" --root "%SIM3_ROOT%" --max-loops "%MAX_LOOPS%" >>"%CONSOLE_LOG%" 2>&1
set "RC=%ERRORLEVEL%"
goto :done

:python_not_found
echo PYTHON_NOT_FOUND>>"%CONSOLE_LOG%"
set "RC=90"

:done
echo FINISHED_AT=%DATE% %TIME%>>"%CONSOLE_LOG%"
echo SIM3_V4_7_FULL_AUTO_EXIT_CODE=%RC%>>"%CONSOLE_LOG%"
exit /b %RC%
