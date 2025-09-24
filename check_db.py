import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot.db")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Print all tables
    print("\n=== Tables in database ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"\nTable: {table[0]}")
        
        # Print table structure
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print("\nColumns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'PK' if col[5] else ''}")
        
        # Print row count
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"\nRow count: {count}")
        
        # Print sample data (first 5 rows)
        if count > 0:
            print("\nSample data (first 5 rows):")
            cursor.execute(f"SELECT * FROM {table[0]} LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(f"  {row}")
    
    # Check for any constraints on the logs table
    print("\n=== Foreign Key Constraints ===")
    cursor.execute("PRAGMA foreign_key_list(logs)")
    fks = cursor.fetchall()
    if fks:
        for fk in fks:
            print(f"  {fk}")
    else:
        print("  No foreign key constraints on logs table")
    
    # Check for any triggers
    print("\n=== Triggers ===")
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'")
    triggers = cursor.fetchall()
    if triggers:
        for trigger in triggers:
            print(f"\nTrigger: {trigger[0]}")
            print(f"SQL: {trigger[1]}")
    else:
        print("  No triggers found")
    
except Exception as e:
    print(f"Error: {e}")
    
finally:
    try:
        conn.close()
    except:
        pass
