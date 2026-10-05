@echo off
cd /d "%~dp0"
set "HOST=127.0.0.1"
set "PORT=8001"
cd backend
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3.14 start_server.py
) else (
    python start_server.py
)
