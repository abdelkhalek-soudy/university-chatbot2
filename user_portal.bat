@echo off
chcp 1256 >nul
title Badya University - Student Portal
echo =========================================
echo    Badya University - Student Portal
echo    Developed by: Abdelkhalek Mohamed
echo    Copyright 2024 - All Rights Reserved
echo =========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in system PATH.
    echo Please install Python 3.8 or later from the official website.
    pause
    exit /b 1
)

:: Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [INFO] No virtual environment found, using system Python...
)

:: Install requirements if needed
if exist "requirements.txt" (
    echo [INFO] Installing/updating requirements...
    pip install -r requirements.txt >nul 2>&1
)

echo Starting Flask server...
echo Please wait for the server to start...
echo.

:: Start Flask server in background and wait a moment
start /b python app.py

:: Wait for server to start
echo Waiting for server to initialize...
timeout /t 3 /nobreak >nul

:: Check if server is running
echo Checking server status...
curl -s http://127.0.0.1:5000/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Server is running!
    echo Opening Student Portal in browser...
    start "" http://127.0.0.1:5000/user-portal
) else (
    echo [INFO] Server might still be starting...
    echo Opening browser anyway...
    start "" http://127.0.0.1:5000/user-portal
)

echo.
echo =========================================
echo Server is running on: http://127.0.0.1:5000
echo Student Portal: http://127.0.0.1:5000/user-portal
echo Admin Dashboard: http://127.0.0.1:5000/admin
echo =========================================
echo.
echo Press any key to stop the server and exit...
pause >nul

:: Stop the Flask server
echo Stopping server...
taskkill /f /im python.exe >nul 2>&1
echo Server stopped. Goodbye!
pause
