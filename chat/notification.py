import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Gmail account (system email)
sender_email = "lostandfoundmmu@gmail.com"
sender_password = "lostandfoundmmu.1"

# Receiver email
receiver_email = input("Receiver email: ")

# Create the email
msg = MIMEMultipart()
msg["From"] = formataddr(("Lost and Found MMU", sender_email)) 
msg["To"] = receiver_email
msg["Subject"] = "Notification from Lost And Found MMU"

# Email body
body = "You have received a new message from Lost And Found MMU."
msg.attach(MIMEText(body, "plain"))

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()
    print("Email sent successfully as Lost and Found MMU!")
except Exception as e:
    print("Error:", e)
