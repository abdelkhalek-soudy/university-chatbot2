from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os, re, datetime, docx, fitz
from PIL import Image
import pytesseract
import openai
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# 🔧 تحميل متغيرات البيئة
load_dotenv()

# إعداد المسارات
FRONTEND_BUILD_PATH = os.path.join(os.getcwd(), "frontend", "build")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# مفاتيح الأمان
openai.api_key = os.getenv("OPENAI_API_KEY")
SECRET_KEY     = os.getenv("SECRET_KEY", "fallback-secret")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "badia@2024")
PDF_PATH       = os.getenv("BADYA_PDF_PATH", "Badya.pdf")
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
]

# إعداد Flask
app = Flask(__name__, static_folder=FRONTEND_BUILD_PATH, static_url_path="")
app.config["JWT_SECRET_KEY"] = SECRET_KEY
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)
jwt     = JWTManager(app)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

# إعداد pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Gateintech\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# ✅ فلترة الذكاء الاصطناعي للتأكد من ارتباط النص بالجامعة
def is_related_to_university(text):
    try:
        prompt = (
            "أنت شات بوت متخصص فقط في الرد على الأسئلة الخاصة بجامعة بادية.\n"
            f"المستخدم قال: \"{text}\"\n"
            "اعتبر أن أي سؤال عن التعليم، الكليات، المصاريف، البرامج، القبول، الدراسة، المواد، أو أي شيء أكاديمي يعتبر سؤال عن جامعة بادية.\n"
            "حتى لو لم يذكر اسم الجامعة بشكل مباشر، افترض إنه يقصد جامعة بادية.\n"
            "لو السؤال عام مثل: (مرحبًا، ممكن مساعدة؟)، رد بـ: general\n"
            "لو مرتبط بالتعليم أو الجامعة، رد بـ: yes\n"
            "لو ملوش علاقة إطلاقًا بالجامعة أو التعليم، رد بـ: no\n"
            "رد بكلمة واحدة فقط: yes / no / general"
        )

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=5
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print("❌ فلترة فشلت:", e)
        return "yes"  # fallback: نعتبره متعلق بالجامعة

# ✅ الرد الذكي
def ask_gpt(msg):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "أنت مساعد ذكي متخصص في الرد فقط على الأسئلة المتعلقة بجامعة بادية."
                        " حتى لو المستخدم لم يذكر اسم الجامعة، افترض دائمًا أن السؤال عن جامعة بادية."
                        " لا تذكر أبدًا أن الجامعة غير معروفة. اجعل إجاباتك واضحة ومباشرة ودقيقة."
                    )
                },
                {"role": "user", "content": msg}
            ],
            temperature=0.4,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ✅ وظائف الملفات
def read_pdf(p): return "".join(page.get_text() for page in fitz.open(p))
def read_docx(p): return "\n".join(para.text for para in docx.Document(p).paragraphs)
def clean_text(t):
    t = re.sub(r'\\[a-z]+\d*','',t)
    t = re.sub(r'{\\.*?}','',t)
    return re.sub(r'\n+','\n',t).strip()
def read_rtf(p): return clean_text(open(p,'r',errors='ignore').read())
def read_image(p):
    text = pytesseract.image_to_string(Image.open(p), lang='eng+ara')
    print("📄 النص المستخرج من الصورة:", text)
    return text
def transcribe_audio(path):
    try:
        with open(path, "rb") as f:
            result = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
                language="ar"
            )
        return result.strip()
    except Exception as e:
        return f"❌ Whisper Error: {str(e)}"

# --- API ---

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if data.get("username") != ADMIN_USERNAME or data.get("password") != ADMIN_PASSWORD:
        return jsonify({"error": "بيانات الدخول خاطئة"}), 401
    token = create_access_token(identity=data["username"], expires_delta=datetime.timedelta(hours=8))
    return jsonify(access_token=token, student_name=data["username"])

@app.route("/api/chat", methods=["POST"])
@jwt_required()
@limiter.limit("5/minute")
def chat():
    data = request.get_json()
    if not data.get("message"):
        return jsonify({"error": "لا يوجد رسالة"}), 400
    reply = ask_gpt(data["message"])
    return jsonify(question=data["message"], answer=reply)

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
        return jsonify({"error": "❌ نوع الملف غير مدعوم"}), 400

    # فلترة ذكية بعد الاستخراج
    related = is_related_to_university(text)
    if related != "yes":
        return jsonify({"error": "❌ هذا الملف لا يبدو متعلقًا بجامعة بادية."}), 400

    reply = ask_gpt(text)
    return jsonify(reply=reply)

@app.route("/api/audio-chat", methods=["POST"])
@jwt_required()
def audio_chat():
    file = request.files.get("audio")
    if not file:
        return jsonify({"error": "يرجى رفع ملف صوتي"}), 400
    fn = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, fn)
    file.save(path)

    transcript = transcribe_audio(path)

    if not isinstance(transcript, str) or not transcript.strip():
        return jsonify({"error": "❌ لم يتم التعرف على الصوت بشكل صحيح."}), 400
    if transcript.startswith("❌"):
        return jsonify({"error": transcript}), 400

    print("🎧 النص المفرغ:", transcript)
    answer = ask_gpt(transcript)
    return jsonify(transcript=transcript, answer=answer)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    full_path = os.path.join(FRONTEND_BUILD_PATH, path)
    if path != "" and os.path.exists(full_path):
        return send_from_directory(FRONTEND_BUILD_PATH, path)
    return send_from_directory(FRONTEND_BUILD_PATH, "index.html")

# ✅ تشغيل السيرفر
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
