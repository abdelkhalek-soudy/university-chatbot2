import sqlite3

conn = sqlite3.connect("chatbot.db")
c = conn.cursor()

# إنشاء جدول logs لو مش موجود
c.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('text', 'audio')),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# بيانات تجريبية
c.execute("INSERT INTO logs (message, type) VALUES ('ما هي مصاريف الجامعة؟', 'text')")
c.execute("INSERT INTO logs (message, type) VALUES ('تكلم عن برامج البكالوريوس', 'text')")
c.execute("INSERT INTO logs (message, type) VALUES ('سؤال صوتي تجريبي', 'audio')")

conn.commit()
conn.close()
print("✅ تم إنشاء قاعدة البيانات والبيانات بنجاح")

