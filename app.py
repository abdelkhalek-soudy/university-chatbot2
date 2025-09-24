"""
جامعة باديا - نظام الدردشة الذكي
تم تطويره بواسطة: عبدالخالق محمد
حقوق النشر © 2024 - جميع الحقوق محفوظة

هذا الكود ملك حصري لجامعة باديا ويحظر نسخه أو توزيعه بدون إذن كتابي مسبق
"""

from flask import Flask, request, jsonify, send_from_directory, render_template, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_jwt_extended import get_jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os, re, datetime, docx
try:
    import fitz
except ImportError:
    fitz = None
from PIL import Image
import pytesseract
from openai import OpenAI
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import pandas as pd
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
# 🔒 Copyright 2025 Abdelkhalek Soudy. All Rights Reserved.
# This file is part of a proprietary project. Do not copy or redistribute.

# 🔧 تحميل متغيرات البيئة
load_dotenv()

# إعداد المسارات
FRONTEND_BUILD_PATH = os.path.join(os.getcwd(), "frontend", "build")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# قاعدة البيانات (SQLite)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_users_table():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create users table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                email TEXT,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        # Create logs table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                type TEXT NOT NULL,
                username TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        # Create questions_analytics table for tracking question patterns
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS questions_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                question_category TEXT,
                question_keywords TEXT,
                username TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                response_length INTEGER,
                session_id TEXT
            )
            """
        )
        
        # Create admin user if not exists
        cur.execute("SELECT * FROM users WHERE username = ?", (ADMIN_USERNAME,))
        if not cur.fetchone():
            hashed_password = generate_password_hash(ADMIN_PASSWORD)
            cur.execute(
                "INSERT INTO users (name, username, password_hash, role) VALUES (?, ?, ?, ?)",
                ("Admin User", ADMIN_USERNAME, hashed_password, "admin")
            )
            
        conn.commit()
        print("[INFO] Database tables initialized successfully")
        
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

# مفاتيح الأمان
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SECRET_KEY     = os.getenv("SECRET_KEY", "fallback-secret")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "badya@2024")
PDF_PATH       = os.getenv("BADYA_PDF_PATH", "Badya.pdf")
KNOWLEDGE_MAX_CHARS = int(os.getenv("KNOWLEDGE_MAX_CHARS", "50000"))
KNOWLEDGE_SUMMARIZE = os.getenv("KNOWLEDGE_SUMMARIZE", "false").strip().lower() in {"1","true","yes","on"}
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:3000"
]
RATE_LIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")

# إعداد Flask
app = Flask(__name__, static_folder="static", static_url_path="/static", template_folder="templates")
app.config["JWT_SECRET_KEY"] = SECRET_KEY
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)
jwt     = JWTManager(app)
limiter = Limiter(key_func=get_remote_address, storage_uri=RATE_LIMIT_STORAGE_URI)
limiter.init_app(app)

# إنشاء جدول المستخدمين عند بدء التشغيل
init_users_table()

# إعداد pytesseract - مع مسار عام
try:
    # محاولة العثور على tesseract في المسارات الشائعة
    import shutil
    tesseract_path = shutil.which("tesseract")
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    else:
        # مسارات شائعة لـ tesseract
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Users\pc\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
            r"C:\Users\Gateintech\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
        else:
            print("[WARN] Tesseract not found - image text extraction will not work")
except Exception as e:
    print(f"[WARN] Tesseract setup failed: {e}")

# تعيين ترميز UTF-8 للإخراج في ويندوز
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ✅ تلخيص نص باستخدام OpenAI (اختياري)
def summarize_text_if_needed(text, max_tokens=400):
    if not KNOWLEDGE_SUMMARIZE:
        return text
    try:
        prompt = (
            "لخّص النص التالي إلى نقاط مركزة وواضحة باللغة العربية، مع الاحتفاظ بالأرقام، الرسوم، الشروط، التواريخ، وأسماء البرامج والكليات إن وُجدت.\n"
            "حافظ على الدقة وابتعد عن الحشو.\n\n"
            f"النص:\n{text}"
        )
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[WARN] Summarization failed, using original text: {e}")
        return text

# فحص أمان البيانات للتأكد من أنها تخص جامعة باديا فقط
def validate_badya_data(text_content):
    """
    فحص شامل للتأكد من أن البيانات تخص جامعة باديا فقط
    """
    try:
        # الكلمات المطلوبة لجامعة باديا
        required_badya_keywords = [
            "باديا", "badya", "جامعة باديا", "badya university",
            "memphis", "ممفيس"  # لأن جامعة باديا مرتبطة بجامعة ممفيس
        ]
        
        # الكلمات المحظورة (جامعات أخرى)
        forbidden_keywords = [
            "الأزهر", "القاهرة", "عين شمس", "الإسكندرية", "أسيوط", "المنصورة", 
            "الزقازيق", "طنطا", "المنوفية", "قناة السويس", "بنها", "الفيوم",
            "جنوب الوادي", "أسوان", "سوهاج", "المنيا", "بني سويف", "دمياط",
            "كفر الشيخ", "مطروح", "العريش", "الوادي الجديد", "حلوان", "التكنولوجيا",
            "الألمانية", "الأمريكية", "البريطانية", "الفرنسية", "الروسية",
            "harvard", "mit", "stanford", "oxford", "cambridge", "yale",
            "الجامعة الأمريكية", "الجامعة الألمانية", "الجامعة البريطانية"
        ]
        
        text_lower = text_content.lower()
        
        # فحص وجود كلمات باديا المطلوبة
        badya_found = any(keyword.lower() in text_lower for keyword in required_badya_keywords)
        
        if not badya_found:
            return False, "البيانات لا تحتوي على معلومات جامعة باديا المطلوبة"
        
        # فحص عدم وجود كلمات محظورة (جامعات أخرى) - فحص ذكي
        forbidden_found = []
        for forbidden in forbidden_keywords:
            if forbidden.lower() in text_lower:
                forbidden_found.append(forbidden)
        
        # إذا وُجدت كلمات محظورة، استخدم GPT للفحص الذكي
        if forbidden_found:
            print(f"[SECURITY INFO] Found potentially forbidden keywords: {forbidden_found}")
            print("[SECURITY INFO] Using GPT for smart context analysis...")
            # استخدام GPT للفحص الذكي - يقبل السياق الإيجابي لباديا
            gpt_result = validate_with_gpt(text_content)
            if not gpt_result[0]:
                print(f"[SECURITY ERROR] GPT validation failed: {gpt_result[1]}")
                return False, f"البيانات تحتوي على معلومات جامعات أخرى غير مناسبة: {gpt_result[1]}"
            else:
                print(f"[SECURITY OK] GPT approved data with context: {gpt_result[1]}")
                return True, gpt_result[1]
        
        # فحص إضافي باستخدام GPT للتأكد
        return validate_with_gpt(text_content)
        
    except Exception as e:
        print(f"[ERROR] Data validation failed: {e}")
        return False, f"خطأ في فحص البيانات: {str(e)}"

def validate_with_gpt(text_content):
    """
    فحص إضافي باستخدام GPT للتأكد من أن البيانات تخص جامعة باديا
    """
    try:
        # أخذ عينة من النص للفحص (أول 2000 حرف)
        sample_text = text_content[:2000]
        
        prompt = f"""
فحص البيانات التالية وحدد ما إذا كانت تخص جامعة باديا (Badya University) بشكل أساسي أم لا.

البيانات:
{sample_text}

قواعد الفحص الذكية:
1. يجب أن تحتوي البيانات على معلومات عن جامعة باديا أو Badya University كموضوع أساسي
2. اقبل البيانات إذا ذُكرت جامعات أخرى في سياق إيجابي لجامعة باديا مثل:
   - "باديا تقبل طلاب من الأزهر"
   - "تحويل من القاهرة إلى باديا" 
   - "باديا أفضل من الجامعة الأمريكية"
   - "خريج جامعة القاهرة يدرس في باديا"
