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
powershell -Command "Start-Process powershell -ArgumentList '-NoExit','-Command','cd \"%ROOT%\"; if (Test-Path \".venv\Scripts\Activate.ps1\") { & \".venv\Scripts\Activate.ps1\" }; python -m uvicorn backend.main:app --reload --port 8000'"

echo  [2/3] Starting React frontend on port 5173...
powershell -Command "Start-Process powershell -ArgumentList '-NoExit','-Command','cd \"%ROOT%\frontend\"; npm run dev'"

echo  [3/3] Opening browser in 6 seconds...
timeout /t 6 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo  Dashboard is launching. Close this window when done.
echo    Backend  : http://localhost:8000/docs
echo    Frontend : http://localhost:5173
echo.
pause >nul
