@echo off
echo ==========================================
echo   BADYA UNIVERSITY CHATBOT SERVER
echo ==========================================
echo.
echo Starting server...
echo.
echo Server will be available at:
echo - Main Page: http://127.0.0.1:5000/
echo - Admin Dashboard: http://127.0.0.1:5000/admin
echo - User Portal: http://127.0.0.1:5000/user-portal
echo - Test Connection: http://127.0.0.1:5000/test
echo.
echo Admin Credentials:
echo - Username: admin
echo - Password: badya@2024
echo.
echo Troubleshooting:
echo - If login fails, go to: http://127.0.0.1:5000/test
echo - Check README_TROUBLESHOOTING.md for help
echo.
echo ==========================================
echo.
cd /d "%~dp0"
python app.py
echo.
echo Server stopped. Press any key to close...
pause
