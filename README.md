# Notification Service

A small async worker that listens on a Redis queue and turns ticketing
events into emails. It exists for one reason: the main [Ticketing
API](#) should never have to wait on an SMTP server to finish a request.

## Why this is a separate service

Email is the slowest, flakiest part of most backends — slow providers,
occasional timeouts, rate limits you don't control. If the ticketing API
sent emails inline, a slow SMTP connection would slow down ticket
purchases and account registrations, which is exactly the kind of thing
you don't want blocking a payment flow.

So the split is simple: the ticketing API pushes a small JSON payload
onto a Redis list (`notifications`) the instant something happens —
someone registers, buys a ticket, an event gets created. It doesn't wait
for a response. This service polls that same queue independently,
validates each payload, and sends the email. If this service is down,
restarting, or just slow, ticket purchases on the other side are
completely unaffected.

## How it works

1. `app/worker.py` runs an infinite loop using Redis `BLPOP` against the
   `notifications` queue — this is the actual service, not a request
   handler.
2. Each payload is validated against a Pydantic model
   (`NotificationPayload`) before anything happens with it. Malformed
   payloads are logged and skipped rather than crashing the worker.
3. `app/services/email.py` maps the event type to a subject/body and
   sends it via `aiosmtplib`.
4. `app/main.py` exposes a bare FastAPI app with a single `/health`
   route — worth being upfront about this: FastAPI here is a thin
   health-check surface, not the thing doing the real work. The worker
   process is what matters.

### Event types handled

- `USER_REGISTRATION` — email verification link
- `PASSWORD_RESET` — reset link
- `TICKET_PURCHASED` — purchase confirmation + QR code link
- `EVENT_CREATE_REMINDER` — new event announcement
- `EVENT_REMINDER` — "your event is tomorrow" reminder
- `PROMO_REMAINING_TICKETS` — low-inventory nudge

## Tech stack

FastAPI (health check only) · async Redis (`redis.asyncio`) · Pydantic ·
aiosmtplib · Docker

## Getting started

```bash
git clone <repo-url>
cd notification_service
cp .env.example .env   # fill in your SMTP + Redis details
docker compose up --build
```

This spins up only the worker container — there's no `redis` service
defined in this project's `docker-compose.yml`. It's meant to connect
to the *same* Redis instance the ticketing API uses. Locally that's
handled via `host.docker.internal`, which is already wired up in
`docker-compose.yml`; if you deploy this separately from the ticketing
API, point `REDIS_HOST` at wherever that Redis instance actually lives.

### Environment variables

| Variable          | Purpose                                  |
|--------------------|-------------------------------------------|
| `REDIS_HOST`       | Host of the shared Redis instance         |
| `REDIS_PORT`       | Redis port (default `6379`)               |
| `REDIS_QUEUE_NAME` | Queue to listen on (default `notifications`, must match the ticketing API) |
| `SMTP_HOST`        | SMTP server host                          |
| `SMTP_PORT`        | SMTP server port                          |
| `SMTP_USER`        | SMTP username                             |
| `SMTP_PASSWORD`    | SMTP password                             |
| `EMAILS_FROM`      | "From" address on outgoing emails         |

## Running tests

```bash
pytest
```

Currently covers payload validation (`NotificationPayload` schema). No
integration test against a live Redis/SMTP yet.

## Known limitations

- No retry or dead-letter handling for emails that fail to send — a
  failed send is logged and the message is gone.
- No exponential backoff or circuit breaker if the SMTP server is down;
  it'll just keep failing per-message until the server recovers.
- The FastAPI layer is intentionally minimal — don't read this as a
  FastAPI showcase, the interesting part is the async Redis consumer.

## License

MIT
