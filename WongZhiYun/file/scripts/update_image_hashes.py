import sqlite3, os, sys
from PIL import Image
import imagehash

# Get database path (argument 1) or default to "instance/users.db"
db_path = sys.argv[1] if len(sys.argv) > 1 else "instance/users.db"
# Get upload folder (argument 2) or default to "app/static/uploads"
upload_folder = sys.argv[2] if len(sys.argv) > 2 else "app/static/uploads"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Select all post IDs and their image filenames
rows = cur.execute("SELECT id, image FROM post").fetchall()
print(f"Found {len(rows)} rows")

for rid, imgname in rows:
    if not imgname:  # Skip if no image 
        continue
    path = os.path.join(upload_folder, imgname)
    if not os.path.exists(path):   # If file does not exist, print message
        print("No file", path)
        continue
    try:
        # Open image, convert to RGB, compute perceptual hash (pHash) 
        h = str(imagehash.phash(Image.open(path).convert("RGB")))
        cur.execute("UPDATE post SET image_hash=? WHERE id=?", (h, rid))
        print(f"Updated {rid} {imgname} hash {h}")
    except Exception as e:
        print("Error", imgname, e)

# Commit all updates and close connection 
conn.commit()
conn.close()
