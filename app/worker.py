import asyncio
import json
import logging
from pydantic import ValidationError
import redis.asyncio as aioredis
from redis.exceptions import TimeoutError as RedisTimeoutError
from app.config import settings
from app.schemas import NotificationPayload
from app.services.email import send_notification_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_worker():
    redis_client = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        decode_responses=True,
    )

    logger.info(f"Connected to Redis. Listening on queue: '{settings.REDIS_QUEUE_NAME}'...")

    while True:
        try:
            result = await redis_client.blpop(settings.REDIS_QUEUE_NAME, timeout=0)

            if result is None:
                continue

            queue_name, raw_message = result

            payload_dict = json.loads(raw_message)

            validated_payload = NotificationPayload(**payload_dict)

            await send_notification_email(validated_payload)
            logger.info(f"Successfully processed email for {validated_payload.email}")
        except (RedisTimeoutError, TimeoutError):
            continue
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse invalid JSON from Redis: {e}")

        except ValidationError as e:
            logger.error(f"Payload validation failed! Bad payload data: {e}")

        except Exception as e:
            logger.error(f"Unexpected error while processing job: {e}")


if __name__ == "__main__":
    asyncio.run(run_worker())