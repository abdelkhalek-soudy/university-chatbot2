@echo off
chcp 1256 >nul
title تثبيت Git لرفع المشروع على GitHub
echo =========================================
echo         تثبيت Git - جامعة باديا
echo =========================================
echo.

echo 🔍 فحص وجود Git...
git --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Git مثبت بالفعل!
    git --version
    echo.
    echo يمكنك الآن رفع المشروع على GitHub
    pause
    exit /b 0
)

echo ❌ Git غير مثبت على النظام
echo.
echo 📥 سيتم فتح صفحة تحميل Git...
echo.
echo 📋 خطوات التثبيت:
echo 1. اضغط Download for Windows
echo 2. شغل الملف المحمل
echo 3. اضغط Next في جميع الخطوات (الإعدادات الافتراضية جيدة)
echo 4. انتظر انتهاء التثبيت
echo 5. أعد تشغيل Command Prompt
echo 6. شغل هذا الملف مرة أخرى للتأكد
echo.

pause
echo 🌐 فتح صفحة تحميل Git...
start "" https://git-scm.com/download/win

echo.
echo ⏳ بعد تثبيت Git:
echo 1. أغلق Command Prompt الحالي
echo 2. افتح Command Prompt جديد
echo 3. انتقل لمجلد المشروع: cd C:\Users\pc\Downloads\FlaskChatbotProject
echo 4. شغل: git --version للتأكد من التثبيت
echo 5. ثم ابدأ برفع المشروع
echo.
pause
