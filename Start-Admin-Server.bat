@echo off
:: Self-elevating script to run Node Server as Administrator
:init
set localdirectory=%~dp0
set tempname=%temp%\getadmin.vbs
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges to run Venkat Windows Tool Kit Server...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /B
)

cd /d "%~dp0."
title Venkat Windows Tool Kit Admin Web Server (Node.js)

:: Kill any process currently occupying port 3000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo ======================================================================
echo             Starting Venkat Windows Tool Kit Node.js Admin Web Server
echo ======================================================================
echo.
echo Server is launching on: http://localhost:3000
echo One-click repairs are now active through this terminal socket.
echo Keep this window open while using the web application dashboard.
echo.
echo ======================================================================

if exist main.exe (
    main.exe
    goto end
)

if exist server.py (
    python server.py
    goto end
)

echo.
echo [ERROR] main.exe was not found in %~dp0
echo.
pause

:end
