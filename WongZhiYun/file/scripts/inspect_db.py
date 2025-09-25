import sqlite3
import sys

db_path = sys.argv[1] if len(sys.argv) > 1 else "instance/users.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("Tables:", tables)

for t in tables:
    print("\nSchema for", t[0])
    for col in cursor.execute(f"PRAGMA table_info({t[0]});").fetchall():
        print(col)

conn.close()
