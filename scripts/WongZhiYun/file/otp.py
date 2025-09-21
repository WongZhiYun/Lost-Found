import random
from flask_mail import Message
from . import mail

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_email(user_email, otp):
    msg = Message(
        subject="Your OTP Code",
        sender="your_email@gmail.com",
        recipients=[user_email],
        body=f"Your OTP code is: {otp}"
    )
    mail.send(msg)
