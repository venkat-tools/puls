@echo off
:: Self-elevating script to run Node Server as Administrator
:init
set localdirectory=%~dp0
set tempname=%temp%\getadmin.vbs
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges to run PrintPulse AI Server...
    echo Set UAC = CreateObject^("Shell.Application"^) > "%tempname%"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%tempname%"
    "%tempname%"
    del "%tempname%"
    exit /B
)

cd /d "%localdirectory%."
title PrintPulse AI Admin Web Server (Node.js)

:: Kill any process currently occupying port 3000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo ======================================================================
echo             Starting PrintPulse AI Node.js Admin Web Server
echo ======================================================================
echo.
echo Server is launching on: http://localhost:3000
echo One-click repairs are now active through this terminal socket.
echo Keep this window open while using the web application dashboard.
echo.
echo ======================================================================

:: Check if python is available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python server.py
    goto end
)

:: Fallback to compiled main.exe
if exist main.exe (
    main.exe
    goto end
)

echo.
echo [ERROR] Neither Python nor main.exe was detected.
echo.
pause

:end
