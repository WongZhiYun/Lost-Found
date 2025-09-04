from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"
socketio = SocketIO(app)

DB_PATH = "users.db"

# --- Database helper ---
def get_user_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password, username FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user  # (id, email, password, username)

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return users  # list of (id, username)

def get_username_by_id(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# --- Routes ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = get_user_by_email(email)
        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[3]
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    users = get_all_users()
    current_user = session["username"]
    return render_template("home.html", users=users, current_user=current_user, current_id=session["user_id"])

@app.route("/profile/<int:user_id>")
def profile(user_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    username = get_username_by_id(user_id)
    if not username:
        return "User not found", 404
    return render_template("profile.html", profile_user=username, profile_id=user_id)

@app.route("/chat/<int:user_id>")
def chat(user_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    current_user = session["username"]
    other_user = get_username_by_id(user_id)
    if not other_user:
        return "User not found", 404

    room = get_room_name(current_user, other_user)
    return render_template("chat.html", room=room, other_user=other_user, current_user=current_user)

# --- Generate unique room name for 2 users ---
def get_room_name(user1, user2):
    return "_".join(sorted([user1, user2]))

# --- Socket.IO Events ---
@socketio.on("join")
def handle_join(data):
    room = data["room"]
    join_room(room)
    emit("status", {"msg": f"{data['username']} joined the chat."}, room=room)

@socketio.on("message")
def handle_message(data):
    room = data["room"]
    emit("message", {"user": data["username"], "msg": data["msg"]}, room=room)

if __name__ == "__main__":
    socketio.run(app, debug=True)
