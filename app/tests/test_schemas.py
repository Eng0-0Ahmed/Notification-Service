import pytest
from pydantic import ValidationError
from app.schemas import EventType, NotificationPayload
from unittest.mock import AsyncMock, patch
import pytest
from app.schemas import EventType, NotificationPayload
from app.services.email import send_notification_email

def test_valid_notification_payload():
    data = {
        "event_type": "USER_REGISTRATION_EMAIL",
        "email": "test@example.com",
        "token_id": "dummy",
    }
    
    payload = NotificationPayload(**data)

    assert payload.event_type == EventType.USER_REGISTRATION
    assert payload.email == "test@example.com"
    assert payload.token_id == "dummy"
    assert payload.ticket_uuid is None


def test_invalid_email_raises_validation_error():
    data = {
        "event_type": "USER_REGISTRATION_EMAIL",
        "email": "not-an-email-address",
    }

    with pytest.raises(ValidationError):
        NotificationPayload(**data)


def test_missing_required_fields_raises_validation_error():
    data = {
        "event_type": "USER_REGISTRATION_EMAIL",
    }

    with pytest.raises(ValidationError):
        NotificationPayload(**data)




@pytest.mark.asyncio
@patch("app.services.email.aiosmtplib.send", new_callable=AsyncMock)
async def test_send_notification_email_user_registration(mock_send):
    payload = NotificationPayload(
        event_type=EventType.USER_REGISTRATION,
        email="testuser@example.com",
        token_id="test-token-123",
    )

    await send_notification_email(payload)

    mock_send.assert_called_once()

    message_arg = mock_send.call_args[0][0]

    assert message_arg["To"] == "testuser@example.com"
    assert message_arg["Subject"] == "Welcome! Verify your email"
    assert "http://localhost:8000/api/users/confirm-email/test-token-123" in message_arg.get_content()