from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_university_related(text):
    """Check if text is related to Badya University"""
    try:
        # Level 1: Check short texts
        if len(text) < 3:
            return "no"
        
        # Level 2: Check for forbidden universities
        forbidden_universities = [
            "جامعة القاهرة", "جامعة الأزهر", "جامعة عين شمس", "جامعة الإسكندرية",
            "الجامعة الأمريكية", "الجامعة الألمانية", "الجامعة البريطانية",
            "cairo university", "al-azhar university", "ain shams university"
        ]
        
        text_lower = text.lower()
        for forbidden_uni in forbidden_universities:
            if forbidden_uni in text_lower:
                return "no"
        
        # Level 3: Check for university keywords
        university_keywords = [
            "badya", "باديا", "جامعة", "university", "كلية", "قسم", "تخصص",
            "المصاريف", "مصروفات", "رسوم", "قبول", "التقديم", "تسجيل",
            "محاضرة", "امتحان", "مواد", "منحة", "سكن", "دراسة", "بكالوريوس",
            "طلاب", "طالب", "أستاذ", "دكتور", "هندسة", "طب", "صيدلة",
            "حاسوب", "إدارة", "اقتصاد", "حقوق", "آداب", "علوم", "تربية"
        ]
        
        has_university_keyword = any(keyword in text_lower for keyword in university_keywords)
        
        if not has_university_keyword:
            return "no"
        
        return "yes"
        
    except Exception as e:
        print(f"Error in filtering: {e}")
        return "no"

def ask_gpt(message, username="مستخدم"):
    """Get response for university-related questions"""
    try:
        # Filter questions
        relation = is_university_related(message)
        
        if relation == "no":
            return "عذراً، أنا مساعد ذكي متخصص في الإجابة على الأسئلة المتعلقة بجامعة باديا فقط. يرجى طرح سؤال واضح ومحدد عن الجامعة، الكليات، المصاريف، التسجيل، أو أي موضوع أكاديمي متعلق بالجامعة."
        
        # Simple predefined responses for common questions
        message_lower = message.lower()
        
        if "أين" in message or "موقع" in message or "مكان" in message:
            return "جامعة باديا تقع في مصر وهي جامعة خاصة معتمدة تقدم تعليماً عالي الجودة في مختلف التخصصات."
        
        elif "كليات" in message or "تخصصات" in message:
            return "جامعة باديا تضم كليات متنوعة منها:\n• كلية الهندسة\n• كلية الطب\n• كلية الصيدلة\n• كلية إدارة الأعمال\n• كلية علوم الحاسوب\n• كلية الآداب والعلوم الإنسانية\n\nللحصول على معلومات مفصلة عن كل كلية، يرجى التواصل مع الجامعة مباشرة."
        
        elif "مصاريف" in message or "رسوم" in message:
            return "مصاريف جامعة باديا تختلف حسب الكلية والتخصص. للحصول على معلومات دقيقة ومحدثة عن المصاريف، يرجى:\n• زيارة موقع الجامعة الرسمي\n• الاتصال بمكتب القبول والتسجيل\n• زيارة الجامعة شخصياً للاستفسار"
        
        elif "قبول" in message or "تسجيل" in message or "التحاق" in message:
            return "للالتحاق بجامعة باديا:\n• يجب الحصول على شهادة الثانوية العامة أو ما يعادلها\n• تقديم الأوراق المطلوبة لمكتب القبول\n• اجتياز أي اختبارات قبول مطلوبة\n• دفع الرسوم المقررة\n\nللتفاصيل الكاملة وشروط القبول، يرجى التواصل مع مكتب القبول والتسجيل بالجامعة."
        
        elif "امتحانات" in message or "اختبارات" in message:
            return "نظام الامتحانات في جامعة باديا يتبع المعايير الأكاديمية العالية. للحصول على معلومات عن مواعيد الامتحانات والجداول، يرجى مراجعة:\n• موقع الجامعة الرسمي\n• إدارة شؤون الطلاب\n• أستاذ المقرر مباشرة"
        
        else:
            return f"شكراً لسؤالك عن جامعة باديا. للحصول على إجابة مفصلة عن '{message}'، أنصحك بالتواصل مع الجامعة مباشرة عبر:\n• الموقع الرسمي للجامعة\n• مكتب خدمة الطلاب\n• الخط الساخن للجامعة\n\nجامعة باديا ملتزمة بتقديم أفضل خدمة تعليمية لطلابها."
        
    except Exception as e:
        print(f"Error: {e}")
        return f"عذراً، حدث خطأ في النظام. يرجى المحاولة مرة أخرى."

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")
        
        if not message:
            return jsonify({"error": "لا يوجد رسالة"}), 400
        
        print(f"[DEBUG] Processing message: {message}")
        
        # Get GPT response
        response = ask_gpt(message)
        
        print(f"[DEBUG] GPT response: {response[:100]}...")
        
        return jsonify({"response": response})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "حدث خطأ في المعالجة"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
