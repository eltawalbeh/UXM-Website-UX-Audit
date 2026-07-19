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

if not exist ".env" (
  copy /y ".env.example" ".env" >nul
  echo A local configuration file was created: prototype\.env
  echo Add your AI and operator credentials, save it, then run this launcher again.
  start "UXM configuration" notepad.exe ".env"
  pause
  exit /b 1
)

for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do set "%%A=%%B"
if "%UXM_AI_API_KEY%"=="" (
  echo UXM_AI_API_KEY is empty in prototype\.env.
  start "UXM configuration" notepad.exe ".env"
  pause
  exit /b 1
)
if "%UXM_OPERATOR_EMAIL%"=="" (
  echo UXM_OPERATOR_EMAIL is empty in prototype\.env.
  start "UXM configuration" notepad.exe ".env"
  pause
  exit /b 1
)
if "%UXM_OPERATOR_PASSWORD%"=="" (
  echo UXM_OPERATOR_PASSWORD is empty in prototype\.env.
  start "UXM configuration" notepad.exe ".env"
  pause
  exit /b 1
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

start "UXM Audit" http://127.0.0.1:4173/login.html
".venv\Scripts\python.exe" -m backend.api_server
