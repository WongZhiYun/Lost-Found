from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

app = Flask(__name__)

# --- DATABASE CONFIG ---
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --- EMAIL CONFIG ---
SENDER_EMAIL = "lostandfoundmmu@gmail.com"
SENDER_PASSWORD = "lostandfoundmmu.1"   # ⚠️ Use Gmail App Password in production
ADMIN_EMAIL = "admin@example.com"       # Replace with actual admin email


# --- MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.String(20), nullable=False,
                          default=datetime.now().strftime("%H:%M:%S"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)


# --- EMAIL FUNCTION ---
def send_email(user_name, user_message):
    """Send email notification to admin with chat message"""
    msg = MIMEMultipart()
    msg["From"] = formataddr(("Lost and Found MMU", SENDER_EMAIL))  # Always system email
    msg["To"] = ADMIN_EMAIL
    msg["Subject"] = f"New Message from {user_name}"

    body = f"User: {user_name}\n\nMessage:\n{user_message}"
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, ADMIN_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email sent successfully to admin!")
    except Exception as e:
        print("❌ Error sending email:", e)


# --- ROUTES ---
@app.route("/")
def index():
    messages = Message.query.all()
    return render_template("chat.html", messages=messages)


@app.route("/send", methods=["POST"])
def send():
    text = request.form.get("message")
    user_name = "Website User"  # default, or fetch from login session

    if text.strip():
        timestamp = datetime.now().strftime("%H:%M:%S")
        new_msg = Message(text=text, timestamp=timestamp)
        db.session.add(new_msg)
        db.session.commit()

        # Send email (always from Lost & Found email)
        send_email(user_name, text)

    all_msgs = Message.query.all()
    return jsonify({
        "status": "ok",
        "messages": [{"text": m.text, "time": m.timestamp} for m in all_msgs]
    })


# --- INIT ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
