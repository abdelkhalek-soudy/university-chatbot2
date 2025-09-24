"""
جامعة باديا - نظام الدردشة الذكي
تم تطويره بواسطة: عبدالخالق محمد
حقوق النشر © 2024 - جميع الحقوق محفوظة

هذا الكود ملك حصري لجامعة باديا ويحظر نسخه أو توزيعه بدون إذن كتابي مسبق
"""

# ===== الوظائف المشتركة بين تطبيق المستخدمين والإدارة =====

import os
import sqlite3
import pandas as pd
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import jwt
import hashlib
import uuid
import re

# تحميل المتغيرات البيئية
load_dotenv()

# إعدادات OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# إعدادات قاعدة البيانات
DATABASE = 'university_chatbot.db'
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')

# متغيرات المعرفة العامة
KNOWLEDGE_TEXT = ""
PDF_PATH = ""

# ===== وظائف قاعدة البيانات =====

def init_db():
    """إنشاء قاعدة البيانات والجداول"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول سجل المحادثات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_type TEXT DEFAULT 'text',
                session_id TEXT
            )
        ''')
        
        # جدول تحليل الأسئلة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                category TEXT NOT NULL,
                keywords TEXT,
                username TEXT NOT NULL,
                response_length INTEGER,
                session_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # إنشاء مستخدم الإدارة الافتراضي
        admin_password = hashlib.sha256('badya@2024'.encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO users (name, username, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Administrator', 'admin', 'admin@badya.edu.eg', admin_password, 'admin'))
        
        conn.commit()
        conn.close()
        print("[INFO] Database tables initialized successfully")
        
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")

# ===== وظائف المصادقة =====

def verify_user(username, password):
    """التحقق من بيانات المستخدم"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('SELECT id, name, role FROM users WHERE username = ? AND password_hash = ?', 
                      (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {'id': user[0], 'username': username, 'name': user[1], 'role': user[2]}
        return None
        
    except Exception as e:
        print(f"[ERROR] User verification failed: {e}")
        return None

def create_jwt_token(user_data):
    """إنشاء JWT token"""
    try:
        payload = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'name': user_data['name'],
            'role': user_data['role'],
            'exp': datetime.utcnow().timestamp() + 86400  # 24 hours
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    except Exception as e:
        print(f"[ERROR] JWT creation failed: {e}")
        return None

def verify_jwt_token(token):
    """التحقق من JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ===== وظائف تحميل المعرفة =====

def validate_badya_data(text_content):
    """فحص أمان البيانات للتأكد من أنها تخص جامعة باديا"""
    try:
        # الكلمات المطلوبة لجامعة باديا
        required_badya_keywords = [
            "باديا", "badya", "جامعة باديا", "badya university", "memphis", "ممفيس"
        ]
        
        # الكلمات المحظورة (جامعات أخرى)
        forbidden_keywords = [
            "الأزهر", "القاهرة", "عين شمس", "الإسكندرية", "أسيوط", "المنصورة", 
            "الزقازيق", "طنطا", "المنوفية", "قناة السويس", "بنها", "الفيوم",
            "الأمريكية", "الألمانية", "البريطانية", "الفرنسية", "harvard", "mit", "stanford"
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
    """فحص إضافي باستخدام GPT للتأكد من أن البيانات تخص جامعة باديا"""
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
            return False, "البيانات لا تخص جامعة باديا بشكل أساسي"
            
    except Exception as e:
        print(f"[ERROR] GPT validation failed: {e}")
        return False, f"خطأ في فحص GPT: {str(e)}"

def load_knowledge_from_excel(file_path, max_chars=50000, summarize=False):
    """تحميل المعرفة من ملف Excel مع فحص الأمان"""
    global KNOWLEDGE_TEXT, PDF_PATH
    
    try:
        print(f"[INFO] Attempting to load Excel file: {file_path}")
        
        # قراءة ملف Excel
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        df = pd.read_excel(file_path)
        
        # تحويل البيانات إلى نص
        knowledge_text = ""
        for _, row in df.iterrows():
            for col in df.columns:
                if pd.notna(row[col]):
                    knowledge_text += f"{col}: {row[col]}\n"
            knowledge_text += "\n"
        
        # فحص أمان البيانات
        print("[INFO] Validating data security for Badya University...")
        is_valid, message = validate_badya_data(knowledge_text)
        
        if not is_valid:
            print(f"[SECURITY ERROR] Data validation failed: {message}")
            raise SecurityError(f"رفض تحميل البيانات: {message}")
        
        print(f"[SECURITY OK] Data validation passed: {message}")
        
        # قطع النص إذا كان طويلاً
        if len(knowledge_text) > max_chars:
            knowledge_text = knowledge_text[:max_chars]
        
        # تلخيص النص إذا طُلب ذلك
        if summarize and len(knowledge_text) > 10000:
            knowledge_text = summarize_text(knowledge_text)
        
        KNOWLEDGE_TEXT = knowledge_text
        PDF_PATH = file_path
        
        print(f"[OK] Loaded Excel knowledge ({len(knowledge_text)} chars) from: {file_path} | summarize={summarize} | limit={max_chars}")
        return knowledge_text
        
    except Exception as e:
        print(f"[ERROR] Failed to load Excel file: {e}")
        raise e

# ===== وظائف الذكاء الاصطناعي =====

def is_related_to_university(text):
    """فحص متعدد المستويات للتأكد من ارتباط النص بجامعة باديا فقط"""
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

def ask_gpt(msg, username="مجهول"):
    """الرد الذكي باستخدام GPT"""
    try:
        # فلترة الأسئلة للتأكد من ارتباطها بجامعة باديا فقط
        relation = is_related_to_university(msg)
        print(f"[DEBUG] Relation result: {relation}")
        
        if relation == "no":
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

        messages = kb_message + [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        # تسجيل السؤال في التحليلات
        log_question_analytics(msg, answer, username)
        
        return answer
        
    except Exception as e:
        print(f"[ERROR] GPT request failed: {e}")
        return f"[ERROR] خطأ في النظام: {str(e)}"

def log_question_analytics(question_text, response_text, username):
    """تسجيل تحليلات الأسئلة"""
    try:
        # تصنيف السؤال باستخدام GPT
        category = categorize_question(question_text)
        
        # استخراج الكلمات المفتاحية
        keywords = extract_keywords(question_text)
        
        # حساب طول الرد
        response_length = len(response_text)
        
        # إنشاء session ID
        session_id = str(uuid.uuid4())[:8]
        
        # حفظ في قاعدة البيانات
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO questions_analytics 
            (question_text, category, keywords, username, response_length, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (question_text[:500], category, keywords, username, response_length, session_id))
        conn.commit()
        conn.close()
        
        print(f"[INFO] Question analytics logged: {category}")
        
    except Exception as e:
        print(f"[ERROR] Failed to log question analytics: {e}")

def categorize_question(question_text):
    """تصنيف السؤال إلى فئة"""
    try:
        prompt = f"""
صنف السؤال التالي إلى إحدى الفئات الجامعية:

السؤال: {question_text}

الفئات المتاحة:
- الكليات والتخصصات
- المصاريف والرسوم
- القبول والتسجيل
- الامتحانات والنتائج
- السكن الجامعي
- الأنشطة الطلابية
- معلومات عامة
- أخرى

أجب بفئة واحدة فقط:
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=20
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"[ERROR] Question categorization failed: {e}")
        return "أخرى"

