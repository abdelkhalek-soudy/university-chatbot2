@echo off
chcp 65001 >nul
title Badya University - Student Portal
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    Badya University                          ║
echo ║                   Student Portal Launcher                    ║
echo ║                                                              ║
echo ║              Developed by: Abdelkhalek Mohamed               ║
echo ║                Copyright 2024 - All Rights Reserved          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Change to project directory
cd /d "%~dp0"

:: Check if Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in system PATH.
    echo Please install Python 3.8 or later from: https://python.org
    echo.
    pause
    exit /b 1
)
echo [✓] Python is installed

:: Check if virtual environment exists and activate it
echo [2/6] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo [✓] Virtual environment found - activating...
    call venv\Scripts\activate.bat
) else (
    echo [!] No virtual environment found - using system Python
)

:: Install/update requirements
echo [3/6] Installing requirements...
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet --disable-pip-version-check
    if %ERRORLEVEL% neq 0 (
        echo [!] Some packages might need updating, continuing...
    ) else (
        echo [✓] Requirements installed successfully
    )
) else (
    echo [!] No requirements.txt found
)

:: Kill any existing Python processes to avoid port conflicts
echo [4/6] Checking for existing server processes...
taskkill /f /im python.exe >nul 2>&1
timeout /t 1 /nobreak >nul

:: Start Flask server
echo [5/6] Starting Flask server...
echo Please wait for the server to initialize...
start /b python app.py

:: Wait and check server status
echo [6/6] Waiting for server to start...
set /a attempts=0
:check_server
set /a attempts+=1
timeout /t 2 /nobreak >nul

:: Try to connect to health endpoint
curl -s http://127.0.0.1:5000/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [✓] Server is running successfully!
    goto server_ready
)

if %attempts% lss 10 (
    echo [%attempts%/10] Server starting... please wait
    goto check_server
)

echo [!] Server might still be starting, opening browser anyway...

:server_ready
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                     SERVER IS READY!                        ║
echo ║                                                              ║
echo ║  🌐 Main Server:      http://127.0.0.1:5000                 ║
echo ║  👨‍🎓 Student Portal:   http://127.0.0.1:5000/user-portal      ║
echo ║  👨‍💼 Admin Dashboard:  http://127.0.0.1:5000/admin            ║
echo ║                                                              ║
echo ║  Opening Student Portal in your browser...                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Open browser
start "" http://127.0.0.1:5000/user-portal

echo Press any key to stop the server and exit...
pause >nul

:: Cleanup
echo.
echo Stopping server...
taskkill /f /im python.exe >nul 2>&1
echo [✓] Server stopped successfully!
echo.
echo Thank you for using Badya University Student Portal!
timeout /t 2 /nobreak >nul
