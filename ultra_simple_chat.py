from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def is_university_related(text):
    """Check if text is related to Badya University"""
    if len(text) < 3:
        return False
    
    # Check for university keywords
    university_keywords = [
        "badya", "باديا", "جامعة", "university", "كلية", "قسم", "تخصص",
        "المصاريف", "مصروفات", "رسوم", "قبول", "التقديم", "تسجيل",
        "محاضرة", "امتحان", "مواد", "منحة", "سكن", "دراسة", "بكالوريوس",
        "طلاب", "طالب", "أستاذ", "دكتور", "هندسة", "طب", "صيدلة",
        "حاسوب", "إدارة", "اقتصاد", "حقوق", "آداب", "علوم", "تربية"
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in university_keywords)

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        print("[DEBUG] Chat endpoint called")
        
        data = request.get_json()
        if not data:
            print("[DEBUG] No JSON data")
            return jsonify({"error": "لا توجد بيانات"}), 400
            
        message = data.get("message", "")
        print(f"[DEBUG] Message received: {len(message)} characters")
        
        if not message:
            print("[DEBUG] Empty message")
            return jsonify({"error": "لا يوجد رسالة"}), 400
        
        # Check if university related
        if not is_university_related(message):
            print("[DEBUG] Not university related")
            response = "عذراً، أنا مساعد ذكي متخصص في الإجابة على الأسئلة المتعلقة بجامعة باديا فقط. يرجى طرح سؤال واضح ومحدد عن الجامعة."
            return jsonify({"response": response})
        
        print("[DEBUG] University related question detected")
        
        # Simple responses based on keywords
        message_lower = message.lower()
        
        if "أين" in message or "موقع" in message or "مكان" in message:
            response = "جامعة باديا تقع في مصر وهي جامعة خاصة معتمدة تقدم تعليماً عالي الجودة في مختلف التخصصات."
        elif "كليات" in message or "تخصصات" in message:
            response = "جامعة باديا تضم كليات متنوعة منها:\n• كلية الهندسة\n• كلية الطب\n• كلية الصيدلة\n• كلية إدارة الأعمال\n• كلية علوم الحاسوب\n• كلية الآداب والعلوم الإنسانية"
        elif "مصاريف" in message or "رسوم" in message:
            response = "مصاريف جامعة باديا تختلف حسب الكلية والتخصص. للحصول على معلومات دقيقة، يرجى التواصل مع مكتب القبول والتسجيل."
        elif "قبول" in message or "تسجيل" in message:
            response = "للالتحاق بجامعة باديا يجب الحصول على شهادة الثانوية العامة وتقديم الأوراق المطلوبة لمكتب القبول."
        else:
            response = f"شكراً لسؤالك عن جامعة باديا. للحصول على معلومات مفصلة، يرجى التواصل مع الجامعة مباشرة."
        
        print(f"[DEBUG] Response generated: {len(response)} characters")
        return jsonify({"response": response})
        
    except Exception as e:
        print(f"[ERROR] Exception in chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "حدث خطأ في المعالجة"}), 500

if __name__ == '__main__':
    print("Starting ultra simple chat server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
