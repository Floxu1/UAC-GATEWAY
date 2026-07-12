@echo off
cd /d "%~dp0"
where pythonw.exe >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw.exe "%~dp0main.py"
) else (
  start "" python.exe "%~dp0main.py"
)