3. اقبل البيانات إذا ذُكرت جامعات أخرى كمرجع أو مقارنة لصالح باديا
4. ارفض فقط إذا كانت البيانات تتحدث عن جامعة أخرى كموضوع أساسي وليس باديا
5. ارفض إذا كانت البيانات دليل أو كتالوج لجامعة أخرى

أجب بـ "valid" إذا كانت البيانات تخص جامعة باديا بشكل أساسي (حتى لو ذُكرت جامعات أخرى في سياق إيجابي)
أجب بـ "invalid" إذا كانت البيانات تتحدث عن جامعة أخرى كموضوع أساسي
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().lower()
        
        if "valid" in result:
            return True, "البيانات صحيحة وتخص جامعة باديا"
        else:
            return False, "البيانات لا تخص جامعة باديا أو تحتوي على معلومات جامعات أخرى"
            
    except Exception as e:
        print(f"[ERROR] GPT validation failed: {e}")
        return False, f"خطأ في فحص البيانات بواسطة الذكاء الاصطناعي: {str(e)}"

# تحميل المعرفة من ملف Excel المحدد في BADYA_PDF_PATH مع فحص الأمان
def load_knowledge_from_excel(path):
    try:
        if not path or not os.path.exists(path):
            print(f"[WARN] Excel file not found or not specified: {path}")
            return ""
        
        # محاولة قراءة الملف بمحركات مختلفة
        print(f"[INFO] Attempting to load Excel file: {path}")
        
        # Try reading directly with pandas
        try:
            # First try with openpyxl for .xlsx files
            if path.endswith('.xlsx'):
                df_all = pd.read_excel(path, engine='openpyxl', sheet_name=None)
            else:
                # For .xls files, try xlrd
                df_all = pd.read_excel(path, engine='xlrd', sheet_name=None)
            
            frames = []
            for sheet_name, df in df_all.items():
                # تحويل الداتا إلى نص قابل للإرسال للموديل
                sheet_text = df.fillna("").astype(str).to_csv(index=False, sep='\t')
                # تلخيص اختياري
                if KNOWLEDGE_SUMMARIZE:
                    sheet_text_summary = summarize_text_if_needed(sheet_text)
                else:
                    sheet_text_summary = sheet_text
                frames.append(f"=== {sheet_name} ===\n{sheet_text_summary}")
            
            text = "\n\n".join(frames)
            
            # 🔒 فحص أمان البيانات قبل التحميل
            print("[INFO] Validating data security for Badya University...")
            is_valid, validation_message = validate_badya_data(text)
            
            if not is_valid:
                print(f"[SECURITY ERROR] Data validation failed: {validation_message}")
                raise SecurityError(f"رفض تحميل البيانات: {validation_message}")
            
            print(f"[SECURITY OK] Data validation passed: {validation_message}")
            
            # تحديد حد أقصى للحجم لتجنب تجاوز الذاكرة/التوكنز
            if len(text) > KNOWLEDGE_MAX_CHARS:
                text = text[:KNOWLEDGE_MAX_CHARS]
            print(f"[OK] Loaded Excel knowledge ({len(text)} chars) from: {path} | summarize={KNOWLEDGE_SUMMARIZE} | limit={KNOWLEDGE_MAX_CHARS}")
            return text
            
        except SecurityError as se:
            print(f"[SECURITY ERROR] {se}")
            raise se
        except Exception as e:
            print(f"[ERROR] Failed to read Excel file: {e}")
            return ""
        
    except SecurityError as se:
        raise se
    except Exception as e:
        print(f"[ERROR] Excel load failed: {e}")
        return ""

# تعريف استثناء الأمان
class SecurityError(Exception):
    pass

# يتم التحميل عند تشغيل السيرفر مع معالجة أخطاء الأمان
try:
    KNOWLEDGE_TEXT = load_knowledge_from_excel(PDF_PATH)
    print(f"[SECURITY OK] Knowledge loaded successfully with security validation")
except SecurityError as se:
    print(f"[SECURITY WARNING] {se}")
    print("[SECURITY WARNING] Starting server without knowledge base - please load valid Badya University data")
    KNOWLEDGE_TEXT = ""
except Exception as e:
    print(f"[ERROR] Failed to load knowledge: {e}")
    KNOWLEDGE_TEXT = ""

# ✅ فلترة الذكاء الاصطناعي للتأكد من ارتباط النص بالجامعة
def _contains_university_keywords(text: str) -> bool:
    try:
        t = (text or "").lower()
        keywords = [
            "badya", "university", "جامعة", "باديا", "كلية", "كليه", "قسم", "تخصص", "تخصصات",
            "المصاريف", "مصروفات", "رسوم", "قبول", "التقديم", "تسجيل", "نتيجة", "نتائج",
            "محاضرة", "محاضرات", "امتحان", "امتحانات", "مواد", "مقررات", "منحة", "المنح",
            "سكن", "سكن جامعي", "دراسة", "دراسات", "بكالوريوس", "ماجستير", "دكتوراه", "كلية",
        ]
        return any(k in t for k in keywords)
    except Exception:
        return False


        # المستوى 1: فحص النصوص القصيرة
        if len(text) < 3:
            print(f"[DEBUG] Text too short: '{text}'")
            return "no"
        
        # المستوى 2: فحص الكلمات المشبوهة والسبام
        spam_keywords = [
            'اشتركوا', 'لايك', 'subscribe', 'اشترك', 'القناة', 'الفيديو', 
            'شير', 'كومنت', 'بيل', 'نوتيفيكيشن', 'تفعيل', 'الجرس', 
            'فولو', 'follow', 'like', 'share', 'بل', 'نوتيف', 'شيير', 'كمنت'
        ]
        
        text_lower = text.lower()
        for spam_word in spam_keywords:
            if spam_word in text_lower:
                print(f"[DEBUG] Found unclear/spam pattern '{spam_word}' in text: '{text}'")
                return "no"
        
        # المستوى 3: فحص أسماء الجامعات المحظورة في السؤال
        forbidden_universities = [
            "جامعة القاهرة", "جامعة الأزهر", "جامعة عين شمس", "جامعة الإسكندرية",
            "جامعة أسيوط", "جامعة المنصورة", "جامعة الزقازيق", "جامعة طنطا",
            "الجامعة الأمريكية", "الجامعة الألمانية", "الجامعة البريطانية",
            "cairo university", "al-azhar university", "ain shams university",
            "american university", "german university", "british university"
        ]
        
        for forbidden_uni in forbidden_universities:
            if forbidden_uni in text_lower:
                print(f"[DEBUG] Found forbidden university in question: '{forbidden_uni}'")
                return "no"
        
        # المستوى 4: فحص النصوص المشوشة (أحرف غريبة)
        weird_chars = sum(1 for c in text if not (c.isalnum() or c.isspace() or c in '.,!?؟،؛:'))
        if weird_chars > len(text) * 0.3:  # أكثر من 30% أحرف غريبة
            print(f"[DEBUG] Too many weird characters: {weird_chars}/{len(text)}")
            return "no"
        
        # المستوى 5: فحص الكلمات المفتاحية الجامعية
        university_keywords = [
            "badya", "باديا", "جامعة", "university", "كلية", "كليه", "قسم", "تخصص", "تخصصات",
            "المصاريف", "مصروفات", "رسوم", "إدارية", "إداري", "قبول", "التقديم", "تسجيل", "نتيجة", "نتائج",
            "محاضرة", "محاضرات", "امتحان", "امتحانات", "مواد", "مقررات", "منحة", "المنح",
            "سكن", "سكن جامعي", "دراسة", "دراسات", "بكالوريوس", "ماجستير", "دكتوراه",
            "طلاب", "طالب", "طالبة", "أستاذ", "دكتور", "معيد", "هندسة", "طب", "صيدلة",
            "حاسوب", "إدارة", "اقتصاد", "حقوق", "آداب", "علوم", "تربية", "فنون",
            "التخرج", "شهادة", "دبلوم", "ماستر", "دكتوراة", "بحث", "رسالة", "مشروع"
        ]
        
        has_university_keyword = any(keyword in text_lower for keyword in university_keywords)
        
        if not has_university_keyword:
            print(f"[DEBUG] No university keywords found in: '{text}'")
            # المستوى 6: فحص GPT الذكي للتأكد
            return check_with_gpt(text)
        
        print(f"[DEBUG] University keywords found, text accepted: '{text[:50]}...'")
        return "yes"
        
    except Exception as e:
        print(f"[ERROR] Error in is_related_to_university: {e}")
        return "no"

