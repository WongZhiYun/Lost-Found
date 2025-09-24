import sqlite3, sys, os
from PIL import Image
import imagehash

# Get database path and upload directory from command line arguments or use defaults
db_path = sys.argv[1] if len(sys.argv)>1 else "instance/users.db"
upload_dir = sys.argv[2] if len(sys.argv)>2 else "app/static/uploads"

# Connect to the SQLite database
con = sqlite3.connect(db_path)
cur = con.cursor()

# find report table by checking table names for keywords
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
report_table = None
for t in tables:
    if any(k in t.lower() for k in ("report", "post", "item", "lost", "found")):
        report_table = t
        break

if not report_table:
    print("No report-like table found.")
    con.close()
    sys.exit(1)

# List columns in the report table and print them
cols = [r[1] for r in cur.execute(f"PRAGMA table_info({report_table})").fetchall()]
print("Report table:", report_table)
print("Columns:", cols)

# Guess the image filename column from a list of candidate names
candidates = ["image_filename", "image", "filename", "img", "photo", "image_path"]
image_col = None
for c in candidates:
    if c in cols:
        image_col = c
        break

if not image_col:
    print("No image filename column found among candidates. Please check table schema.")
    con.close()
    sys.exit(1)

print("Using image filename column:", image_col)
rows = cur.execute(f"SELECT rowid, * FROM {report_table}").fetchall()
# Find the index of the image filename column in the selected columns (skip rowid)
col_index = cols.index(image_col)

updated = 0        # Counter for how many rows have been updated
missing_files = 0  # Counter for missing image files
for r in rows:
    # r[0] is rowid, r[1..] are columns in cols order
    image_name = r[1 + col_index]  # because rowid added at front
    pk_rowid = r[0]

    # Skip if no image filename
    if not image_name:
        continue

    # Construct the local file path for the image
    local_path = os.path.join(upload_dir, image_name)
    # Check if image file exists
    if not os.path.exists(local_path):
        print(f"Missing file for id {pk_rowid}: {local_path}")
        missing_files += 1
        continue
    try:
        # Open image, convert to RGB and compute perceptual hash
        img = Image.open(local_path).convert("RGB")
        h = imagehash.phash(img)
        hash_hex = str(h)
        # Update image_hash column for this row
        cur.execute(f"UPDATE {report_table} SET image_hash = ? WHERE rowid = ?", (hash_hex, pk_rowid))
        updated += 1
    except Exception as e:
        print("Error processing", local_path, e)

# Commit changes and close the database connection
con.commit()
con.close()
print(f"Done. Updated: {updated}, Missing files: {missing_files}")
