from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime

app = Flask(__name__)

# --- Initialize DB if not exists ---
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE
    )
    """)

    # messages table
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        text TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# --- Routes ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/users")
def get_users():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT username FROM users ORDER BY username")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(users)

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    user = data.get("user")        # receiver
    sender = data.get("sender")    # sender
    text = data.get("text")
    timestamp = datetime.datetime.now().strftime("%H:%M")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender, receiver, text, timestamp) VALUES (?, ?, ?, ?)",
              (sender, user, text, timestamp))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/messages/<receiver>")
def get_messages(receiver):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT sender, text, timestamp FROM messages WHERE receiver=? OR sender=? ORDER BY id",
              (receiver, receiver))
    msgs = c.fetchall()
    conn.close()
    return jsonify(msgs)

if __name__ == "__main__":
    app.run(debug=True)
