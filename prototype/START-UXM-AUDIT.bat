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

start "UXM Audit" http://127.0.0.1:4173
".venv\Scripts\python.exe" -m backend.api_server
