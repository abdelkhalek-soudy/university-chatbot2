# تثبيت Python يدوياً - الحل الأسرع

## المشكلة
تثبيت Python التلقائي بياخد وقت طويل. الحل الأسرع هو التثبيت اليدوي.

## الخطوات السريعة

### 1. تحميل Python
- اذهب إلى: https://www.python.org/downloads/
- اضغط على "Download Python 3.11.x" (أحدث إصدار)
- حمل الملف

### 2. تثبيت Python
- شغل الملف المحمل
- **مهم جداً**: فعل "Add Python to PATH" ✅
- اضغط "Install Now"
- انتظر انتهاء التثبيت

### 3. تشغيل المشروع
بعد تثبيت Python، افتح Command Prompt في مجلد المشروع وشغل:

```bash
# الطريقة الأولى
QUICK_START.bat

# أو الطريقة الثانية
python -m pip install -r requirements.txt
python app.py
```

### 4. فتح الموقع
- افتح المتصفح على: http://localhost:5000
- للمستخدمين: http://localhost:5000/chat
- للإدارة: http://localhost:5000/admin

## بيانات الدخول
- **المستخدم العادي**: سجل حساب جديد
- **الإدارة**: 
  - اسم المستخدم: `admin`
  - كلمة المرور: `badya@2024`

## إذا واجهت مشاكل
1. تأكد من تفعيل "Add to PATH" أثناء التثبيت
2. أعد تشغيل Command Prompt بعد تثبيت Python
3. تأكد من وجود اتصال إنترنت لتحميل المكتبات