def check_with_gpt(text):
    """
    فحص GPT محسن للتأكد من وجود سؤال حقيقي عن الجامعة
    """
    try:
        prompt = f"""
هل النص التالي يحتوي على سؤال واضح ومحدد عن جامعة باديا أو التعليم الجامعي؟

النص: "{text}"

قواعد التصنيف الصارمة:
- يجب أن يكون هناك سؤال واضح ومفهوم
- يجب أن يكون السؤال متعلق بالجامعة أو التعليم
- ارفض العبارات غير المفهومة أو المشوشة
- ارفض الكلمات المفردة أو العبارات القصيرة غير الواضحة
- ارفض أي محتوى يبدو كسبام أو غير مفيد

أجب بـ "yes" فقط إذا كان سؤالاً واضحاً عن الجامعة، وإلا أجب بـ "no"
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().lower()
        print(f"[DEBUG] GPT classification result: '{result}' for text: '{text}'")
        
        return "yes" if "yes" in result else "no"
        
    except Exception as e:
        print(f"[ERROR] GPT classification failed: {e}")
        return "no"

def analyze_question_category(question_text):
    """
    تحليل وتصنيف السؤال إلى فئات مختلفة
    """
    try:
        prompt = f"""
صنف السؤال التالي إلى إحدى الفئات الرئيسية لجامعة باديا:

السؤال: "{question_text}"

الفئات المتاحة:
1. القبول والتسجيل
2. المصاريف والرسوم
3. الكليات والتخصصات
4. المواد والمناهج
5. الامتحانات والدرجات
6. السكن الجامعي
7. المنح والدعم المالي
8. الأنشطة الطلابية
9. الخدمات الجامعية
10. أخرى

أجب بالفئة فقط (مثل: "القبول والتسجيل")
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=20
        )
        
        category = response.choices[0].message.content.strip()
        return category
        
    except Exception as e:
        print(f"[ERROR] Question categorization failed: {e}")
        return "أخرى"

def extract_question_keywords(question_text):
    """
    استخراج الكلمات المفتاحية من السؤال
    """
    try:
        # كلمات مفتاحية شائعة في الأسئلة الجامعية
        university_keywords = [
            "باديا", "جامعة", "كلية", "قسم", "تخصص", "مصاريف", "رسوم", "قبول", 
            "تسجيل", "امتحان", "درجات", "مواد", "منحة", "سكن", "دراسة", "طلاب",
            "بكالوريوس", "ماجستير", "دكتوراه", "هندسة", "طب", "صيدلة", "حاسوب",
            "إدارة", "اقتصاد", "حقوق", "آداب", "علوم", "تربية", "فنون"
        ]
        
        text_lower = question_text.lower()
        found_keywords = []
        
        for keyword in university_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return ", ".join(found_keywords[:5])  # أول 5 كلمات مفتاحية
        
    except Exception as e:
        print(f"[ERROR] Keyword extraction failed: {e}")
        return ""

def log_question_analytics(question_text, username, response_length=0):
    """
    تسجيل تحليلات السؤال في قاعدة البيانات
    """
    try:
        category = analyze_question_category(question_text)
        keywords = extract_question_keywords(question_text)
        session_id = f"{username}_{datetime.datetime.now().strftime('%Y%m%d_%H')}"
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO questions_analytics 
            (question_text, question_category, question_keywords, username, response_length, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (question_text[:500], category, keywords, username, response_length, session_id))
        conn.commit()
        conn.close()
        
        print(f"[INFO] Question analytics logged: {category}")
        
    except Exception as e:
        print(f"[ERROR] Failed to log question analytics: {e}")

def is_related_to_university(text):
    """
    فحص متعدد المستويات للتأكد من ارتباط النص بجامعة باديا فقط
    """
    try:
        # المستوى 1: فحص النصوص القصيرة
        if len(text) < 3:
            print(f"[DEBUG] Text too short: '{text}'")
            return "no"
        
        # المستوى 2: فحص أسماء الجامعات المحظورة في السؤال
        forbidden_universities = [
            "جامعة القاهرة", "جامعة الأزهر", "جامعة عين شمس", "جامعة الإسكندرية",
            "جامعة أسيوط", "جامعة المنصورة", "جامعة الزقازيق", "جامعة طنطا",
            "الجامعة الأمريكية", "الجامعة الألمانية", "الجامعة البريطانية",
            "cairo university", "al-azhar university", "ain shams university",
            "american university", "german university", "british university"
        ]
        
        text_lower = text.lower()
        for forbidden_uni in forbidden_universities:
            if forbidden_uni in text_lower:
                print(f"[DEBUG] Found forbidden university in question: '{forbidden_uni}'")
                return "no"
        
        # المستوى 3: فحص الكلمات المفتاحية الجامعية
        university_keywords = [
            "badya", "باديا", "جامعة", "university", "كلية", "كليه", "قسم", "تخصص", "تخصصات",
            "المصاريف", "مصروفات", "رسوم", "إدارية", "إداري", "قبول", "التقديم", "تسجيل", "نتيجة", "نتائج",
            "محاضرة", "محاضرات", "امتحان", "امتحانات", "مواد", "مقررات", "منحة", "المنح",
            "سكن", "سكن جامعي", "دراسة", "دراسات", "بكالوريوس", "ماجستير", "دكتوراه",
            "طلاب", "طالب", "طالبة", "أستاذ", "دكتور", "معيد", "هندسة", "طب", "صيدلة",
            "حاسوب", "إدارة", "اقتصاد", "حقوق", "آداب", "علوم", "تربية", "فنون",
            "التخرج", "شهادة", "دبلوم", "ماستر", "دكتوراة", "بحث", "رسالة", "مشروع"
        ]
        
        has_university_keyword = any(keyword in text_lower for keyword in university_keywords)
        
        if not has_university_keyword:
            print(f"[DEBUG] No university keywords found in: '{text}'")
            return "no"
        
        print(f"[DEBUG] University keywords found, text accepted: '{text[:50]}...'")
        return "yes"
        
    except Exception as e:
        print(f"[ERROR] Error in is_related_to_university: {e}")
        return "no"

