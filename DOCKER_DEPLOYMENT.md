# 🐳 نشر شات بوت جامعة باديا باستخدام Docker

## 🎯 **لماذا Docker؟**
- ✅ **سهولة التثبيت**: أمر واحد فقط
- ✅ **عزل البيئة**: لا تأثير على النظام
- ✅ **نقل سهل**: يعمل على أي سيرفر
- ✅ **إدارة بسيطة**: بدء وإيقاف سهل

---

## 📋 **المتطلبات:**

### **على السيرفر:**
- Docker Engine
- Docker Compose
- 2GB RAM على الأقل
- 5GB مساحة فارغة

---

## 🚀 **خطوات التثبيت:**

### **1. تثبيت Docker (Ubuntu):**
```bash
# تحديث النظام
sudo apt update

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# إضافة المستخدم لمجموعة Docker
sudo usermod -aG docker $USER

# إعادة تسجيل الدخول أو:
newgrp docker

# تثبيت Docker Compose
sudo apt install docker-compose -y
```

### **2. تحميل المشروع:**
```bash
# تحميل من GitHub
git clone https://github.com/abdelkhalek-soudy/university-chatbot2.git
cd university-chatbot2
```

### **3. إعداد متغيرات البيئة:**
```bash
# نسخ ملف المثال
cp .env.example .env

# تحرير الملف
nano .env
```

**محتوى ملف .env:**
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
SECRET_KEY=your-very-long-random-secret-key-here
```

### **4. بناء وتشغيل المشروع:**
```bash
# بناء الصورة وتشغيل الحاوية
docker-compose up -d

# أو بناء جديد
docker-compose up --build -d
```

### **5. التحقق من التشغيل:**
```bash
# فحص حالة الحاويات
docker-compose ps

# عرض السجلات
docker-compose logs -f
```

---

## 🎛️ **إدارة النظام:**

### **أوامر أساسية:**
```bash
# تشغيل النظام
docker-compose up -d

# إيقاف النظام
docker-compose down

# إعادة تشغيل
docker-compose restart

# عرض السجلات
docker-compose logs -f badya-chatbot

# تحديث المشروع
git pull origin main
docker-compose up --build -d
```

### **فحص الصحة:**
```bash
# فحص الحاوية
docker ps

# دخول الحاوية
docker exec -it badya-university-chatbot bash

# فحص الاتصال
curl http://localhost:5000/api/health
```

---

## 🌐 **الوصول للنظام:**

بعد التشغيل، النظام متاح على:

- **الصفحة الرئيسية**: `http://server-ip:5000`
- **بوابة الطلاب**: `http://server-ip:5000/user-portal`
- **لوحة الإدارة**: `http://server-ip:5000/admin`
- **فحص الصحة**: `http://server-ip:5000/api/health`

**بيانات الدخول:**
- **المدير**: `admin` / `badya@2024`

---

## 🔧 **تخصيص الإعدادات:**

### **تغيير المنفذ:**
```yaml
# في docker-compose.yml
ports:
  - "8080:5000"  # استخدام منفذ 8080 بدلاً من 5000
```

### **إضافة SSL:**
```yaml
# إضافة Nginx مع SSL
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - badya-chatbot
```

---

## 📊 **مراقبة الأداء:**

### **استخدام الموارد:**
```bash
# استخدام CPU والذاكرة
docker stats badya-university-chatbot

# مساحة القرص
docker system df
```

### **النسخ الاحتياطي:**
```bash
# نسخ قاعدة البيانات
docker cp badya-university-chatbot:/app/chatbot.db ./backup/

# نسخ الملفات المرفوعة
docker cp badya-university-chatbot:/app/uploads ./backup/
```

---

## 🆘 **حل المشاكل:**

### **المشكلة: الحاوية لا تعمل**
```bash
# فحص السجلات
docker-compose logs badya-chatbot

# فحص حالة الحاوية
docker inspect badya-university-chatbot
```

### **المشكلة: منفذ مشغول**
```bash
# فحص المنافذ المستخدمة
sudo netstat -tlnp | grep :5000

# تغيير المنفذ في docker-compose.yml
```

### **المشكلة: نفاد الذاكرة**
```bash
# إضافة حد للذاكرة
services:
  badya-chatbot:
    # ...
    mem_limit: 1g
    memswap_limit: 1g
```

---

## 🔄 **التحديث:**

### **تحديث المشروع:**
```bash
# سحب آخر التحديثات
git pull origin main

# إعادة بناء وتشغيل
docker-compose up --build -d

# تنظيف الصور القديمة
docker image prune -f
```

### **تحديث Docker:**
```bash
# تحديث Docker Engine
sudo apt update && sudo apt upgrade docker-ce docker-ce-cli containerd.io
```

---

## 🎉 **المميزات:**

### **✅ مميزات Docker:**
- **عزل كامل**: لا يؤثر على النظام
- **نقل سهل**: نفس البيئة في كل مكان
- **تحديث آمن**: rollback سريع
- **مراقبة متقدمة**: logs وstats مدمجة

### **🚀 الأداء:**
- **بدء سريع**: أقل من دقيقة
- **استهلاك قليل**: 200-500MB RAM
- **موثوقية عالية**: auto-restart
- **صحة تلقائية**: health checks

---

## 📞 **الدعم:**

### **للمساعدة:**
```bash
# فحص شامل
docker-compose ps
docker-compose logs --tail=50
curl http://localhost:5000/api/health
```

### **إعادة تعيين كاملة:**
```bash
docker-compose down
docker system prune -f
docker-compose up --build -d
```

**النظام الآن جاهز للاستخدام مع Docker! 🐳**
