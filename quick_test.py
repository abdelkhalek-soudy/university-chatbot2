#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للفلترة
"""

import urllib.request
import urllib.parse
import json
import time

def test_filter():
    print("🧪 اختبار سريع للفلترة...")
    
    # تسجيل الدخول أولاً
    login_data = {
        "username": "admin",
        "password": "badya@2024"
    }
    
    try:
        # تسجيل الدخول
        req = urllib.request.Request(
            "http://localhost:5000/api/login",
            data=json.dumps(login_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            login_result = json.loads(response.read().decode('utf-8'))
            token = login_result.get('access_token')
            
        if not token:
            print("❌ فشل في الحصول على token")
            return
            
        print("✅ تم تسجيل الدخول بنجاح")
        
        # اختبار سؤال عام (يجب أن يُرفض)
        test_cases = [
            ("ما هو الطقس اليوم؟", True),  # يجب أن يُرفض
            ("ما هي كليات جامعة باديا؟", False)  # يجب أن يمر
        ]
        
        for question, should_be_filtered in test_cases:
            chat_data = {"message": question}
            
            req = urllib.request.Request(
                "http://localhost:5000/api/chat",
                data=json.dumps(chat_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                answer = result.get('answer', '')
                
                is_filtered = 'عذراً، أنا مساعد ذكي مختص' in answer
                
                print(f"\n📝 السؤال: {question}")
                print(f"🎯 متوقع فلترة: {should_be_filtered}")
                print(f"✅ تم فلترة: {is_filtered}")
                print(f"💬 الجواب: {answer[:100]}...")
                
                if is_filtered == should_be_filtered:
                    print("✅ النتيجة صحيحة!")
                else:
                    print("❌ النتيجة خاطئة!")
                    
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")

if __name__ == "__main__":
    test_filter()
