# 🐳 حل مشاكل Docker - دليل العميل

## ❌ **المشكلة المواجهة:**
```
unable to get image 'university-chatbot2-badya-chatbot': error during connect: 
Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.51/images/...": 
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified
```

## 🎯 **السبب:**
Docker Desktop غير متصل أو لا يعمل بشكل صحيح.

---

## 🛠️ **الحلول السريعة:**

### **الحل 1: تشغيل Docker Desktop**
1. **افتح Start Menu** واكتب "Docker Desktop"
2. **شغل Docker Desktop** وانتظر حتى يظهر "Docker Desktop is running"
3. **تأكد من الأيقونة** في System Tray (بجانب الساعة)
4. **اختبر Docker**:
   ```bash
   docker --version
   docker-compose --version
   ```
5. **جرب المشروع مرة أخرى**:
   ```bash
   docker-compose up --build -d
   ```

### **الحل 2: إعادة تشغيل Docker**
```powershell
# افتح PowerShell كـ Administrator
net stop com.docker.service
net start com.docker.service

# أو
Restart-Service docker
```

### **الحل 3: تنظيف Docker Cache**
```bash
docker system prune -a -f
docker-compose down --remove-orphans
docker-compose up --build -d
```

---

## 🚀 **الحل البديل السريع (مُوصى به):**

إذا Docker لا يزال لا يعمل، استخدم **البداية السريعة** بدلاً منه:

### **Windows:**
```cmd
# 1. تحميل المشروع (إذا لم تفعل بعد)
git clone https://github.com/abdelkhalek-soudy/university-chatbot2.git
cd university-chatbot2

# 2. إنشاء البيئة الافتراضية
python -m venv venv
venv\Scripts\activate

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. إعداد OpenAI API Key
copy .env.example .env
notepad .env

# 5. تشغيل المشروع
python app.py
```

### **Linux/Ubuntu:**
```bash
# 1. تحميل المشروع
git clone https://github.com/abdelkhalek-soudy/university-chatbot2.git
cd university-chatbot2

# 2. إنشاء البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. إعداد OpenAI API Key
cp .env.example .env
nano .env

# 5. تشغيل المشروع
python app.py
```

**النتيجة:** المشروع سيعمل على `http://server-ip:5000` ✅

---

## 🔧 **إعداد OpenAI API Key:**

في ملف `.env`، غير هذا السطر:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

إلى:
```env
OPENAI_API_KEY=sk-المفتاح-الذي-حصلت-عليه-من-OpenAI
```

---

## 🎯 **مقارنة الحلول:**

| الطريقة | الوقت | الصعوبة | الموثوقية |
|---------|-------|---------|-----------|
| **إصلاح Docker** | 15-30 دقيقة | متوسط | متغيرة |
| **البداية السريعة** | 5 دقائق | سهل | عالية ✅ |

---

## 🆘 **إذا استمرت المشاكل:**

### **مع Docker:**
1. **أعد تثبيت Docker Desktop** من الصفر
2. **تأكد من تفعيل WSL 2** في Windows
3. **أعد تشغيل الجهاز** بعد التثبيت

### **مع Python:**
1. **تأكد من تثبيت Python 3.8+**
2. **استخدم البيئة الافتراضية** دائماً
3. **تحقق من OpenAI API Key**

---

## 🎉 **الخلاصة:**

### **✅ الحل المُوصى به:**
**استخدم البداية السريعة** - أسرع وأكثر موثوقية!

### **🐳 Docker (اختياري):**
يمكن تجربته لاحقاً عندما يكون لديك وقت أكثر لحل المشاكل.

### **🚀 النتيجة النهائية:**
المشروع سيعمل بنجاح في كلا الحالتين!

---

## 📞 **للدعم:**
إذا واجهت أي مشاكل أخرى، راجع:
- `QUICK_START_GUIDE.md` - للبداية السريعة
- `CLIENT_DEPLOYMENT_GUIDE.md` - للدليل الكامل