# ✅ الرد الذكي
def ask_gpt(msg, username="مجهول"):
    try:
        print(f"[DEBUG] ask_gpt called with message: '{msg}', username: '{username}'")
        
        # فلترة الأسئلة للتأكد من ارتباطها بجامعة باديا فقط
        relation = is_related_to_university(msg)
        print(f"[DEBUG] Relation result: {relation}")
        
        if relation == "no":
            print("[DEBUG] Question rejected by filter")
            return "عذراً، أنا مساعد ذكي متخصص في الإجابة على الأسئلة المتعلقة بجامعة باديا فقط. يرجى طرح سؤال واضح ومحدد عن الجامعة، الكليات، المصاريف، التسجيل، أو أي موضوع أكاديمي متعلق بالجامعة."
        
        system_prompt = (
            "أنت مساعد ذكي متخصص في جامعة باديا فقط. "
            "قواعد صارمة يجب اتباعها: "
            "1. أجب فقط عن الأسئلة المتعلقة بجامعة باديا (Badya University) "
            "2. إذا سُئلت عن أي جامعة أخرى (مثل القاهرة، الأزهر، عين شمس، الأمريكية، إلخ) ارفض الإجابة تماماً "
            "3. قل: 'عذراً، أنا متخصص في جامعة باديا فقط ولا أستطيع الإجابة عن جامعات أخرى' "
            "4. استخدم فقط المعلومات المتوفرة في قاعدة البيانات عن جامعة باديا "
            "5. لا تستخدم معرفتك العامة عن جامعات أخرى أبداً "
            "أجب باللغة العربية بشكل واضح ومفصل عن جامعة باديا فقط."
        )
        
        # نضيف معرفة من ملف الإكسل إذا كانت متاحة
        kb_message = []
        if KNOWLEDGE_TEXT:
            kb_message = [{
                "role": "system",
                "content": f"قاعدة بيانات جامعة باديا:\n{KNOWLEDGE_TEXT}\n\nاستخدم هذه المعلومات للإجابة على الأسئلة."
            }]

        print("[DEBUG] Calling OpenAI GPT...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                *kb_message,
                {"role": "user", "content": msg}
            ],
            temperature=0.2,
            max_tokens=800
        )
        
        answer = response.choices[0].message.content.strip()
        print(f"[DEBUG] GPT response received: '{answer[:100]}...'")
        
        # تسجيل تحليلات السؤال فقط للأسئلة المقبولة
        if relation == "yes":
            log_question_analytics(msg, username, len(answer))
        
        print(f"[DEBUG] Returning answer: '{answer[:50]}...'")
        return answer
        
    except Exception as e:
        error_msg = f"[ERROR] خطأ في النظام: {str(e)}"
        print(error_msg)
        return error_msg

# ✅ إعادة تحميل المعرفة بدون إعادة تشغيل السيرفر
def _require_admin():
    try:
        claims = get_jwt()
        if not claims or claims.get("role") != "admin":
            return False
        return True
    except Exception:
        return False

@app.route("/api/reload-knowledge", methods=["POST"])
@jwt_required()
def reload_knowledge():
    if not _require_admin():
        return jsonify({"error": "غير مصرح للمستخدم"}), 403
    
    global KNOWLEDGE_TEXT, PDF_PATH, KNOWLEDGE_MAX_CHARS, KNOWLEDGE_SUMMARIZE
    
    try:
        data = request.get_json(silent=True) or {}
        
        # حفظ البيانات القديمة في حالة الفشل
        old_knowledge = KNOWLEDGE_TEXT
        old_path = PDF_PATH
        
        # السماح بتغيير المسار والخيارات في الطلب أو عبر .env
        new_path = data.get("path") or os.getenv("BADYA_PDF_PATH", PDF_PATH)
        PDF_PATH = new_path
        
        if "KNOWLEDGE_MAX_CHARS" in data:
            try:
                KNOWLEDGE_MAX_CHARS = int(data["KNOWLEDGE_MAX_CHARS"]) 
            except Exception:
                pass
        env_max = os.getenv("KNOWLEDGE_MAX_CHARS")
        if env_max:
            try:
                KNOWLEDGE_MAX_CHARS = int(env_max)
            except Exception:
                pass
        if "KNOWLEDGE_SUMMARIZE" in data:
            KNOWLEDGE_SUMMARIZE = str(data["KNOWLEDGE_SUMMARIZE"]).strip().lower() in {"1","true","yes","on"}
        else:
            KNOWLEDGE_SUMMARIZE = os.getenv("KNOWLEDGE_SUMMARIZE", "false").strip().lower() in {"1","true","yes","on"}

        # محاولة تحميل البيانات الجديدة مع فحص الأمان
        try:
            new_knowledge = load_knowledge_from_excel(PDF_PATH)
            KNOWLEDGE_TEXT = new_knowledge
            
            return jsonify({
                "status": "ok",
                "path": PDF_PATH,
                "summarize": KNOWLEDGE_SUMMARIZE,
                "limit": KNOWLEDGE_MAX_CHARS,
                "chars": len(KNOWLEDGE_TEXT) if KNOWLEDGE_TEXT else 0,
                "security_status": "تم فحص البيانات بنجاح - البيانات تخص جامعة باديا فقط"
            })
            
        except SecurityError as se:
            # استعادة البيانات القديمة في حالة فشل الأمان
            KNOWLEDGE_TEXT = old_knowledge
            PDF_PATH = old_path
            
            return jsonify({
                "error": f"🔒 خطأ أمان: {str(se)}",
                "security_error": True,
                "message": "تم رفض تحميل البيانات لأنها لا تخص جامعة باديا. البيانات القديمة محفوظة."
            }), 400
            
        except Exception as e:
            # استعادة البيانات القديمة في حالة أي خطأ آخر
            KNOWLEDGE_TEXT = old_knowledge
            PDF_PATH = old_path
            
            return jsonify({
                "error": f"خطأ في تحميل البيانات: {str(e)}",
                "message": "فشل تحميل البيانات. البيانات القديمة محفوظة."
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": f"خطأ عام: {str(e)}"
        }), 500

# ✅ وظائف الملفات
def read_pdf(p): 
    if fitz is None:
        return "PDF reading not available - PyMuPDF not installed"
    return "".join(page.get_text() for page in fitz.open(p))
def read_docx(p): return "\n".join(para.text for para in docx.Document(p).paragraphs)
def clean_text(t):
    t = re.sub(r'\\[a-z]+\d*','',t)
    t = re.sub(r'{\\.*?}','',t)
    return re.sub(r'\n+','\n',t).strip()
def read_rtf(p): return clean_text(open(p,'r',errors='ignore').read())
def read_image(p):
    text = pytesseract.image_to_string(Image.open(p), lang='eng+ara')
    # print("📄 النص المستخرج من الصورة:", text)  # تم تعطيل الطباعة لتجنب مشاكل الترميز
    return text
