@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Creating project-local Python environment...
  python -m venv .venv
  if errorlevel 1 (
    echo Unable to create .venv. Ensure Python 3 is installed and available as "python".
    pause
    exit /b 1
  )
)

echo Installing Python requirements...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Unable to install Python requirements.
  pause
  exit /b 1
)

echo Bootstrapping local audit data from committed pilots...
".venv\Scripts\python.exe" ..\scripts\bootstrap_prototype.py
if errorlevel 1 (
  echo Unable to bootstrap the local audit database.
  pause
  exit /b 1
)

start "UXM Audit" http://127.0.0.1:4173
".venv\Scripts\python.exe" -m backend.api_server
