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

    elif  payload.event_type == EventType.EVENT_CREATE_REMINDER:
        subject = "New Event Has Been Created"
        link = f"{BASE_URL}/api/events/{payload.event_uuid}"
        body = f"New Event has been created {payload.event_title}. For more information click here {link}"

    elif payload.event_type == EventType.EVENT_REMINDER:
        subject = f"Reminder: {payload.event_title} is tomorrow!"
        link = f"{BASE_URL}/api/events/{payload.event_uuid}"
        body = f"Hello! Sir {payload.name}, Reminder that {payload.event_title} starts in 24 hours, for your ticket {payload.ticket_uuid}. Check event details here {link}"

    elif payload.event_type == EventType.PROMO_REMAINING_TICKETS:
        tier = payload.ticket_tier
        qty = payload.remaining_tickets
        subject = f"Limited Tickets Available: {payload.event_title}"
        link = f"{BASE_URL}/api/events/{payload.event_uuid}"
        body = f"Only {qty} {tier} tickets remaining for {payload.event_title}! Get yours here {link}"
        
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