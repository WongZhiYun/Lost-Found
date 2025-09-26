import sqlite3, sys

db_path = sys.argv[1] if len(sys.argv)>1 else "instance/users.db"
con = sqlite3.connect(db_path)
cur = con.cursor()

tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
report_table = None
for t in tables:
    if any(k in t.lower() for k in ("report", "post", "item", "lost", "found")):
        report_table = t
        break

if not report_table:
    print("No report-like table found. Tables:", tables)
    con.close()
    sys.exit(1)

cols = [r[1] for r in cur.execute(f"PRAGMA table_info({report_table})").fetchall()]
print("Found report table:", report_table)
print("Columns:", cols)

if "image_hash" in cols:
    print("image_hash already exists.")
else:
    cur.execute(f"ALTER TABLE {report_table} ADD COLUMN image_hash TEXT;")
    con.commit()
    print("Added image_hash column to", report_table)

con.close()
