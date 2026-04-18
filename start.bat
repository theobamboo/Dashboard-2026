@echo off
title Living the Dream Trading — Launcher
echo.
echo  =====================================================
echo   Living the Dream Trading Dashboard
echo  =====================================================
echo.

:: ── Resolve the project root (the folder containing this .bat) ──────────────
set "ROOT=%~dp0"
:: Remove trailing backslash
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

:: ── 1) Backend — activate venv then run uvicorn ──────────────────────────────
echo  [1/3] Starting FastAPI backend on port 8000...
start "LTD Backend :8000" cmd /k "cd /d "%ROOT%" && if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat" && python -m uvicorn backend.main:app --reload --port 8000"

:: ── 2) Frontend — npm run dev ─────────────────────────────────────────────────
echo  [2/3] Starting React frontend on port 5173...
start "LTD Frontend :5173" cmd /k "cd /d "%ROOT%\frontend" && npm run dev"

:: ── 3) Wait 5s, then open browser ─────────────────────────────────────────────
echo  [3/3] Browser opens in 5 seconds...
timeout /t 5 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo  Servers are running in separate windows.
echo    Backend  ^> http://localhost:8000
echo    Frontend ^> http://localhost:5173
echo.
echo  Close this window (or press any key) when done.
pause >nul
