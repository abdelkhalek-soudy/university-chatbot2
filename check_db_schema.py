import sqlite3
import os
import sys

# Set console output to UTF-8
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def check_schema():
    db_path = 'chatbot.db'
    if not os.path.exists(db_path):
        print("[ERROR] Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Check logs table structure
        print("\n=== Logs Table Schema ===")
        cur.execute("PRAGMA table_info(logs)")
        logs_columns = cur.fetchall()
        print("Columns:")
        for col in logs_columns:
            col_info = f"  {col['name']}: {col['type']}"
            if col['pk']:
                col_info += " PRIMARY KEY"
            if col['notnull']:
                col_info += " NOT NULL"
            if col['dflt_value'] is not None:
                col_info += f" DEFAULT {col['dflt_value']}"
            print(col_info)
        
        # Check foreign key constraint
        print("\n=== Foreign Keys ===")
        cur.execute("PRAGMA foreign_key_list(logs)")
        fks = cur.fetchall()
        if fks:
            for fk in fks:
                print(f"  {fk['from']} references {fk['table']}({fk['to']})")
        else:
            print("  No foreign key constraints found in logs table")
        
        # Check recent logs
        print("\n=== Recent Logs ===")
        try:
            cur.execute("""
                SELECT id, message, username, user_id, datetime(timestamp, 'localtime') as timestamp
                FROM logs 
                ORDER BY id DESC 
                LIMIT 5
            """)
            logs = cur.fetchall()
            if logs:
                for log in logs:
                    print(f"ID: {log['id']}")
                    print(f"  Message: {log['message']}")
                    print(f"  Username: {log['username']}")
                    print(f"  User ID: {log['user_id']}")
                    print(f"  Timestamp: {log['timestamp']}")
                    print()
            else:
                print("  No log entries found")
        except sqlite3.Error as e:
            print(f"  Error fetching logs: {e}")
        
        # Check users table
        print("\n=== Users Table ===")
        try:
            # First get the table structure
            cur.execute("PRAGMA table_info(users)")
            user_columns = cur.fetchall()
            print("Columns:")
            for col in user_columns:
                col_info = f"  {col['name']}: {col['type']}"
                if col['pk']:
                    col_info += " PRIMARY KEY"
                if col['notnull']:
                    col_info += " NOT NULL"
                if col['dflt_value'] is not None:
                    col_info += f" DEFAULT {col['dflt_value']}"
                print(col_info)
            
            # Then get the user data
            print("\nUser Data:")
            try:
                cur.execute("SELECT id, username, name, role FROM users")
                users = cur.fetchall()
                if users:
                    for user in users:
                        user_id = user['id']
                        username = user['username']
                        name = user['name'] if 'name' in user and user['name'] else 'N/A'
                        role = user['role'] if 'role' in user and user['role'] else 'N/A'
                        print(f"ID: {user_id}, Username: {username}, Name: {name}, Role: {role}")
                else:
                    print("  No users found")
            except sqlite3.Error as e:
                print(f"  Error fetching user data: {e}")
            else:
                print("  No users found")
        except sqlite3.Error as e:
            print(f"  Error fetching users: {e}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_schema()
