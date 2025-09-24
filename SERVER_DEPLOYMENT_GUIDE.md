# 🚀 دليل نشر شات بوت جامعة باديا على السيرفر

## 📋 **متطلبات السيرفر:**

### **المتطلبات الأساسية:**
- **نظام التشغيل**: Ubuntu 20.04+ أو CentOS 7+
- **الذاكرة**: 1GB RAM على الأقل (2GB مُوصى به)
- **المساحة**: 5GB مساحة فارغة
- **Python**: 3.8 أو أحدث
- **الإنترنت**: اتصال مستقر

### **المنافذ المطلوبة:**
- **5000**: للتطبيق (يمكن تغييره)
- **80/443**: للوصول العام (اختياري)

---

## 🛠️ **خطوات التثبيت على Ubuntu:**

### **1. تحديث النظام:**
```bash
sudo apt update && sudo apt upgrade -y
```

### **2. تثبيت Python و pip:**
```bash
sudo apt install python3 python3-pip python3-venv git -y
```

### **3. تحميل المشروع:**
```bash
# إنشاء مجلد للمشروع
mkdir ~/chatbot
cd ~/chatbot

# تحميل من GitHub
git clone https://github.com/abdelkhalek-soudy/university-chatbot2.git
cd university-chatbot2
```

### **4. إنشاء البيئة الافتراضية:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### **5. تثبيت المتطلبات:**
```bash
pip install -r requirements.txt
```

### **6. إعداد ملف البيئة:**
```bash
# نسخ ملف المثال
cp .env.example .env

# تحرير الملف وإضافة OpenAI API Key
nano .env
```

**محتوى ملف .env:**
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
SECRET_KEY=your-long-random-secret-key-here
FLASK_ENV=production
HOST=0.0.0.0
PORT=5000
```

### **7. اختبار التشغيل:**
```bash
python app.py
```

### **8. إعداد خدمة النظام (Systemd):**
```bash
sudo nano /etc/systemd/system/badya-chatbot.service
```

**محتوى الملف:**
```ini
[Unit]
Description=Badya University Chatbot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/chatbot/university-chatbot2
Environment=PATH=/home/ubuntu/chatbot/university-chatbot2/venv/bin
ExecStart=/home/ubuntu/chatbot/university-chatbot2/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **9. تفعيل الخدمة:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable badya-chatbot
sudo systemctl start badya-chatbot
sudo systemctl status badya-chatbot
```

---

## 🌐 **إعداد Nginx (اختياري للإنتاج):**

### **1. تثبيت Nginx:**
```bash
sudo apt install nginx -y
```

### **2. إعداد Nginx:**
```bash
sudo nano /etc/nginx/sites-available/badya-chatbot
```

**محتوى الملف:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # أو IP السيرفر

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **3. تفعيل الموقع:**
```bash
sudo ln -s /etc/nginx/sites-available/badya-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 **إعداد SSL (HTTPS):**

### **باستخدام Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 🔥 **إعداد Firewall:**

```bash
# السماح بالمنافذ المطلوبة
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 5000  # التطبيق (اختياري)
sudo ufw enable
```

---

## 📊 **مراقبة النظام:**

### **فحص حالة الخدمة:**
```bash
sudo systemctl status badya-chatbot
```

### **عرض السجلات:**
```bash
sudo journalctl -u badya-chatbot -f
```

### **إعادة تشغيل الخدمة:**
```bash
sudo systemctl restart badya-chatbot
```

---

## 🔄 **تحديث المشروع:**

```bash
cd ~/chatbot/university-chatbot2
git pull origin main
sudo systemctl restart badya-chatbot
```

---

## 🚀 **للسيرفرات الأخرى:**

### **CentOS/RHEL:**
```bash
# استبدال apt بـ yum
sudo yum update -y
sudo yum install python3 python3-pip git -y
# باقي الخطوات نفسها
```

### **Windows Server:**
```powershell
# تحميل Python من python.org
# تحميل Git من git-scm.com
# نفس الخطوات لكن بدون sudo
```

---

## 🎯 **الوصول للنظام:**

بعد التثبيت، النظام سيكون متاح على:

### **بدون Nginx:**
- `http://server-ip:5000`

### **مع Nginx:**
- `http://your-domain.com`
- `https://your-domain.com` (مع SSL)

### **الصفحات المهمة:**
- **بوابة الطلاب**: `/user-portal`
- **لوحة الإدارة**: `/admin`
- **فحص الصحة**: `/api/health`

---

## 🆘 **حل المشاكل الشائعة:**

### **المشكلة: الخدمة لا تعمل**
```bash
sudo systemctl status badya-chatbot
sudo journalctl -u badya-chatbot --no-pager
```

### **المشكلة: منفذ مشغول**
```bash
sudo lsof -i :5000
sudo kill -9 PID_NUMBER
```

### **المشكلة: إذن مرفوض**
```bash
sudo chown -R ubuntu:ubuntu ~/chatbot/
chmod +x ~/chatbot/university-chatbot2/app.py
```

### **المشكلة: OpenAI API لا يعمل**
```bash
# تحقق من ملف .env
cat .env | grep OPENAI_API_KEY
# تأكد من صحة المفتاح
```

---

## 📞 **الدعم الفني:**

### **للمساعدة:**
- تحقق من السجلات أولاً
- تأكد من تشغيل الخدمة
- تحقق من الاتصال بالإنترنت
- تأكد من صحة OpenAI API Key

### **أوامر مفيدة:**
```bash
# حالة النظام
sudo systemctl status badya-chatbot

# السجلات المباشرة
sudo journalctl -u badya-chatbot -f

# اختبار الاتصال
curl http://localhost:5000/api/health

# فحص المنافذ
sudo netstat -tlnp | grep :5000
```

---

## 🎉 **تهانينا!**

النظام الآن يعمل على السيرفر الخاص بك! 

**بيانات الدخول:**
- **المدير**: `admin` / `badya@2024`
- **النظام جاهز للاستخدام الكامل**
