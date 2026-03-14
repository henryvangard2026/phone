"""
phoneconsumer.py
-----------------
Consumes phone CRUD events from RabbitMQ and writes an audit trail.

Run this in a separate terminal BEFORE (or alongside) phone.py:

    python phoneconsumer.py

Output
------
  Console  : pretty-printed event lines
  audit.log: one JSON record per line (append-only)

Requires:
    pip install pika
    Docker:  docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
"""

import pika
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
QUEUE_NAME    = "phoneEvents"
AUDIT_LOG     = "audit.log"


# set up logging to both console and audit.log
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),          # console
        logging.FileHandler(AUDIT_LOG, mode="a"),   # audit.log  (append)
    ],
)

log = logging.getLogger(__name__)


_EVENT_ICONS = {
    "ADD":    "✚",
    "UPDATE": "✎",
    "DELETE": "✖",
}

def _format_event(msg: dict) -> str:
    """Return a human-readable single-line summary of the event."""
    icon      = _EVENT_ICONS.get(msg.get("event", ""), "?")
    event     = msg.get("event", "UNKNOWN")
    phone_id  = msg.get("phone_id", "?")
    ts        = msg.get("timestamp", "")
    details   = msg.get("details", {})

    # Build a compact details string
    detail_str = "  |  ".join(f"{k}={v}" for k, v in details.items())

    return f"{icon} [{event}]  phone_id={phone_id}  ts={ts}  {detail_str}"



def _on_message(channel, method, properties, body):
    """
    Called by pika for every message delivered from the queue.

    Workflow:
      1. Decode JSON
      2. Log to console + audit.log
      3. ACK the message so RabbitMQ removes it from the queue
    """
    try:
        msg = json.loads(body)
    except json.JSONDecodeError as e:
        log.error(f"[CONSUMER] Could not decode message body: {e}  raw={body!r}")
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    log.info(_format_event(msg))

    # ── ACK: tell RabbitMQ the message was processed successfully ─────────────
    channel.basic_ack(delivery_tag=method.delivery_tag)


# ── Consumer startup ──────────────────────────────────────────────────────────

def start_consumer():
    """Connect to RabbitMQ and block-consume phoneEvents forever."""

    log.info(f"[CONSUMER] Connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT} ...")

    try:
        params     = pika.ConnectionParameters(
            host      = RABBITMQ_HOST,
            port      = RABBITMQ_PORT,
            heartbeat = 60,
            blocked_connection_timeout = 30,
        )
        connection = pika.BlockingConnection(params)
        channel    = connection.channel()

        # Declare queue (idempotent — safe to call even if already exists)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        # prefetch_count=1: don't dispatch a new message until this consumer ACKs
        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(
            queue        = QUEUE_NAME,
            on_message_callback = _on_message,
            auto_ack     = False,   # we ACK manually inside _on_message
        )

        log.info(f"[CONSUMER] Listening on queue '{QUEUE_NAME}' — press Ctrl+C to stop.")
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        log.error(f"[CONSUMER] Cannot connect to RabbitMQ: {e}")
        log.error("[CONSUMER] Is RabbitMQ running?  Try:  docker start rabbitmq")
        sys.exit(1)

    except KeyboardInterrupt:
        log.info("[CONSUMER] Shutting down ...")
        try:
            connection.close()
        except Exception:
            pass


# main

if __name__ == "__main__":
    start_consumer()
