@echo off
title Living the Dream Trading — Launcher
echo.
echo  =====================================================
echo   Living the Dream Trading Dashboard
echo  =====================================================
echo.

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

echo  [1/3] Starting FastAPI backend on port 8000...
start "LTD Backend (port 8000)" cmd /k "cd /d "%ROOT%" && (if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat") && python -m uvicorn backend.main:app --reload --port 8000"

echo  [2/3] Starting React frontend on port 5173...
start "LTD Frontend (port 5173)" cmd /k "cd /d "%ROOT%\frontend" && npm run dev"

echo  [3/3] Opening browser in 7 seconds...
timeout /t 7 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo  Dashboard is launching. Close this window when done.
echo    Backend  : http://localhost:8000/docs
echo    Frontend : http://localhost:5173
echo.
pause >nul
