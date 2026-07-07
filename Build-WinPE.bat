@echo off
:: Check if running as Admin
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges to run WinPE Builder...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /B
)

cd /d "%~dp0."
title WinPE ISO Builder

echo ======================================================================
echo             Starting PrintPulse WinPE ISO Compiler
echo ======================================================================
echo.

powershell -ExecutionPolicy Bypass -File Build-WinPE-ISO.ps1

echo.
echo ======================================================================
echo Done! Press any key to exit.
echo ======================================================================
pause
