@echo off
title Tifinify Backend Server
cd /d "%~dp0"

echo =======================================================
echo          TIFINIFY - WAMP BACKEND LAUNCHER
echo =======================================================
echo.
echo Starting Tifinify backend on port 5000...
echo.
echo You can access the application through WAMP at:
echo   - http://localhost:8080/
echo   - http://tifinify.local/
echo   - http://localhost/tifinify
echo.
echo Press CTRL+C to stop the server.
echo =======================================================
echo.

".venv\Scripts\python.exe" run.py
pause