def transcribe_audio(path):
    try:
        print(f"[INFO] Starting audio transcription for: {path}")
        
        # التحقق من وجود الملف وحجمه
        if not os.path.exists(path):
            print(f"[ERROR] Audio file not found: {path}")
            return "[ERROR] Audio file not found"
        
        file_size = os.path.getsize(path)
        print(f"[INFO] Audio file size: {file_size} bytes")
        
        if file_size < 100:  # أقل من 100 bytes يعتبر فارغ تقريباً
            print("[ERROR] Audio file too small (virtually empty)")
            return "[ERROR] Audio file too small - may be empty or corrupted"
        
        if file_size > 25 * 1024 * 1024:  # أكبر من 25MB
            print("[ERROR] Audio file too large")
            return "[ERROR] Audio file too large - maximum 25MB allowed"
        
        # التحقق من وجود OpenAI client
        if not client:
            print("[ERROR] OpenAI client not initialized")
            return "[ERROR] OpenAI client not available"
        
        # فحص إذا كان الملف WebM وحجمه صغير - قد يحتاج معالجة خاصة
        file_ext = os.path.splitext(path)[1].lower()
        if file_ext == '.webm' and file_size < 5000:  # أقل من 5KB
            print(f"[INFO] Small WebM file detected ({file_size} bytes) - applying special handling")
        
        # تحويل الملف إلى تنسيق مدعوم إذا لزم الأمر
        converted_path = convert_audio_format(path)
        if converted_path != path:
            print(f"[INFO] Audio converted to: {converted_path}")
            path = converted_path
        
        # محاولة متعددة مع إعدادات مختلفة
        attempts = [
            # المحاولة الأولى: عربية مع prompt قوي
            {
                "language": "ar",
                "prompt": "مرحبا، أنا طالب أريد أن أسأل عن جامعة باديا. ما هي المصاريف والكليات المتاحة؟ شكرا لك.",
                "temperature": 0
            },
            # المحاولة الثانية: عربية بدون prompt
            {
                "language": "ar",
                "prompt": None,
                "temperature": 0
            },
            # المحاولة الثالثة: بدون تحديد لغة
            {
                "language": None,
                "prompt": None,
                "temperature": 0.1
            },
            # المحاولة الرابعة: إنجليزية (للكلمات الإنجليزية المختلطة)
            {
                "language": "en",
                "prompt": None,
                "temperature": 0.2
            }
        ]
        
        last_error = None
        transcribed_text = ""
        
        for i, attempt in enumerate(attempts):
            try:
                print(f"[INFO] Transcription attempt {i+1}/4 with language: {attempt.get('language', 'auto')}")
                
                with open(path, "rb") as f:
                    # قراءة محتوى الملف
                    file_content = f.read()
                    
                    # إنشاء اسم الملف مع التنسيق الصحيح
                    file_name = os.path.basename(path)
                    file_ext = os.path.splitext(file_name)[1].lower()
                    
                    # تحديد التنسيق المناسب لـ Whisper
                    if file_ext == '.webm':
                        # تحويل WebM إلى اسم ملف بتنسيق مقبول
                        file_name = f"{os.path.splitext(file_name)[0]}.webm"
                        mime_type = 'audio/webm'
                    elif file_ext == '.wav':
                        file_name = f"{os.path.splitext(file_name)[0]}.wav"
                        mime_type = 'audio/wav'
                    elif file_ext == '.mp3':
                        file_name = f"{os.path.splitext(file_name)[0]}.mp3"
                        mime_type = 'audio/mpeg'
                    elif file_ext == '.m4a':
                        file_name = f"{os.path.splitext(file_name)[0]}.m4a"
                        mime_type = 'audio/mp4'
                    else:
                        # افتراضي: WAV
                        file_name = f"{os.path.splitext(file_name)[0]}.wav"
                        mime_type = 'audio/wav'
                    
                    # إنشاء BytesIO object للملف
                    from io import BytesIO
                    file_obj = BytesIO(file_content)
                    file_obj.name = file_name
                    
                    params = {
                        "model": "whisper-1",
                        "file": file_obj,
                        "response_format": "text",
                        "temperature": attempt.get("temperature", 0)
                    }
                    
                    if attempt["language"]:
                        params["language"] = attempt["language"]
                    if attempt["prompt"]:
                        params["prompt"] = attempt["prompt"]
                    
                    print(f"[INFO] Sending request to OpenAI Whisper with file: {file_name}, type: {mime_type}, size: {os.path.getsize(path)} bytes")
                    result = client.audio.transcriptions.create(**params)
                    transcribed_text = result.strip() if hasattr(result, 'strip') else str(result).strip()
                    
                    try:
                        print(f"[INFO] Transcription result length: {len(transcribed_text)}")
                    except:
                        pass
                    
                    # فحص جودة النتيجة
                    if len(transcribed_text) >= 2:
                        # فحص إذا كان النص يحتوي على أحرف عربية أو إنجليزية مفيدة
                        arabic_chars = sum(1 for c in transcribed_text if '\u0600' <= c <= '\u06FF')
                        english_chars = sum(1 for c in transcribed_text if c.isalpha() and c.isascii())
                        
                        if arabic_chars > 0 or english_chars > 2:
                            print(f"[SUCCESS] Good transcription found: Arabic chars: {arabic_chars}, English chars: {english_chars}")
                            return transcribed_text
                        
            except Exception as e:
                last_error = str(e)
                error_details = str(e)
                
                # تحليل نوع الخطأ لإعطاء رسائل أكثر وضوحاً
                if "could not be decoded" in error_details.lower():
                    print(f"[WARN] Attempt {i+1}: Audio format not supported - {error_details}")
                elif "invalid_request_error" in error_details.lower():
                    print(f"[WARN] Attempt {i+1}: Invalid request format - {error_details}")
                elif "file" in error_details.lower() and "size" in error_details.lower():
                    print(f"[WARN] Attempt {i+1}: File size issue - {error_details}")
                else:
                    print(f"[WARN] Attempt {i+1}: General error - {error_details}")
                
                continue
        
        # إذا فشلت كل المحاولات
        if transcribed_text and len(transcribed_text) > 0:
            try:
                print(f"[INFO] Returning transcription with length: {len(transcribed_text)}")
            except:
                pass
            return transcribed_text
        
        # رسالة خطأ واضحة للمستخدم
        if "could not be decoded" in str(last_error).lower():
            error_msg = "[ERROR] خطأ في تنسيق الملف الصوتي. يرجى التحدث لفترة أطول (3-5 ثوان على الأقل) أو التأكد من جودة الميكروفون."
        elif "invalid_request_error" in str(last_error).lower():
            error_msg = "[ERROR] مشكلة في إرسال الملف الصوتي. يرجى المحاولة مرة أخرى."
        else:
            error_msg = f"[ERROR] خطأ في معالجة الصوت: {last_error}"
        
        print(f"[ERROR] All transcription attempts failed. Last error: {last_error}")
        return error_msg
        
    except Exception as e:
        error_msg = f"[ERROR] Whisper transcription failed: {str(e)}"
        print(error_msg)
        return error_msg
    finally:
        # تنظيف الملف المحول إذا كان مختلفاً عن الأصلي
        if 'converted_path' in locals() and converted_path != path and os.path.exists(converted_path):
            try:
                os.remove(converted_path)
                print(f"[INFO] Cleaned up converted file: {converted_path}")
            except Exception as e:
                print(f"[WARN] Failed to clean up converted file: {e}")

