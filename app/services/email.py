from email.message import EmailMessage
import aiosmtplib
from app.config import settings
from app.schemas import EventType, NotificationPayload


async def send_notification_email(payload: NotificationPayload):
    subject = ""
    body = ""

    BASE_URL = "http://localhost:8000"

    if payload.event_type == EventType.USER_REGISTRATION:
        token_id = payload.token_id
        subject = "Welcome! Verify your email"
        link = f"{BASE_URL}/api/users/confirm-email/{token_id}"
        body = f"Hello! Please verify your account using this link: {link}"

    elif payload.event_type == EventType.PASSWORD_RESET:
        token_id = payload.token_id
        user_id = payload.user_id
        subject = "Password Reset Request"
        link = f"{BASE_URL}/api/users/password-reset/{user_id}/{token_id}"
        body = f"Use this link to reset your password: {link}"

    elif payload.event_type == EventType.TICKET_PURCHASED:
        ticket_uuid = payload.ticket_uuid
        qr_code_url = payload.qr_code_url
        subject = "Your Ticket Purchase Confirmation"
        body = f"Thank you for your purchase! Your ticket code is {ticket_uuid}. Access your QR code here: {qr_code_url}"

    message = EmailMessage()
    message["From"] = settings.EMAILS_FROM
    message["To"] = payload.email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
    )