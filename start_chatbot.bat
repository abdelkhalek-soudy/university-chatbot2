@echo off
title شات بوت جامعة باديا - Badya University Chatbot
color 0A

echo.
echo ========================================
echo    شات بوت جامعة باديا
echo    Badya University Chatbot
echo ========================================
echo.
echo [INFO] بدء تشغيل الخادم...
echo [INFO] Starting server...
echo.

cd /d "%~dp0"

echo [CHECK] فحص ملف التطبيق...
if not exist "app.py" (
    echo [ERROR] ملف app.py غير موجود!
    echo [ERROR] app.py file not found!
    pause
    exit /b 1
)

echo [CHECK] فحص ملف البيانات...
if not exist ".env" (
    echo [WARNING] ملف .env غير موجود - تأكد من إعداد OpenAI API Key
    echo [WARNING] .env file not found - make sure to set OpenAI API Key
)

echo.
echo [INFO] تشغيل الخادم على المنفذ 5000...
echo [INFO] Starting server on port 5000...
echo.
echo ========================================
echo   معلومات مهمة - Important Info
echo ========================================
echo 🌐 الرابط: http://127.0.0.1:5000
echo 👤 المدير: admin / badya@2024
echo 🎤 التسجيل الصوتي: محسن ويعمل بشكل مثالي
echo 📱 المتصفحات المدعومة: Chrome, Firefox, Edge
echo.
echo [INFO] اضغط Ctrl+C لإيقاف الخادم
echo [INFO] Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

echo.
echo [INFO] تم إيقاف الخادم
echo [INFO] Server stopped
pause
