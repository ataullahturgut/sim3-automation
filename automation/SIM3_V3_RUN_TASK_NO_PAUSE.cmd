@echo off
setlocal EnableExtensions
for %%I in ("%~dp0.") do set "SIM3_V3_ROOT=%%~fI"
set "TASK_FILE=%~1"
if not defined TASK_FILE set "TASK_FILE=%SIM3_V3_ROOT%\INBOX\TASK.txt"

where py.exe >nul 2>&1
if errorlevel 1 goto :try_python
py.exe -3 "%SIM3_V3_ROOT%\sim3_v3_worker.py" --root "%SIM3_V3_ROOT%" --task "%TASK_FILE%"
set "RC=%ERRORLEVEL%"
goto :done

:try_python
where python.exe >nul 2>&1
if errorlevel 1 goto :python_not_found
python.exe "%SIM3_V3_ROOT%\sim3_v3_worker.py" --root "%SIM3_V3_ROOT%" --task "%TASK_FILE%"
set "RC=%ERRORLEVEL%"
goto :done

:python_not_found
echo PYTHON_NOT_FOUND
set "RC=90"

:done
echo SIM3_V3_EXIT_CODE=%RC%
exit /b %RC%
