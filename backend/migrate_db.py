import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "lostfound.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE posts ADD COLUMN is_resolved BOOLEAN DEFAULT 0;")
    conn.commit()
    print("Column is_resolved added successfully!")
except Exception as e:
    print("Error:", e)
conn.close()
