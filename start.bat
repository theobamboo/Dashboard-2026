@echo off
setlocal EnableDelayedExpansion

title Living the Dream — Launcher

:: ============================================================
:: Resolve absolute project root from the location of this .bat
:: (works regardless of working directory at launch time)
:: ============================================================
set "ROOT=%~dp0"
if "!ROOT:~-1!"=="\" set "ROOT=!ROOT:~0,-1!"

set "VENV_PYTHON=!ROOT!\.venv\Scripts\python.exe"
set "VENV_UVICORN=!ROOT!\.venv\Scripts\uvicorn.exe"
set "FRONTEND_DIR=!ROOT!\frontend"

echo.
echo  ====================================================
echo   Living the Dream Trading Dashboard
echo  ====================================================
echo.

:: ============================================================
:: PRE-FLIGHT CHECK 1: Virtual environment
:: ============================================================
if not exist "!VENV_PYTHON!" (
    echo  [ERROR] .venv not found at:  !VENV_PYTHON!
    echo  Run:  python -m venv .venv  then  pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

if not exist "!VENV_UVICORN!" (
    echo  [ERROR] uvicorn not installed in venv.
    echo  Run:  .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

:: ============================================================
:: PRE-FLIGHT CHECK 2: Frontend node_modules
:: ============================================================
if not exist "!FRONTEND_DIR!\node_modules" (
    echo  [ERROR] node_modules missing. Running npm install first...
    pushd "!FRONTEND_DIR!"
    npm install
    if !ERRORLEVEL! neq 0 (
        echo  [ERROR] npm install failed. Fix frontend dependencies first.
        popd
        pause
        exit /b 1
    )
    popd
    echo  [OK] npm install complete.
)

:: ============================================================
:: KILL STALE PORT HOLDERS (silently)
:: Prevents "address already in use" crashes on relaunch
:: ============================================================
echo  [1/4] Clearing stale processes on ports 8000 and 5173...

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R ":8000 " 2^>nul') do (
    taskkill /PID %%P /F >nul 2>&1
)
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R ":5173 " 2^>nul') do (
    taskkill /PID %%P /F >nul 2>&1
)

:: ============================================================
:: LAUNCH BACKEND — call venv executables DIRECTLY (no activate)
:: No --reload: prevents mid-session restarts from autosave/git
:: ============================================================
echo  [2/4] Starting FastAPI backend on port 8000...
start "LTD-Backend" cmd /k "cd /d "!ROOT!" && "!VENV_UVICORN!" backend.main:app --port 8000"

:: ============================================================
:: LAUNCH FRONTEND
:: ============================================================
echo  [3/4] Starting React frontend on port 5173...
start "LTD-Frontend" cmd /k "cd /d "!FRONTEND_DIR!" && npm run dev"

:: ============================================================
:: HEALTH CHECK LOOP — poll /health instead of blind sleep
:: Waits up to 60 seconds for the backend to respond
:: ============================================================
echo  [4/4] Waiting for backend to be ready (up to 60s)...

set "READY=0"
set "TRIES=0"
:health_loop
if !TRIES! geq 30 goto health_timeout
timeout /t 2 /nobreak >nul
set /a TRIES+=1

:: Use PowerShell to hit the health endpoint (curl not reliable on all Win10)
powershell -NoProfile -Command "try { $r=(Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop).StatusCode; if($r -eq 200){exit 0} } catch { exit 1 }" >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "READY=1"
    goto health_done
)
goto health_loop

:health_timeout
echo.
echo  [WARN] Backend did not respond within 60s.
echo  Check the LTD-Backend terminal window for errors.
echo  Opening browser anyway — it may work in a moment.
goto open_browser

:health_done
echo  [OK] Backend is up!

:open_browser
echo  Opening http://localhost:5173 ...
start "" http://localhost:5173

echo.
echo  ====================================================
echo   Dashboard is running.
echo   Backend  : http://localhost:8000/docs
echo   Frontend : http://localhost:5173
echo   Close LTD-Backend and LTD-Frontend windows to stop.
echo  ====================================================
echo.
endlocal
