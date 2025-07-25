import random
import string
from datetime import datetime, timedelta
from utils.supabase_client import supabase
from utils.smtp_client import send_otp_email
import secrets


def register_user(email, password):
    response = supabase.auth.sign_up({"email": email, "password": password})
    return {
    "user": str(response.user.email),
    "message": "Registered successfully"
}


def login_user(email, password):
    auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})

    if not auth_response.user:
        return {"error": "Invalid credentials"}

    otp = "".join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    send_otp_email(email, otp)

    supabase.table("otp_verifications").insert({
        "email": email,
        "otp": otp,
        "expires_at": expires_at.isoformat()
    }).execute()

    return {"message": "OTP sent to email"}

# services/auth_handler.py

def is_token_valid(token: str) -> bool:
    # Dummy validation logic for now
    return token is not None and len(token) > 10


def verify_otp_and_create_token(email, otp):
    # Fetch matching OTP record
    result = supabase.table("otp_verifications").select("*").eq("email", email).eq("otp", otp).execute()

    if not result.data:
        return {"error": "Invalid OTP"}

    otp_record = result.data[0]
    if datetime.utcnow() > datetime.fromisoformat(otp_record["expires_at"]):
        return {"error": "OTP expired"}

    # Generate access token (random string)
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    # Store token in access_tokens table
    supabase.table("access_tokens").insert({
        "email": email,
        "token": token,
        "expires_at": expires_at.isoformat()
    }).execute()

    return {
        "access_token": token,
        "expires_at": expires_at.isoformat()
    }


    