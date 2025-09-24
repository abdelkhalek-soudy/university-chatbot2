import os
import sys
from app import transcribe_audio

def test_audio_file(file_path):
    """
    اختبار تحويل ملف صوتي إلى نص
    """
    if not os.path.exists(file_path):
        print(f"[ERROR] الملف غير موجود: {file_path}")
        return
    
    print(f"\n🔊 اختبار تحويل الصوت إلى نص:")
    print(f"📂 الملف: {file_path}")
    print(f"📏 الحجم: {os.path.getsize(file_path) / 1024:.2f} كيلوبايت")
    
    # استدعاء دالة التحويل
    try:
        result = transcribe_audio(file_path)
        print("\n✅ نتيجة التحويل:")
        print("-" * 50)
        print(result)
        print("-" * 50)
    except Exception as e:
        print(f"\n❌ حدث خطأ: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("الرجاء تحديد مسار الملف الصوتي")
        print(f"مثال: python {sys.argv[0]} path/to/audio.webm")
        sys.exit(1)
    
    test_audio_file(sys.argv[1])
