from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr


class EventType(str, Enum):
    USER_REGISTRATION = "USER_REGISTRATION_EMAIL"
    PASSWORD_RESET = "PASSWORD_RESET_EMAIL"
    TICKET_PURCHASED = "TICKET_PURCHASED"
    EVENT_REMINDER = "EVENT_REMINDER_24H"
    PROMO_REMAINING_TICKETS = "PROMO_REMAINING_TICKETS"
    EVENT_CREATE_REMINDER = "EVENT_CREATED_EMAIL"

class NotificationPayload(BaseModel):
    event_type: EventType
    email: EmailStr
    user_id: str | None = None
    token_id: str | None = None
    ticket_uuid: str | None = None
    event_id: str | None = None
    qr_code_url: str | None = None
    event_title: str | None = None
    event_uuid: str | None = None
    ticket_tier: str | None = None
    event_date: str | None = None
    name: str | None = None
    remaining_tickets: str | None = None