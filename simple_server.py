from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('chatbot.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/user-portal')
def user_portal():
    return render_template('user_portal.html')

@app.route('/')
def home():
    return render_template('user_portal.html')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not all([name, username, password]):
            return jsonify({'error': 'الاسم واسم المستخدم وكلمة المرور مطلوبة'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'اسم المستخدم يجب أن يكون 3 أحرف على الأقل'}), 400
        
        if len(password) < 4:
            return jsonify({'error': 'كلمة المرور يجب أن تكون 4 أحرف على الأقل'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if username exists
        cur.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cur.fetchone():
            return jsonify({'error': 'اسم المستخدم موجود بالفعل'}), 400
        
        # Check if email exists
        if email:
            cur.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cur.fetchone():
                return jsonify({'error': 'البريد الإلكتروني مستخدم بالفعل'}), 400
        
        # Create user
        password_hash = generate_password_hash(password)
        cur.execute('''
            INSERT INTO users (name, username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, username, email or None, password_hash, 'user', datetime.datetime.now()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن'
        })
        
    except Exception as e:
        print(f"Register error: {e}")
        return jsonify({'error': 'حدث خطأ أثناء إنشاء الحساب'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            return jsonify({
                'success': True,
                'message': 'تم تسجيل الدخول بنجاح',
                'user': {'name': user['name'], 'username': user['username']},
                'token': 'dummy_token'
            })
        else:
            return jsonify({'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'حدث خطأ أثناء تسجيل الدخول'}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
