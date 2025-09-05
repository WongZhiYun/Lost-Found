from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']  # assuming you store passwords

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                        (username, password)).fetchone()
    conn.close()

    if user:
        return jsonify({'status': 'success', 'user': dict(user)})
    else:
        return jsonify({'status': 'fail', 'message': 'Invalid credentials'})

@app.route('/users')
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT username FROM users').fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])
