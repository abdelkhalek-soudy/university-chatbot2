#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام الفلترة للشات بوت
"""

import requests
import json

# إعدادات الاختبار
BASE_URL = "http://localhost:5000"
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test123456"

def test_login():
    """تسجيل الدخول للحصول على token"""
    try:
        # محاولة تسجيل الدخول
        login_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        
        if response.status_code == 401:
            # إنشاء حساب جديد إذا لم يكن موجود
            print("إنشاء حساب جديد...")
            signup_data = {
                "name": "Test User",
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD,
                "email": "test@example.com"
            }
            
            response = requests.post(f"{BASE_URL}/api/signup", json=signup_data)
            
        if response.status_code in [200, 201]:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"خطأ في تسجيل الدخول: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"خطأ في الاتصال: {e}")
        return None

def test_chat_filter(token, message, expected_filtered=False):
    """اختبار فلترة الرسائل"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {"message": message}
        response = requests.post(f"{BASE_URL}/api/chat", json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "")
            
            # التحقق من وجود رسالة الفلترة
            is_filtered = "عذراً، أنا مساعد ذكي مختص" in answer
            
            print(f"السؤال: {message}")
            print(f"متوقع فلترة: {expected_filtered}")
            print(f"تم فلترة: {is_filtered}")
            print(f"الجواب: {answer[:100]}...")
            print("-" * 50)
            
            return is_filtered == expected_filtered
        else:
            print(f"خطأ في الطلب: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"خطأ في اختبار الرسالة: {e}")
        return False

def main():
    print("🧪 بدء اختبار نظام الفلترة...")
    
    # تسجيل الدخول
    token = test_login()
    if not token:
        print("❌ فشل في تسجيل الدخول")
        return
    
    print("✅ تم تسجيل الدخول بنجاح")
    print("=" * 60)
    
    # اختبارات الفلترة
    test_cases = [
        # أسئلة متعلقة بالجامعة (يجب أن تمر)
        ("ما هي كليات جامعة باديا؟", False),
        ("كم مصاريف كلية الهندسة؟", False),
        ("متى يبدأ التسجيل في الجامعة؟", False),
        ("ما هي شروط القبول؟", False),
        ("أريد معلومات عن السكن الجامعي", False),
        
        # أسئلة عامة (يجب أن تُفلتر)
        ("ما هو الطقس اليوم؟", True),
        ("كيف أطبخ المكرونة؟", True),
        ("من هو رئيس مصر؟", True),
        ("ما هي أخبار كرة القدم؟", True),
        ("أخبرني نكتة مضحكة", True),
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for message, should_be_filtered in test_cases:
        if test_chat_filter(token, message, should_be_filtered):
            passed_tests += 1
            print("✅ اختبار ناجح")
        else:
            print("❌ اختبار فاشل")
        print()
    
    print("=" * 60)
    print(f"📊 نتائج الاختبار: {passed_tests}/{total_tests} اختبار ناجح")
    
    if passed_tests == total_tests:
        print("🎉 جميع الاختبارات نجحت! نظام الفلترة يعمل بشكل صحيح")
    else:
        print("⚠️ بعض الاختبارات فشلت. يحتاج النظام إلى مراجعة")

if __name__ == "__main__":
    main()
