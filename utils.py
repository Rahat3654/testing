import os
import smtplib
import pyotp
import jwt
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import Profile, SessionLocal, User
from models import Users

# load local dev.env only if present
if os.path.exists("dev.env"):
    load_dotenv("dev.env")

passwd_context = CryptContext(schemes=["bcrypt"])
ACCESS_TOKEN_EXPIRY = 3600

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT") or 587)
MAIL_FROM = os.getenv("MAIL_FROM_EMAIL") or os.getenv("MAIL_FROM")
MAIL_FROM_NAME = "pentaridex"
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGO")

blacklist = set()

def generate_passwd_hash(password: str) -> str:
    return passwd_context.hash(password)

async def user_exists(email: str, session: Session) -> bool:
    # Use a DB filter instead of iterating all users
    return session.query(User).filter(User.email == email).first() is not None

async def get_user_by_email(email: str, session: Session):
    return session.query(User).filter(User.email == email).first()

def verify_password(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)

async def send_email_verify(email: str):
    secret = pyotp.random_base32()
    if not MAIL_SERVER or not MAIL_USERNAME or not MAIL_PASSWORD:
        # Skip real email in CI/tests when mail env vars are not configured
        print("Mail configuration incomplete, skipping email send in CI/test mode")
        return secret
    time_window = 60 * 5
    totp = pyotp.TOTP(s=secret, interval=time_window)
    otp = totp.now()
    try:
        with smtplib.SMTP(MAIL_SERVER, port=MAIL_PORT) as connection:
            connection.starttls()
            connection.login(user=MAIL_USERNAME, password=MAIL_PASSWORD)
            connection.sendmail(
                from_addr=MAIL_FROM,
                to_addrs=email,
                msg=f"Subject:Email Verification OTP\n\nYour OTP for email verification is: {otp}",
            )
        print("Please check your email for the OTP to complete your registration.")
        return secret
    except Exception as e:
        print("Exception occurred while sending email:", e)
        return None
