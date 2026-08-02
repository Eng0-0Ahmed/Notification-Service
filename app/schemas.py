from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr


class EventType(str, Enum):
    USER_REGISTRATION = "USER_REGISTRATION_EMAIL"
    PASSWORD_RESET = "PASSWORD_RESET_EMAIL"
    TICKET_PURCHASED = "TICKET_PURCHASED"

class NotificationPayload(BaseModel):
    event_type: EventType
    email: EmailStr
    user_id: Optional[str] = None
    token_id: Optional[str] = None
    ticket_uuid: Optional[str] = None
    event_id: Optional[str] = None
    qr_code_url: Optional[str] = None