def convert_audio_format(input_path):
    """تحويل الملف الصوتي إلى تنسيق مدعوم من Whisper"""
    try:
        # التحقق من امتداد الملف
        file_ext = os.path.splitext(input_path)[1].lower()
        
        # التنسيقات المدعومة مباشرة من Whisper
        supported_formats = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
        
        # فحص حجم الملف أولاً
        file_size = os.path.getsize(input_path)
        print(f"[INFO] Original file size: {file_size} bytes, format: {file_ext}")
        
        # معالجة خاصة لملفات WebM الصغيرة
        if file_ext == '.webm' and file_size < 5000:  # أقل من 5KB
            print(f"[WARN] Small WebM file detected ({file_size} bytes) - may need conversion")
            # لا نعيد الملف مباشرة، بل نحاول التحويل
        elif file_ext in supported_formats and file_size > 1000:  # أكبر من 1KB
            print(f"[INFO] File format {file_ext} is supported and size is good")
            return input_path
        
        # إنشاء مسار الملف المحول
        base_name = os.path.splitext(input_path)[0]
        output_path = base_name + '.wav'
        
        print(f"[INFO] Converting {file_ext} to .wav format...")
        
        # محاولة تحويل بسيط باستخدام Python
        try:
            import wave
            import struct
            
            # قراءة الملف الأصلي كبيانات خام
            with open(input_path, 'rb') as f:
                audio_data = f.read()
            
            # إنشاء ملف WAV بسيط
            with wave.open(output_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # أحادي
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                
                # تحويل البيانات إلى تنسيق WAV
                # هذا تحويل بسيط - قد لا يعمل مع جميع التنسيقات
                if len(audio_data) > 44:  # تجاهل header إذا وجد
                    audio_data = audio_data[44:]
                
                wav_file.writeframes(audio_data)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"[SUCCESS] Audio converted successfully to: {output_path}")
                return output_path
            else:
                print("[WARN] Simple conversion failed")
                
        except Exception as e:
            print(f"[WARN] Simple conversion failed: {e}")
        
        # محاولة استخدام ffmpeg للتحويل
        try:
            import subprocess
            subprocess.run([
                'ffmpeg', '-i', input_path, 
                '-acodec', 'pcm_s16le', 
                '-ar', '16000', 
                '-ac', '1', 
                '-y', output_path
            ], check=True, capture_output=True, timeout=30)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"[SUCCESS] FFmpeg conversion successful: {output_path}")
                return output_path
            else:
                print("[WARN] FFmpeg conversion failed - output file is empty")
                
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"[WARN] FFmpeg conversion failed: {e}")
        
        # إذا فشل التحويل، جرب إنشاء ملف WAV بسيط
        try:
            print("[INFO] Creating simple WAV file...")
            create_simple_wav(input_path, output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                return output_path
        except Exception as e:
            print(f"[WARN] Simple WAV creation failed: {e}")
        
        print("[INFO] All conversion attempts failed, using original file")
        return input_path
            
    except Exception as e:
        print(f"[WARN] Audio conversion error: {e}")
        return input_path

def create_simple_wav(input_path, output_path):
    """إنشاء ملف WAV بسيط من البيانات الخام"""
    import wave
    import struct
    
    # قراءة البيانات الأصلية
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # إنشاء ملف WAV
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(1)      # أحادي
        wav_file.setsampwidth(2)      # 16-bit
        wav_file.setframerate(16000)  # 16kHz
        
        # تحويل البيانات إلى 16-bit samples
        if len(data) % 2 != 0:
            data += b'\x00'  # إضافة byte إذا كان العدد فردي
        
        # كتابة البيانات
        wav_file.writeframes(data)

def get_mime_type(file_path):
    """تحديد نوع MIME للملف الصوتي"""
    ext = os.path.splitext(file_path)[1].lower()
    mime_types = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4',
        '.mp4': 'audio/mp4',
        '.webm': 'audio/webm',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac'
    }
    return mime_types.get(ext, 'audio/wav')

# --- API ---

