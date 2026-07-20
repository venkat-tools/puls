@echo off
:: Self-elevating script to run Node Server as Administrator
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

:: Resolve python path (check local appdata if not in system path when elevated)
set "PYTHON_CMD=python"
python --version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe" (
        set "PYTHON_CMD=C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe"
    )
)

:: Run python server if resolved
"%PYTHON_CMD%" --version >nul 2>&1
if %errorlevel% equ 0 (
    "%PYTHON_CMD%" server.py
    if %errorlevel% neq 0 (
        echo.
        echo [CRASH] Python server exited with error code %errorlevel%.
        pause
    )
    goto end
)

:: Fallback to compiled main.exe
if exist main.exe (
    main.exe
    if %errorlevel% neq 0 (
        echo.
        echo [CRASH] main.exe exited with error code %errorlevel%.
        pause
    )
    goto end
)

echo.
echo [ERROR] Neither Python nor main.exe was detected.
echo.
pause

:end
