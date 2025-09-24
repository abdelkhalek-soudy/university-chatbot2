#!/usr/bin/env python3
"""
Simplified Flask app launcher - works without virtual environment
"""
import sys
import os
import subprocess

def install_requirements():
    """Install required packages"""
    packages = [
        'Flask==2.3.3',
        'flask-cors==4.0.0', 
        'flask-jwt-extended==4.5.3',
        'flask-limiter==3.5.0',
        'python-dotenv==1.0.0',
        'openai==1.3.0',
        'pytesseract==0.3.10',
        'python-docx==0.8.11',
        'PyMuPDF==1.23.8',
        'Pillow==10.0.1',
        'pandas==2.1.3',
        'openpyxl==3.1.2',
        'Werkzeug==2.3.7'
    ]
    
    print("Installing packages...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")
            continue

def main():
    print("🚀 Starting University Chatbot...")
    
    # Install packages
    install_requirements()
    
    # Import and run Flask app
    try:
        from app import app
        print("\n" + "="*50)
        print("✅ Server starting on http://localhost:5000")
        print("📋 Available pages:")
        print("   - Login: http://localhost:5000/login")
        print("   - User Chat: http://localhost:5000/chat")
        print("   - Admin Panel: http://localhost:5000/admin")
        print("   - Admin: admin / badya@2024")
        print("="*50 + "\n")
        
        # Open browser
        import webbrowser
        webbrowser.open('http://localhost:5000/login')
        
        app.run(host="0.0.0.0", port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
