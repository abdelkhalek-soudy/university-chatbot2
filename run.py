#!/usr/bin/env python3
"""
Simple launcher script for the University Chatbot Flask application
"""
import os
import sys
import subprocess

def main():
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print("Starting University Chatbot...")
    print(f" Project directory: {project_dir}")
    
    # Check if virtual environment exists
    venv_path = os.path.join(project_dir, "venv")
    if not os.path.exists(venv_path):
        print("  Virtual environment not found. Please create one manually:")
        print("   python -m venv venv")
        print("   venv\\Scripts\\activate")
        print("   pip install -r requirements.txt")
        return
    
    # Try to run the Flask app
    try:
        print("Starting Flask server on http://localhost:5000")
        print("Available pages:")
        print("   - Login/Signup: http://localhost:5000/login")
        print("   - Admin Dashboard: http://localhost:5000/admin")
        print("   - User Chat: http://localhost:5000/chat")
        print("\nPress Ctrl+C to stop the server")
        print("\n" + "="*50)
        
        # Import and run the Flask app
        from app import app
        app.run(host="0.0.0.0", port=5000, debug=True)
        
    except ImportError as e:
        print(f"\u274C Import error: {e}")
        print("\u2728 Please install dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()
