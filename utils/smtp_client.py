import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

def send_otp_email(to_email, otp):
    msg = MIMEText (f"Your Otp is {otp}")
    msg['Subject'] = "Your login OTP"
    msg["from"]= EMAIL_USER
    msg["to"] = to_email
    
    with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
