@echo off
title PrintPulse Screenshot Tool Launcher
echo Starting Screenshot and Scrolling Utility...
echo Make sure Python and CustomTkinter are installed.
python "%~dp0screenshot_tool.py"
if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to run screenshot_tool.py.
    echo Installing dependencies and trying again...
    pip install customtkinter pillow
    python "%~dp0screenshot_tool.py"
)
pause
