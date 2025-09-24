import sqlite3, sys

# Get the database path from the command line argument or use default path
db_path = sys.argv[1] if len(sys.argv)>1 else "instance/users.db"
# Connect to the SQLite database
con = sqlite3.connect(db_path)
cur = con.cursor()

print("DB:", db_path)
# List all tables in the database
print("Tables:")
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
for t in tables:
    print(" -", t)

def show_schema(table):
    """
    Print the schema (column info) of the given table.
    """
    print(f"\nSchema for {table}:")
    for r in cur.execute(f"PRAGMA table_info({table})").fetchall():
        print(r)  

print()
# show all table schema
for t in tables:
    show_schema(t)

# find report（table names containing these keywords）
candidates = [t for t in tables if any(k in t.lower() for k in ("report", "post", "item", "lost", "found"))]
print("\nCandidate report tables:", candidates)
# Show sample rows from each candidate report table (limit 5 rows)
for t in candidates:
    print(f"\nSample rows for {t}:")
    for row in cur.execute(f"SELECT * FROM {t} LIMIT 5").fetchall():
        print(row)

# Close the database connection
con.close()
