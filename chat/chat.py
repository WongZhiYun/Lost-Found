from flask import Flask, render_template, session
from flask_socketio import SocketIO, join_room, emit
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Track connected users per room
users = {}

@app.route('/')
def index():
    # Assume user is logged in
    if 'username' not in session:
        session['username'] = 'zhiyun0506'  # example
    current_user = session['username']

    # Get all users except the current user
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username != ?", (current_user,))
    all_users = [row[0] for row in c.fetchall()]
    conn.close()

    # Render template and pass users
    return render_template('index.html', current_user=current_user, users=all_users)

@socketio.on('join')
def on_join(data):
    username = session['username']
    room = data['room']
    join_room(room)
    users[username] = room
    emit('status', {'msg': f'{username} has joined the chat'}, room=room)

@socketio.on('send_message')
def handle_message(data):
    username = session['username']
    room = data['room']
    emit('receive_message', {'username': username, 'msg': data['msg']}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
