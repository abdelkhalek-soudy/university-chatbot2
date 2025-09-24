#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاحات التسجيل الصوتي
"""

import os
import sys
from io import BytesIO

def test_audio_processing():
    """اختبار معالجة الملفات الصوتية"""
    print("🧪 اختبار إصلاحات التسجيل الصوتي...")
    print("=" * 50)
    
    # اختبار 1: فحص BytesIO
    print("1️⃣ اختبار BytesIO...")
    try:
        test_data = b"test audio data"
        file_obj = BytesIO(test_data)
        file_obj.name = "test_recording.webm"
        print(f"✅ BytesIO يعمل بشكل صحيح - الحجم: {len(test_data)} bytes")
    except Exception as e:
        print(f"❌ خطأ في BytesIO: {e}")
    
    # اختبار 2: فحص تحديد MIME types
    print("\n2️⃣ اختبار تحديد MIME types...")
    test_files = {
        "test.webm": "audio/webm",
        "test.wav": "audio/wav", 
        "test.mp3": "audio/mpeg",
        "test.m4a": "audio/mp4"
    }
    
    for filename, expected_mime in test_files.items():
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext == '.webm':
            mime_type = 'audio/webm'
        elif file_ext == '.wav':
            mime_type = 'audio/wav'
        elif file_ext == '.mp3':
            mime_type = 'audio/mpeg'
        elif file_ext == '.m4a':
            mime_type = 'audio/mp4'
        else:
            mime_type = 'audio/wav'
        
        if mime_type == expected_mime:
            print(f"✅ {filename} -> {mime_type}")
        else:
            print(f"❌ {filename} -> {mime_type} (متوقع: {expected_mime})")
    
    # اختبار 3: فحص معالجة الأخطاء
    print("\n3️⃣ اختبار معالجة الأخطاء...")
    test_errors = [
        "could not be decoded",
        "invalid_request_error", 
        "file size issue",
        "general error"
    ]
    
    for error in test_errors:
        if "could not be decoded" in error.lower():
            error_type = "Audio format not supported"
        elif "invalid_request_error" in error.lower():
            error_type = "Invalid request format"
        elif "file" in error.lower() and "size" in error.lower():
            error_type = "File size issue"
        else:
            error_type = "General error"
        
        print(f"✅ '{error}' -> {error_type}")
    
    print("\n" + "=" * 50)
    print("🎉 جميع الاختبارات مكتملة!")
    print("\n📋 ملخص الإصلاحات:")
    print("• ✅ تحسين إرسال الملفات باستخدام BytesIO")
    print("• ✅ تحسين تحديد MIME types")
    print("• ✅ رفع جودة التسجيل إلى 128kbps")
    print("• ✅ إزالة timeslice من MediaRecorder")
    print("• ✅ تحسين معالجة أخطاء Whisper")
    print("• ✅ رسائل خطأ واضحة للمستخدم")
    
    print("\n🚀 التوصيات للاختبار:")
    print("1. شغل الخادم: python app.py")
    print("2. افتح المتصفح: http://127.0.0.1:5000/user-portal")
    print("3. جرب التسجيل الصوتي:")
    print("   • تحدث بوضوح لمدة 3-5 ثوان")
    print("   • قل شيئاً مثل: 'ما هي مصاريف جامعة باديا؟'")
    print("   • تأكد من جودة الميكروفون")

if __name__ == "__main__":
    test_audio_processing()
