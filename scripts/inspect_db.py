import sqlite3, sys

db_path = sys.argv[1] if len(sys.argv)>1 else "instance/users.db"
con = sqlite3.connect(db_path)
cur = con.cursor()

print("DB:", db_path)
print("Tables:")
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
for t in tables:
    print(" -", t)

def show_schema(table):
    print(f"\nSchema for {table}:")
    for r in cur.execute(f"PRAGMA table_info({table})").fetchall():
        print(r)  

print()
# show all table schema
for t in tables:
    show_schema(t)

# find report（include report/post/item）
candidates = [t for t in tables if any(k in t.lower() for k in ("report", "post", "item", "lost", "found"))]
print("\nCandidate report tables:", candidates)
for t in candidates:
    print(f"\nSample rows for {t}:")
    for row in cur.execute(f"SELECT * FROM {t} LIMIT 5").fetchall():
        print(row)

con.close()
