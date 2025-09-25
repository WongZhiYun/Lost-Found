import sqlite3, os, sys
from PIL import Image
import imagehash

db_path = sys.argv[1] if len(sys.argv) > 1 else "instance/users.db"
upload_folder = sys.argv[2] if len(sys.argv) > 2 else "app/static/uploads"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

rows = cur.execute("SELECT id, image FROM post").fetchall()
print(f"Found {len(rows)} rows")

for rid, imgname in rows:
    if not imgname:
        continue
    path = os.path.join(upload_folder, imgname)
    if not os.path.exists(path):
        print("No file", path)
        continue
    try:
        h = str(imagehash.phash(Image.open(path).convert("RGB")))
        cur.execute("UPDATE post SET image_hash=? WHERE id=?", (h, rid))
        print(f"Updated {rid} {imgname} hash {h}")
    except Exception as e:
        print("Error", imgname, e)

conn.commit()
conn.close()
