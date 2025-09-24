import sqlite3, sys

# Get database path from command line argument, or use default path
db_path = sys.argv[1] if len(sys.argv)>1 else "instance/users.db"
# Connect to the SQLite database
con = sqlite3.connect(db_path)
cur = con.cursor()

# Get all table names in the database
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
report_table = None
# Find the first table whose name suggests it might be the report table
for t in tables:
    if any(k in t.lower() for k in ("report", "post", "item", "lost", "found")):
        report_table = t
        break

# If no suitable table found, print message and exit
if not report_table:
    print("No report-like table found. Tables:", tables)
    con.close()
    sys.exit(1)

# Get the list of columns in the found report table
cols = [r[1] for r in cur.execute(f"PRAGMA table_info({report_table})").fetchall()]
print("Found report table:", report_table)
print("Columns:", cols)

# Check if image_hash column already exists
if "image_hash" in cols:
    print("image_hash already exists.")
else:
    # Add image_hash column of type TEXT if it doesn't exist
    cur.execute(f"ALTER TABLE {report_table} ADD COLUMN image_hash TEXT;")
    con.commit()
    print("Added image_hash column to", report_table)

# Close the database connection
con.close()
