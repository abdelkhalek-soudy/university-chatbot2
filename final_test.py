#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نهائي للفلترة
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import is_related_to_university

def test_final_filter():
    print("=== اختبار نهائي للفلترة ===")
    
    test_cases = [
        # أسئلة يجب أن تُرفض
        ("اشتركوا في القناة", "no", "كلمات مشبوهة"),
        ("ما هو الطقس اليوم؟", "no", "سؤال عام"),
        ("لايك للفيديو", "no", "كلمات مشبوهة"),
        ("abc xyz", "no", "نص مشوش"),
        ("hi", "no", "نص قصير"),
        
        # أسئلة يجب أن تمر
        ("ما هي كليات جامعة باديا؟", "yes", "سؤال جامعي"),
        ("كم مصاريف الدراسة؟", "yes", "سؤال جامعي"),
        ("متى يبدأ التسجيل في الجامعة؟", "yes", "سؤال جامعي"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for text, expected, description in test_cases:
        try:
            result = is_related_to_university(text)
            status = "✅" if result == expected else "❌"
            print(f"{status} '{text}' -> توقع: {expected}, نتيجة: {result} ({description})")
            if result == expected:
                passed += 1
        except Exception as e:
            print(f"❌ خطأ في اختبار '{text}': {e}")
    
    print(f"\n📊 النتيجة: {passed}/{total} اختبار ناجح")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! الفلترة تعمل بشكل مثالي")
    else:
        print("⚠️ بعض الاختبارات فشلت")

if __name__ == "__main__":
    test_final_filter()