@app.route("/api/health", methods=["GET"])
def health_check():
    """فحص حالة الخادم"""
    return jsonify({
        "status": "ok",
        "message": "Server is running",
        "timestamp": datetime.datetime.now().isoformat()
    }), 200

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    # Basic validation
    if not name or not username or not password:
        return jsonify({"error": "يرجى إدخال الاسم واسم المستخدم وكلمة المرور"}), 400
    if len(password) < 6:
        return jsonify({"error": "كلمة المرور يجب أن تكون 6 أحرف على الأقل"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            return jsonify({"error": "اسم المستخدم مستخدم بالفعل"}), 409

        pwd_hash = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (name, username, email, password_hash, role) VALUES (?, ?, ?, ?, 'user')",
            (name, username, email, pwd_hash)
        )
        conn.commit()
        # Auto-login after signup
        claims = {"role": "user"}
        token = create_access_token(identity=username, additional_claims=claims, expires_delta=datetime.timedelta(hours=8))
        return jsonify({
            "status": "ok",
            "access_token": token,
            "student_name": name,
            "role": "user"
        }), 201
    except Exception as e:
        print("[ERROR] signup:", e)
        return jsonify({"error": "تعذر إنشاء الحساب حالياً"}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    # Admin login (env-based) - مخصص للوحة التحكم الادمن
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        claims = {"role": "admin"}
        token = create_access_token(identity=username, additional_claims=claims, expires_delta=datetime.timedelta(hours=8))
        # دعم الصفحة الجديدة والقديمة معاً
        return jsonify({
            "success": True,
            "message": "تم تسجيل الدخول بنجاح",
            "access_token": token, 
            "student_name": username, 
            "role": "admin",
            "token": token,
            "user": {"name": "Administrator", "username": username}
        })

    # Normal users (from DB)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, username, password_hash, role FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "بيانات الدخول خاطئة"}), 401
        user_id, name, username_db, pwd_hash, role = row
        if not check_password_hash(pwd_hash, password):
            return jsonify({"error": "بيانات الدخول خاطئة"}), 401
        claims = {"role": role or "user"}
        token = create_access_token(identity=username_db, additional_claims=claims, expires_delta=datetime.timedelta(hours=8))
        # دعم الصفحة الجديدة والقديمة معاً
        return jsonify({
            "success": True,
            "message": "تم تسجيل الدخول بنجاح",
            "access_token": token, 
            "student_name": name, 
            "role": claims["role"],
            "token": token,
            "user": {"name": name, "username": username_db}
        })
    except Exception as e:
        print("[ERROR] login:", e)
        return jsonify({"error": "حدث خطأ أثناء تسجيل الدخول"}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route("/api/register", methods=["POST"])
def register():
    """تسجيل مستخدم جديد"""
    try:
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip()
        password = (data.get("password") or "").strip()
        
        # التحقق من البيانات المطلوبة
        if not all([name, username, password]):
            return jsonify({"error": "الاسم واسم المستخدم وكلمة المرور مطلوبة"}), 400
        
        # التحقق من طول البيانات
        if len(username) < 3:
            return jsonify({"error": "اسم المستخدم يجب أن يكون 3 أحرف على الأقل"}), 400
        if len(password) < 4:
            return jsonify({"error": "كلمة المرور يجب أن تكون 4 أحرف على الأقل"}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # التحقق من عدم وجود المستخدم
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            return jsonify({"error": "اسم المستخدم موجود بالفعل"}), 400
        
        # التحقق من البريد الإلكتروني إذا تم إدخاله
        if email:
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cur.fetchone():
                return jsonify({"error": "البريد الإلكتروني مستخدم بالفعل"}), 400
        
        # إنشاء المستخدم الجديد
        password_hash = generate_password_hash(password)
        cur.execute("""
            INSERT INTO users (name, username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, username, email or None, password_hash, "user", datetime.datetime.now()))
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": "تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن"
        })
        
    except Exception as e:
        print(f"[ERROR] Register failed: {e}")
        return jsonify({"error": "حدث خطأ أثناء إنشاء الحساب"}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route("/api/logs", methods=["GET"])
@jwt_required()
def get_logs():
    if not _require_admin():
        return jsonify({"error": "غير مصرح للمستخدم"}), 403
    try:
        # قراءة آخر 100 سجل
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, message, type, username, timestamp FROM logs ORDER BY id DESC LIMIT 100")
        rows = cur.fetchall()
        logs = [
            {"id": r[0], "message": r[1], "type": r[2], "username": r[3], "timestamp": r[4]}
            for r in rows
        ]
        return jsonify({"items": logs})
    except Exception as e:
        print("[ERROR] get_logs:", e)
        return jsonify({"error": "تعذر جلب السجلات"}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data.get("message"):
            return jsonify({"error": "لا يوجد رسالة"}), 400
        
        message = data.get("message")
        
        # Get username from JWT if available
        username = "مستخدم"
        try:
            current_user = get_jwt_identity()
            if current_user:
                username = current_user
        except:
            pass
        
        reply = ask_gpt(message, username)
        return jsonify(response=reply)
        
    except Exception as e:
        print(f"[ERROR] Chat endpoint failed: {str(e)}")
        return jsonify({"error": "حدث خطأ في المعالجة"}), 500

@app.route("/api/analyze", methods=["POST"])
@jwt_required()
def analyze_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "يرجى رفع ملف"}), 400

    fn = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, fn)
    file.save(path)

    ext = fn.lower()
    if ext.endswith(".pdf"):
        text = read_pdf(path)
    elif ext.endswith(".docx"):
        text = read_docx(path)
    elif ext.endswith(".rtf"):
        text = read_rtf(path)
    elif ext.endswith((".jpg", ".jpeg", ".png")):
        text = read_image(path)
        if not text.strip():
            return jsonify({"error": "⚠️ لم يتم العثور على أي نص يمكن تحليله داخل الصورة."}), 400
    elif ext.endswith((".mp3", ".wav", ".webm")):
        text = transcribe_audio(path)
        if not isinstance(text, str) or not text.strip():
            return jsonify({"error": "⚠️ لم يتم العثور على أي نص صوتي يمكن تحليله."}), 400
        if text.startswith("❌"):
            return jsonify({"error": text}), 400
    else:
        return jsonify({"error": "نوع الملف غير مدعوم"}), 400

    # تم إلغاء الفلترة - نقبل كل الملفات
    # related = is_related_to_university(text)
    # if related != "yes":
    #     return jsonify({"error": "عذراً..."}), 400

    # Log extracted text (trim to avoid DB bloat)
    try:
        preview = (text or "").strip()
        if len(preview) > 500:
            preview = preview[:500] + "..."
        conn = get_db_connection()
        cur = conn.cursor()
        # الحصول على اسم المستخدم من JWT
        current_user = get_jwt_identity()
        # البحث عن اسم المستخدم الكامل في قاعدة البيانات
        try:
            user_conn = get_db_connection()
            user_cur = user_conn.cursor()
            user_cur.execute("SELECT name FROM users WHERE username = ?", (current_user,))
            user_row = user_cur.fetchone()
            username = user_row[0] if user_row else (current_user or "مجهول")
            user_conn.close()
        except:
            username = current_user or "مجهول"
        cur.execute("INSERT INTO logs (message, type, username) VALUES (?, 'text', ?)", (preview, username))
        conn.commit()
    except Exception as e:
        print("[WARN] failed to log analyze text:", e)
    finally:
        try:
            conn.close()
        except Exception:
            pass
        
        # الحصول على اسم المستخدم لتسجيل التحليلات
        current_user = get_jwt_identity()
        if current_user:
            try:
                user_conn = get_db_connection()
                user_cur = user_conn.cursor()
                user_cur.execute("SELECT name FROM users WHERE username = ?", (current_user,))
                user_row = user_cur.fetchone()
                username = user_row[0] if user_row else current_user
                user_conn.close()
            except:
                username = current_user

@app.route('/api/audio-chat', methods=['POST'])
@jwt_required()
def audio_chat():
    try:
        print("\n=== New Audio Request ===")
        print(f"Time: {datetime.datetime.now().isoformat()}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Content-Type: {request.content_type}")
        print(f"Content-Length: {request.content_length}")
        print(f"Files in request: {list(request.files.keys())}")
        print(f"Form data: {dict(request.form)}")
        
        # Check if the request contains a file
        if 'audio' not in request.files:
            print("Error: No audio file in request")
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio']
        print(f"Received file: {file.filename} (Type: {file.content_type}, Size: {file.content_length} bytes)")
        
        # Check if file is empty
        if file.filename == '':
            print("Error: Empty filename")
            return jsonify({"error": "No selected file"}), 400
        
        # Create uploads directory if it doesn't exist
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        # Secure the filename and create path
        filename = secure_filename(file.filename or 'recording.webm')
        file_path = os.path.join(upload_dir, filename)
        
        try:
            # Save the file temporarily
            file.save(file_path)
            print(f"File saved to: {file_path}")
            
            # Verify file was saved correctly
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                print("Error: File is empty after saving")
                return jsonify({"error": "Failed to save audio file"}), 500
                
            print(f"File size: {os.path.getsize(file_path)} bytes")
            
            # Transcribe audio to text
            print("Starting speech-to-text conversion...")
            transcript = transcribe_audio(file_path)
            
            try:
                print(f"Raw transcript length: {len(transcript) if transcript else 0} characters")
            except:
                pass
            
            # Check for transcription errors
            if not transcript or not isinstance(transcript, str):
                print("Error: Empty or invalid transcript")
                return jsonify({"error": "فشل في تحويل الصوت إلى نص"}), 400
            
            if transcript.startswith("[ERROR]"):
                print(f"Transcription error: {transcript}")
                return jsonify({"error": f"خطأ في معالجة الصوت: {transcript}"}), 400
                
            if len(transcript.strip()) < 1:
                print("Error: Transcript too short")
                return jsonify({"error": "التسجيل قصير جداً أو غير واضح. يرجى المحاولة مرة أخرى بصوت أوضح."}), 400
                
            print(f"Transcription successful. Length: {len(transcript)} characters")
            print(f"[DEBUG] Audio transcript: '{transcript}'")
            
            # Log the conversation
            try:
                current_user = get_jwt_identity()
                username = current_user or "Unknown"
                
                if current_user:
                    user_conn = get_db_connection()
                    user_cur = user_conn.cursor()
                    try:
                        user_cur.execute("SELECT name FROM users WHERE username = ?", (current_user,))
                        user_row = user_cur.fetchone()
                        if user_row:
                            username = user_row[0]
                    except Exception as e:
                        print(f"[WARN] User lookup failed: {e}")
                    finally:
                        user_conn.close()
                
                # Truncate long transcripts for logging
                log_message = (transcript[:497] + '...') if len(transcript) > 500 else transcript
                
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO logs (message, type, username, timestamp)
                    VALUES (?, 'audio', ?, datetime('now', 'localtime'))
                """, (log_message, username))
                conn.commit()
                
            except Exception as log_error:
                print(f"[WARN] Failed to log conversation: {log_error}")
            finally:
                try:
                    if 'conn' in locals():
                        conn.close()
                except Exception as e:
                    print(f"[WARN] Error closing database connection: {e}")
            
            # الحصول على اسم المستخدم لتسجيل التحليلات
            current_user = get_jwt_identity()
            analytics_username = "مجهول"
            if current_user:
                try:
                    user_conn = get_db_connection()
                    user_cur = user_conn.cursor()
                    user_cur.execute("SELECT name FROM users WHERE username = ?", (current_user,))
                    user_row = user_cur.fetchone()
                    analytics_username = user_row[0] if user_row else current_user
                    user_conn.close()
                except:
                    analytics_username = current_user
            
            # Get response from GPT
            print("Getting response from GPT...")
            answer = ask_gpt(transcript, analytics_username)
            
            return jsonify({
                "transcript": transcript,
                "response": answer
            })
            
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Error processing audio: {str(e)}"}), 500
            
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Temporary file {file_path} removed")
            except Exception as e:
                print(f"[WARN] Failed to remove temporary file: {e}")
                
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

# HTML Routes
@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/chat")
def chat_page():
    return render_template("user_chat.html")

@app.route("/admin")
def admin_page():
    return render_template("admin_dashboard.html")

# User Management API
@app.route("/api/users", methods=["GET"])
@jwt_required()
def get_users():
    if not _require_admin():
        return jsonify({"error": "غير مصرح للمستخدم"}), 403
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, username, email, role, created_at FROM users ORDER BY created_at DESC")
        rows = cur.fetchall()
        users = [
            {
                "id": r[0], "name": r[1], "username": r[2], 
                "email": r[3], "role": r[4], "created_at": r[5]
            }
            for r in rows
        ]
        return jsonify({"users": users})
    except Exception as e:
        print("[ERROR] get_users:", e)
        return jsonify({"error": "تعذر جلب المستخدمين"}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route("/api/users", methods=["POST"])
@jwt_required()
def add_user():
    if not _require_admin():
        return jsonify({"error": "غير مصرح للمستخدم"}), 403
    
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()
    role = (data.get("role") or "user").strip()

    if not name or not username or not password:
        return jsonify({"error": "يرجى إدخال جميع البيانات المطلوبة"}), 400
    if len(password) < 6:
        return jsonify({"error": "كلمة المرور يجب أن تكون 6 أحرف على الأقل"}), 400
    if role not in ["user", "admin"]:
        role = "user"

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            return jsonify({"error": "اسم المستخدم مستخدم بالفعل"}), 409

        pwd_hash = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (name, username, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
            (name, username, email, pwd_hash, role)
        )
        conn.commit()
        return jsonify({"status": "ok", "message": "تم إضافة المستخدم بنجاح"}), 201
    except Exception as e:
        print("[ERROR] add_user:", e)
        return jsonify({"error": "تعذر إضافة المستخدم"}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):              
    if not _require_admin():
        return jsonify({"error": "غير مصرح للمستخدم"}), 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "المستخدم غير موجود"}), 404
        
        # Don't allow deleting admin user
        if user[0] == ADMIN_USERNAME:
            return jsonify({"error": "لا يمكن حذف حساب الإدارة الرئيسي"}), 403
        
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return jsonify({"status": "ok", "message": "تم حذف المستخدم بنجاح"})
    except Exception as e:
        print("[ERROR] delete_user:", e)
        return jsonify({"error": "تعذر حذف المستخدم"}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route("/api/logout", methods=["POST"])
def logout():
    """
    Logout endpoint - simple logout without JWT validation
    """
    try:
        # Log the logout attempt
        print("[INFO] User logout requested")
        
        # Return success - frontend will handle token removal
        return jsonify({
            "status": "ok",
            "message": "تم تسجيل الخروج بنجاح"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Logout failed: {e}")
        return jsonify({
            "error": "حدث خطأ أثناء تسجيل الخروج"
        }), 500

# Questions Analytics API
@app.route("/api/questions-analytics", methods=["GET"])
@jwt_required()
def get_questions_analytics():
    if not _require_admin():
        return jsonify({"error": "غير مصرح للمستخدم"}), 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # إحصائيات عامة
        cur.execute("SELECT COUNT(*) FROM questions_analytics")
        total_questions = cur.fetchone()[0]
        
        # أكثر الفئات سؤالاً مع مثال على السؤال
        cur.execute("""
            SELECT question_category, COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM questions_analytics), 2) as percentage,
                   (SELECT question_text FROM questions_analytics q2 
                    WHERE q2.question_category = qa.question_category 
                    ORDER BY q2.timestamp DESC LIMIT 1) as sample_question
            FROM questions_analytics qa
            WHERE question_category IS NOT NULL AND question_category != ''
            GROUP BY question_category 
            ORDER BY count DESC 
            LIMIT 10
        """)
        categories_stats = [
            {
                "category": row[0], 
                "count": row[1], 
                "percentage": row[2],
                "sample_question": row[3][:100] + "..." if len(row[3]) > 100 else row[3]
            }
            for row in cur.fetchall()
        ]
        
        # أكثر الكلمات المفتاحية
        cur.execute("""
            SELECT question_keywords, COUNT(*) as count
            FROM questions_analytics 
            WHERE question_keywords IS NOT NULL AND question_keywords != ''
            GROUP BY question_keywords 
            ORDER BY count DESC 
            LIMIT 15
        """)
        keywords_raw = cur.fetchall()
        
        # معالجة الكلمات المفتاحية
        keyword_counts = {}
        for row in keywords_raw:
            keywords = row[0].split(', ')
            count = row[1]
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword:
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + count
        
        # ترتيب الكلمات المفتاحية
        keywords_stats = [
            {"keyword": k, "count": v, "percentage": round(v * 100.0 / total_questions, 2)}
            for k, v in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # إحصائيات المستخدمين الأكثر نشاطاً
        cur.execute("""
            SELECT username, COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM questions_analytics), 2) as percentage
            FROM questions_analytics 
            WHERE username IS NOT NULL AND username != ''
            GROUP BY username 
            ORDER BY count DESC 
            LIMIT 10
        """)
        users_stats = [
            {"username": row[0], "count": row[1], "percentage": row[2]}
            for row in cur.fetchall()
        ]
        
        # إحصائيات يومية (آخر 7 أيام)
        cur.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM questions_analytics 
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY DATE(timestamp) 
            ORDER BY date DESC
        """)
        daily_stats = [
            {"date": row[0], "count": row[1]}
            for row in cur.fetchall()
        ]
        
        # أحدث الأسئلة
        cur.execute("""
            SELECT question_text, question_category, username, timestamp
            FROM questions_analytics 
            ORDER BY timestamp DESC 
            LIMIT 20
        """)
        recent_questions = [
            {
                "question": row[0][:100] + "..." if len(row[0]) > 100 else row[0],
                "category": row[1],
                "username": row[2],
                "timestamp": row[3]
            }
            for row in cur.fetchall()
        ]
        
        return jsonify({
            "total_questions": total_questions,
            "categories_stats": categories_stats,
            "keywords_stats": keywords_stats,
            "users_stats": users_stats,
            "daily_stats": daily_stats,
            "recent_questions": recent_questions
        })
        
    except Exception as e:
        print(f"[ERROR] get_questions_analytics: {e}")
        return jsonify({"error": "تعذر جلب إحصائيات الأسئلة"}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route("/api/questions-summary", methods=["GET"])
@jwt_required()
def get_questions_summary():
    if not _require_admin():
        return jsonify({"error": "غير مصرح للمستخدم"}), 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # ملخص الأسئلة الأكثر تكراراً
        cur.execute("""
            SELECT question_text, COUNT(*) as frequency,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM questions_analytics), 2) as percentage,
                   question_category, MIN(timestamp) as first_asked, MAX(timestamp) as last_asked
            FROM questions_analytics 
            GROUP BY LOWER(TRIM(question_text))
            HAVING COUNT(*) > 1
            ORDER BY frequency DESC 
            LIMIT 20
        """)
        
        frequent_questions = [
            {
                "question": row[0][:150] + "..." if len(row[0]) > 150 else row[0],
                "frequency": row[1],
                "percentage": row[2],
                "category": row[3] or "غير محدد",
                "first_asked": row[4],
                "last_asked": row[5]
            }
            for row in cur.fetchall()
        ]
        
        return jsonify({
            "frequent_questions": frequent_questions
        })
        
    except Exception as e:
        print(f"[ERROR] get_questions_summary: {e}")
        return jsonify({"error": "تعذر جلب ملخص الأسئلة"}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route("/api/all-questions", methods=["GET"])
@jwt_required()
def get_all_questions():
    if not _require_admin():
        return jsonify({"error": "غير مصرح للمستخدم"}), 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # جلب جميع الأسئلة مع التفاصيل
        cur.execute("""
            SELECT question_text, question_category, question_keywords, 
                   username, timestamp, response_length
            FROM questions_analytics 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        
        all_questions = [
            {
                "question": row[0],
                "category": row[1] or "غير محدد",
                "keywords": row[2] or "لا توجد",
                "username": row[3],
                "timestamp": row[4],
                "response_length": row[5] or 0
            }
            for row in cur.fetchall()
        ]
        
        return jsonify({
            "all_questions": all_questions
        })
        
    except Exception as e:
        print(f"[ERROR] get_all_questions: {e}")
        return jsonify({"error": "تعذر جلب الأسئلة"}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

# ===== بوابة الطلاب الجديدة =====
@app.route("/user-portal")
def user_portal():
    """بوابة الطلاب المنفصلة - صفحة جديدة لليوزر فقط"""
    return render_template("user_portal.html")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    # Check if it's a React build file
    full_path = os.path.join(FRONTEND_BUILD_PATH, path)
    if path != "" and os.path.exists(full_path) and not path.startswith("api/"):
        return send_from_directory(FRONTEND_BUILD_PATH, path)
    # For any other path, redirect to login
    return render_template("login.html")

# ✅ تشغيل السيرفر
# Initialize database tables
init_users_table()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)