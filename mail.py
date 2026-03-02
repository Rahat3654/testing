import os
from dotenv import load_dotenv
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType

if os.path.exists("dev.env"):
    load_dotenv("dev.env")

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT") or 587)
MAIL_FROM = os.getenv("MAIL_FROM_EMAIL") or os.getenv("MAIL_FROM")

mail_config = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_FROM=MAIL_FROM,
    MAIL_FROM_NAME="pentaridex",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

mail = FastMail(config=mail_config)

def create_message(recipients: list[str], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )
    return message
