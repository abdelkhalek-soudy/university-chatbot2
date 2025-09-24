#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط لنظام الفلترة
"""

# استيراد الدوال من app.py
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import is_related_to_university, _contains_university_keywords

def test_keyword_filter():
    """اختبار فلتر الكلمات المفتاحية"""
    print("🔍 اختبار فلتر الكلمات المفتاحية:")
    print("-" * 40)
    
    # أسئلة متعلقة بالجامعة
    university_questions = [
        "ما هي كليات جامعة باديا؟",
        "كم مصاريف الدراسة؟",
        "متى يبدأ التسجيل؟",
        "أريد معلومات عن التخصصات",
        "ما شروط القبول؟"
    ]
    
    # أسئلة عامة
    general_questions = [
        "ما هو الطقس اليوم؟",
        "كيف أطبخ المكرونة؟",
        "من هو رئيس مصر؟",
        "أخبرني نكتة مضحكة",
        "ما هي أخبار الرياضة؟"
    ]
    
    print("✅ أسئلة الجامعة (يجب أن تمر):")
    for q in university_questions:
        result = _contains_university_keywords(q)
        status = "✅" if result else "❌"
        print(f"{status} {q} -> {result}")
    
    print("\n❌ أسئلة عامة (يجب أن تُرفض):")
    for q in general_questions:
        result = _contains_university_keywords(q)
        status = "❌" if result else "✅"
        print(f"{status} {q} -> {result}")

def test_ai_filter():
    """اختبار فلتر الذكاء الاصطناعي (بدون استدعاء API)"""
    print("\n🤖 اختبار منطق الفلترة:")
    print("-" * 40)
    
    test_cases = [
        ("ما هي كليات جامعة باديا؟", "yes"),
        ("كم مصاريف الدراسة؟", "yes"),
        ("ما هو الطقس اليوم؟", "no"),
        ("كيف أطبخ المكرونة؟", "no"),
    ]
    
    for question, expected in test_cases:
        # نختبر فقط الكلمات المفتاحية لتجنب استدعاء API
        has_keywords = _contains_university_keywords(question)
        predicted = "yes" if has_keywords else "no"
        
        status = "✅" if predicted == expected else "❌"
        print(f"{status} '{question}' -> توقع: {expected}, نتيجة: {predicted}")

def main():
    print("🧪 بدء اختبار نظام الفلترة المحسن...")
    print("=" * 60)
    
    test_keyword_filter()
    test_ai_filter()
    
    print("\n" + "=" * 60)
    print("📋 ملخص:")
    print("- تم تحسين قائمة الكلمات المفتاحية لتشمل مصطلحات أكثر")
    print("- تم إعادة تفعيل نظام الفلترة في ask_gpt()")
    print("- تم تطبيق الفلترة على تحليل الملفات أيضاً")
    print("- النظام الآن يرفض الأسئلة غير المتعلقة بالجامعة")
    
    print("\n🎯 للاختبار الكامل:")
    print("1. افتح المتصفح على http://localhost:5000")
    print("2. سجل دخول بحساب المدير: admin / badya@2024")
    print("3. جرب أسئلة متعلقة بالجامعة (يجب أن تعمل)")
    print("4. جرب أسئلة عامة مثل الطقس (يجب أن تُرفض)")

if __name__ == "__main__":
    main()
