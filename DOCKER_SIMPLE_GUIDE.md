# 🐳 تشغيل شات بوت جامعة باديا بـ Docker - دليل مبسط

## 🎯 **لماذا Docker؟**
- ✅ **تثبيت بأمر واحد** - لا تعقيدات
- ✅ **بيئة معزولة** - لا يؤثر على النظام
- ✅ **سهولة الإدارة** - تشغيل وإيقاف بسيط
- ✅ **تحديث آمن** - بدون مشاكل

---

## 📋 **المتطلبات:**
- سيرفر Ubuntu 20.04+ أو CentOS 7+
- 2GB RAM على الأقل
- اتصال إنترنت مستقر
- OpenAI API Key

---

## 🚀 **التثبيت في 4 خطوات:**

### **الخطوة 1: تثبيت Docker**
```bash
# تحديث النظام
sudo apt update

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# إضافة المستخدم لمجموعة Docker
sudo usermod -aG docker $USER

# تثبيت Docker Compose
sudo apt install docker-compose -y

# تفعيل التغييرات
newgrp docker
```

### **الخطوة 2: تحميل المشروع**
```bash
# تحميل من GitHub
git clone https://github.com/abdelkhalek-soudy/university-chatbot2.git
cd university-chatbot2
```

### **الخطوة 3: إعداد OpenAI API Key**
```bash
# نسخ ملف الإعدادات
cp .env.example .env

# تحرير الملف
nano .env
```

**في ملف .env، غير هذا السطر:**
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```
**إلى:**
```env
OPENAI_API_KEY=sk-المفتاح-الذي-حصلت-عليه-من-OpenAI
```

### **الخطوة 4: تشغيل المشروع**
```bash
# بناء وتشغيل المشروع
docker-compose up --build -d
```

**خلاص! المشروع شغال على: http://server-ip:5000** 🎉

---

## 🎛️ **إدارة المشروع:**

### **أوامر أساسية:**
```bash
# تشغيل المشروع
docker-compose up -d

# إيقاف المشروع
docker-compose down

# إعادة تشغيل
docker-compose restart

# عرض السجلات
docker-compose logs -f

# فحص حالة المشروع
docker-compose ps

# فحص استخدام الموارد
docker stats badya-university-chatbot
```

### **التحديث:**
```bash
# تحديث المشروع
git pull origin main
docker-compose up --build -d
```

---

## 🌐 **الوصول للنظام:**

بعد التشغيل الناجح:

- **🏠 الصفحة الرئيسية**: `http://server-ip:5000`
- **👨‍🎓 بوابة الطلاب**: `http://server-ip:5000/user-portal`
- **👨‍💼 لوحة الإدارة**: `http://server-ip:5000/admin`

**🔐 بيانات الدخول:**
- **المستخدم**: `admin`
- **كلمة المرور**: `badya@2024`

---

## 🔧 **إعداد متقدم (اختياري):**

### **تغيير المنفذ:**
```yaml
# في docker-compose.yml
ports:
  - "8080:5000"  # استخدام منفذ 8080 بدلاً من 5000
```

### **إضافة SSL مع Nginx:**
```bash
# إنشاء ملف nginx.conf
# إعداد certbot للـ SSL
# تحديث docker-compose.yml
```

---

## 🆘 **حل المشاكل:**

### **المشكلة: "permission denied"**
```bash
sudo usermod -aG docker $USER
newgrp docker
# أو أعد تسجيل الدخول
```

### **المشكلة: "port already in use"**
```bash
# إيقاف الخدمة التي تستخدم المنفذ
sudo lsof -i :5000
sudo kill -9 PID_NUMBER
```

### **المشكلة: "OpenAI API Error"**
- تأكد من صحة API Key في ملف .env
- تأكد من وجود رصيد في حساب OpenAI

### **المشكلة: "Docker daemon not running"**
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

---

## 📊 **فحص الصحة:**

### **التأكد من عمل المشروع:**
```bash
# فحص الحاويات
docker ps

# فحص السجلات
docker-compose logs badya-chatbot

# اختبار الاتصال
curl http://localhost:5000/api/health
```

### **علامات النجاح:**
```bash
✅ badya-university-chatbot is up and running
✅ Health check: healthy
✅ HTTP response: 200 OK
```

---

## 🎉 **مبروك!**

إذا وصلت لهنا، فالمشروع يعمل بنجاح مع Docker! 

### **المميزات اللي حصلت عليها:**
- ✅ **تثبيت سريع** في دقائق معدودة
- ✅ **بيئة معزولة** وآمنة
- ✅ **إدارة سهلة** بأوامر بسيطة
- ✅ **تحديث آمن** بدون مشاكل
- ✅ **مراقبة متقدمة** للأداء

### **الآن الطلاب يمكنهم:**
- طرح أسئلة عن الجامعة
- استخدام التسجيل الصوتي
- الوصول للنظام 24/7

### **وأنت كمدير:**
- مراقبة الإحصائيات
- إدارة النظام بسهولة
- تحديث المحتوى حسب الحاجة

**🚀 النظام جاهز للاستخدام مع Docker!**
