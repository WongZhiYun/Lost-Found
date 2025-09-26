import sqlite3
import sys

# Get database path from command line else default to "instance/users.db"
db_path = sys.argv[1] if len(sys.argv) > 1 else "instance/users.db"
# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("PRAGMA table_info(post);")
cols = [c[1] for c in cur.fetchall()]
if "image_hash" not in cols:
    cur.execute("ALTER TABLE post ADD COLUMN image_hash TEXT;")
    conn.commit()
    print("Added column image_hash to post.")
else:
    print("Column already exists.")

conn.close()
