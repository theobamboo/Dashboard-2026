@echo off
title Living the Dream Trading — Launcher
echo.
echo  =====================================================
echo   Living the Dream Trading Dashboard
echo  =====================================================
echo.
echo  [1/3] Starting FastAPI backend on port 8000...
start "LTD — Backend" PowerShell -NoExit -Command ^
  "cd '%~dp0'; if (Test-Path '.venv\Scripts\Activate.ps1') { & '.venv\Scripts\Activate.ps1' }; python -m uvicorn backend.main:app --reload --port 8000"

echo  [2/3] Starting React frontend on port 5173...
start "LTD — Frontend" PowerShell -NoExit -Command ^
  "cd '%~dp0frontend'; npm run dev"

echo  [3/3] Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul
start "" http://localhost:5173

echo.
echo  Both servers are running. Close this window when done.
echo  Backend : http://localhost:8000
echo  Frontend: http://localhost:5173
echo.
pause
