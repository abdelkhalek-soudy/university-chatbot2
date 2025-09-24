@echo off
chcp 1256 >nul
title رفع مشروع جامعة باديا على GitHub
echo =========================================
echo     رفع مشروع جامعة باديا على GitHub
echo =========================================
echo.

echo 🔍 فحص Git...
git --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Git غير مثبت! يرجى تثبيته أولاً
    pause
    exit /b 1
)

echo ✅ Git مثبت بنجاح!
echo.

echo 📁 التأكد من المجلد الحالي...
echo المجلد الحالي: %CD%
echo.

echo ⚙️ إعداد Git (إذا لم يتم من قبل)...
echo يرجى إدخال اسم المستخدم GitHub:
set /p username="اسم المستخدم: "
echo يرجى إدخال البريد الإلكتروني:
set /p email="البريد الإلكتروني: "

git config --global user.name "%username%"
git config --global user.email "%email%"

echo.
echo 🚀 بدء رفع المشروع...
echo.

echo 1️⃣ تهيئة Git repository...
git init

echo.
echo 2️⃣ إضافة جميع الملفات...
git add .

echo.
echo 3️⃣ إنشاء أول commit...
git commit -m "🎓 Initial commit: Badya University Chatbot

✨ Features:
- 🤖 AI-powered chatbot with GPT-4
- 🎤 Advanced audio recording with Whisper
- 📁 Document analysis capabilities
- 👥 User management system
- 📊 Question analytics
- 🛡️ Multi-level security system
- 🔊 Fixed audio recording issues (400 error)
- 🌐 Bilingual support (Arabic/English)

🛠️ Tech Stack:
- Python Flask
- OpenAI GPT-4 & Whisper
- SQLite Database
- JWT Authentication
- Bootstrap UI
- MediaRecorder API

👨‍💻 Developer: Abdelkhalek Mohamed
🏫 University: Badya University
📅 Year: 2024"

echo.
echo 4️⃣ إعداد branch main...
git branch -M main

echo.
echo ⚠️ الآن يجب إنشاء المستودع على GitHub:
echo.
echo 📋 خطوات إنشاء المستودع:
echo 1. اذهب إلى: https://github.com/abdelkhalek-soudy
echo 2. اضغط "New Repository"
echo 3. اسم المستودع: university-chatbot
echo 4. الوصف: 🎓 شات بوت ذكي لجامعة باديا مع تسجيل صوتي متقدم
echo 5. اختر Public
echo 6. لا تضع ✅ في أي خيارات إضافية
echo 7. اضغط "Create Repository"
echo.

echo 🌐 فتح GitHub...
start "" https://github.com/abdelkhalek-soudy

echo.
echo ⏳ بعد إنشاء المستودع، اضغط أي زر للمتابعة...
pause

echo.
echo 5️⃣ ربط المشروع بـ GitHub...
git remote add origin https://github.com/abdelkhalek-soudy/university-chatbot.git

echo.
echo 6️⃣ رفع المشروع...
git push -u origin main

echo.
echo 🎉 تم رفع المشروع بنجاح!
echo.
echo 🔗 رابط المشروع: https://github.com/abdelkhalek-soudy/university-chatbot
echo.
echo ✅ يمكن للعميل الآن تحميل المشروع باستخدام:
echo git clone https://github.com/abdelkhalek-soudy/university-chatbot.git
echo.
echo أو تحميل ZIP من الموقع مباشرة
echo.
pause
