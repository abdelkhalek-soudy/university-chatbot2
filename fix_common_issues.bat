@echo off
chcp 65001 >nul
title Badya University - Fix Common Issues
color 0E
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 Badya University System                      ║
echo ║                  Common Issues Fixer                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [1] Killing any existing Python processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
echo [✓] Processes cleared

echo.
echo [2] Checking Python installation...
python --version
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo [3] Checking pip...
pip --version
if %ERRORLEVEL% neq 0 (
    echo [ERROR] pip not found!
    pause
    exit /b 1
)

echo.
echo [4] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo.
echo [5] Installing/updating all requirements...
pip install -r requirements.txt --upgrade --quiet
echo [✓] Requirements updated

echo.
echo [6] Checking Flask installation...
python -c "import flask; print('Flask version:', flask.__version__)"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Flask import failed!
    pip install flask --force-reinstall
)

echo.
echo [7] Checking OpenAI installation...
python -c "import openai; print('OpenAI version:', openai.__version__)"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] OpenAI import failed!
    pip install openai --force-reinstall
)

echo.
echo [8] Testing server startup...
timeout /t 2 /nobreak >nul
start /b python app.py
timeout /t 5 /nobreak >nul

curl -s http://127.0.0.1:5000/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [✓] Server test successful!
    taskkill /f /im python.exe >nul 2>&1
) else (
    echo [!] Server test failed - check your .env file and database
    taskkill /f /im python.exe >nul 2>&1
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    FIXES COMPLETED!                          ║
echo ║                                                              ║
echo ║  Now try running: start_user_portal.bat                     ║
echo ║                                                              ║
echo ║  If issues persist, check:                                   ║
echo ║  • .env file has correct OpenAI API key                     ║
echo ║  • Port 5000 is not used by another application             ║
echo ║  • Windows Firewall allows Python                           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
