@echo off
title تشغيل جميع خدمات جامعة باديا
echo ========================================
echo    تشغيل جميع خدمات جامعة باديا - الإصدار 1.0
echo    تم التطوير بواسطة: عبدالخالق محمد
echo    حقوق النشر © 2024 - جميع الحقوق محفوظة
echo ========================================
echo.

:: التحقق من تثبيت Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo خطأ: Python غير مثبت أو غير مضاف إلى متغيرات النظام.
    echo يرجى تثبيت Python 3.8 أو أحدث من الموقع الرسمي.
    pause
    exit /b 1
)

:: تشغيل التطبيق
echo جاري تشغيل جميع خدمات جامعة باديا...
echo يرجى الانتظار...

start "" http://127.0.0.1:5000/user/portal
start "" http://127.0.0.1:5000/user/chat
start "" http://127.0.0.1:5000/admin/dashboard

:: تشغيل الخادم
echo.
echo تم فتح المتصفح بجميع الروابط التالية:
echo 1. البوابة الرئيسية: http://127.0.0.1:5000/user/portal
echo 2. شات المستخدم: http://127.0.0.1:5000/user/chat
echo 3. لوحة التحكم: http://127.0.0.1:5000/admin/dashboard
echo.
python app.py

pause
