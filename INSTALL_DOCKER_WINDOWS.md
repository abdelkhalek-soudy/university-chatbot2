# 🐳 تثبيت Docker على Windows - دليل خطوة بخطوة

## 📋 **المتطلبات:**
- Windows 10/11 (64-bit)
- 4GB RAM على الأقل
- تفعيل Virtualization في BIOS

---

## 🚀 **الخطوات:**

### **1. تحميل Docker Desktop:**
- اذهب إلى: https://www.docker.com/products/docker-desktop/
- اضغط **"Download for Windows"**
- حمل الملف: `Docker Desktop Installer.exe`

### **2. تثبيت Docker Desktop:**
- شغل الملف المحمل كـ Administrator
- اتبع خطوات التثبيت (اضغط Next في كل شيء)
- **مهم**: اختر "Use WSL 2 instead of Hyper-V" إذا ظهر
- انتظر انتهاء التثبيت (5-10 دقائق)

### **3. إعادة تشغيل الجهاز:**
- أعد تشغيل الكمبيوتر بعد التثبيت

### **4. تشغيل Docker Desktop:**
- افتح Docker Desktop من Start Menu
- انتظر حتى يظهر "Docker Desktop is running"
- قد يطلب منك تسجيل حساب (اختياري)

### **5. اختبار Docker:**
افتح Command Prompt أو PowerShell واكتب:
```cmd
docker --version
docker-compose --version
```

إذا ظهرت الأرقام، يبقى Docker شغال! ✅

---

## 🔧 **إذا واجهت مشاكل:**

### **مشكلة: WSL 2 غير مثبت**
```powershell
# في PowerShell كـ Administrator:
wsl --install
# ثم أعد تشغيل الجهاز
```

### **مشكلة: Virtualization غير مفعل**
- ادخل BIOS/UEFI عند بدء التشغيل
- ابحث عن "Virtualization" أو "VT-x" أو "AMD-V"
- فعله واحفظ

### **مشكلة: Docker لا يبدأ**
- تأكد من تشغيل Docker Desktop
- جرب إعادة تشغيل Docker Desktop
- تأكد من أن Windows مُحدث

---

## ✅ **علامات النجاح:**
- أيقونة Docker في System Tray (جانب الساعة)
- `docker --version` يعطي رقم الإصدار
- Docker Desktop يظهر "Running"

---

## 🎯 **الخطوة التالية:**
بعد تثبيت Docker بنجاح، ستكون جاهز لتشغيل مشروع شات بوت جامعة باديا!
