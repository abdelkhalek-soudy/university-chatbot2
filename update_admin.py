import sqlite3
import os
from werkzeug.security import generate_password_hash

def update_admin_user():
    db_path = 'chatbot.db'
    if not os.path.exists(db_path):
        print("[ERROR] Database file not found!")
        return False
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Update admin user
        admin_username = "admin"
        admin_password = "badya@2024"  # From memory
        admin_name = "Admin User"
        admin_email = "admin@badya.edu"
        
        # Check if admin exists
        cur.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
        admin = cur.fetchone()
        
        if admin:
            # Update existing admin
            cur.execute("""
                UPDATE users 
                SET name = ?, 
                    role = 'admin',
                    email = ?,
                    password_hash = ?
                WHERE username = ?
            """, (admin_name, admin_email, generate_password_hash(admin_password), admin_username))
            print(f"[INFO] Updated admin user: {admin_username}")
        else:
            # Create admin user if not exists
            cur.execute("""
                INSERT INTO users (name, username, email, password_hash, role)
                VALUES (?, ?, ?, ?, 'admin')
            """, (admin_name, admin_username, admin_email, generate_password_hash(admin_password)))
            print(f"[INFO] Created admin user: {admin_username}")
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if update_admin_user():
        print("Admin user updated successfully")
    else:
        print("Failed to update admin user")
