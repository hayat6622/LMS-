@echo off
setlocal

:: Get the directory where the batch file is located
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo ==========================================
echo    Django LMS - Auto Startup Script
echo ==========================================
echo Current Directory: %CD%

:: Check if manage.py exists
if not exist "manage.py" (
    echo [ERROR] manage.py not found in %CD%
    echo Make sure this .bat file is in the project root folder.
    pause
    exit /b
)

:: Activate the virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] venv\Scripts\activate.bat not found.
    echo Attempting to run with system python...
)

:: Try to open the URL
echo Opening project link...
:: Try chrome specifically first, then fallback to default browser
start chrome "http://127.0.0.1:8000/" 2>nul || (
    echo [INFO] Chrome not found in PATH, using default browser.
    start "" "http://127.0.0.1:8000/"
)

:: Start the Django server
echo Starting server on http://127.0.0.1:8000/
echo (Press Ctrl+C to stop)
python manage.py runserver

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Server failed to start.
    pause
)

pause
