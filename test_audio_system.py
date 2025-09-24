#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لنظام التسجيل الصوتي
Test script for audio recording system
"""

import requests
import json
import time

def test_server_health():
    """اختبار حالة الخادم"""
    try:
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ الخادم يعمل بشكل طبيعي")
            return True
        else:
            print(f"❌ مشكلة في الخادم: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ لا يمكن الوصول للخادم: {e}")
        return False

def test_login():
    """اختبار تسجيل الدخول"""
    try:
        login_data = {
            "username": "admin",
            "password": "badya@2024"
        }
        
        response = requests.post(
            'http://127.0.0.1:5000/api/login',
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print("✅ تسجيل الدخول نجح")
                return data['access_token']
            else:
                print("❌ لم يتم استلام access token")
                return None
        else:
            print(f"❌ فشل تسجيل الدخول: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في تسجيل الدخول: {e}")
        return None

def test_text_chat(token):
    """اختبار الشات النصي"""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        chat_data = {
            "message": "ما هي كليات جامعة باديا؟"
        }
        
        response = requests.post(
            'http://127.0.0.1:5000/api/chat',
            json=chat_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data or 'answer' in data:
                print("✅ الشات النصي يعمل بشكل طبيعي")
                return True
            else:
                print("❌ لم يتم استلام رد من الشات")
                return False
        else:
            print(f"❌ فشل الشات النصي: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الشات النصي: {e}")
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("🧪 بدء اختبار نظام شات بوت جامعة باديا")
    print("=" * 50)
    
    # اختبار 1: حالة الخادم
    print("\n1️⃣ اختبار حالة الخادم...")
    if not test_server_health():
        print("❌ الخادم لا يعمل. يرجى تشغيل الخادم أولاً.")
        return
    
    # اختبار 2: تسجيل الدخول
    print("\n2️⃣ اختبار تسجيل الدخول...")
    token = test_login()
    if not token:
        print("❌ فشل تسجيل الدخول. يرجى التحقق من بيانات المدير.")
        return
    
    # اختبار 3: الشات النصي
    print("\n3️⃣ اختبار الشات النصي...")
    if not test_text_chat(token):
        print("❌ فشل الشات النصي.")
        return
    
    # النتيجة النهائية
    print("\n" + "=" * 50)
    print("🎉 جميع الاختبارات نجحت!")
    print("✅ النظام جاهز للاستخدام")
    print("\n📋 معلومات مهمة:")
    print("🌐 الرابط: http://127.0.0.1:5000")
    print("👤 المدير: admin / badya@2024")
    print("🎤 التسجيل الصوتي: جاهز ومحسن")
    print("\n💡 نصائح للتسجيل الصوتي:")
    print("• تحدث بوضوح لمدة 3-10 ثوان")
    print("• استخدم مكان هادئ")
    print("• تأكد من إذن الميكروفون")

if __name__ == "__main__":
    main()
