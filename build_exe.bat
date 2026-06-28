@echo off
echo =======================================================
echo          Building PrintPulse Standalone Executable
echo =======================================================
echo.

:: Detect Python and PyInstaller paths
set PYTHON_EXE=C:\Users\USER\AppData\Local\Programs\Python\Python312\python.exe
set PYINSTALLER_EXE=C:\Users\USER\AppData\Local\Programs\Python\Python312\Scripts\pyinstaller.exe

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python 3.12 was not found at %PYTHON_EXE%
    pause
    exit /B 1
)

if not exist "%PYINSTALLER_EXE%" (
    echo [ERROR] PyInstaller was not found at %PYINSTALLER_EXE%
    echo Installing pyinstaller...
    "%PYTHON_EXE%" -m pip install pyinstaller
)

echo Compiling server.py to standalone main.exe...
"%PYINSTALLER_EXE%" --onefile --name main server.py

echo.
echo =======================================================
echo                  Build Process Completed!
echo     The output file is located in the 'dist' directory.
echo =======================================================
echo.
pause
