@echo off
echo Starting Mumble Quick...

:: Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if the app file exists
if not exist "src\mumble_quick\app.py" (
    echo Error: Could not find src\mumble_quick\app.py
    echo Current directory: %CD%
    pause
    exit /b 1
)

:: Check if required directories exist
if not exist "src\shared" (
    echo Error: Could not find shared modules directory
    pause
    exit /b 1
)

if not exist "src\assets" (
    echo Error: Could not find assets directory
    pause
    exit /b 1
)

:: Run with error output
echo Running Mumble Quick...
python src/mumble_quick/app.py 2> error_quick.log
if errorlevel 1 (
    echo Application crashed. Check error_quick.log for details.
    type error_quick.log
    pause
    exit /b 1
)

pause 