def extract_keywords(text):
    """استخراج الكلمات المفتاحية من النص"""
    try:
        # كلمات مفتاحية جامعية شائعة
        university_keywords = [
            "باديا", "badya", "جامعة", "كلية", "قسم", "تخصص", "مصاريف", "رسوم",
            "قبول", "تسجيل", "امتحان", "نتيجة", "سكن", "طلاب", "دراسة"
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in university_keywords if kw in text_lower]
        
        return ", ".join(found_keywords[:5])  # أول 5 كلمات مفتاحية
        
    except Exception as e:
        print(f"[ERROR] Keyword extraction failed: {e}")
        return ""

# ===== استثناءات مخصصة =====

class SecurityError(Exception):
    """استثناء أمان مخصص"""
    pass

# ===== تهيئة النظام =====

# تحميل المعرفة عند بدء التشغيل
try:
    PDF_PATH = os.getenv('BADYA_PDF_PATH', 'badya_ultra_clean.xlsx')
    if PDF_PATH and os.path.exists(PDF_PATH):
        KNOWLEDGE_TEXT = load_knowledge_from_excel(PDF_PATH)
        print("[SECURITY OK] Knowledge loaded successfully with security validation")
    else:
        print(f"[WARNING] Knowledge file not found: {PDF_PATH}")
        KNOWLEDGE_TEXT = ""
except Exception as e:
    print(f"[ERROR] Failed to load knowledge: {e}")
    KNOWLEDGE_TEXT = ""

# تهيئة قاعدة البيانات
init_db()
