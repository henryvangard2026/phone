"""
phone_producer.py
-----------------
Publishes phone CRUD events to RabbitMQ.

Queue name : phone_events
Exchange   : default (direct)
Message    : JSON  { "event": "ADD|UPDATE|DELETE", "timestamp": "...", "phone_id": ..., "details": {...} }

Requires:
    pip install pika
    Docker:  docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
"""

import pika
import json
import logging
from datetime import datetime, timezone


# RabbitMQ setups

RABBITMQ_HOST  = "localhost"
RABBITMQ_PORT  = 5672
QUEUE_NAME     = "phone_events"


# Helper functions:

def _get_connection():
    """
    Return a blocking RabbitMQ connection.
    """
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        heartbeat=30,
        blocked_connection_timeout=10,
    )
    return pika.BlockingConnection(params)


def _publish(event: str, details: dict):
    """
    Build a message and publish it to the phone_events queue.

    Parameters
    ----------
    event    : "ADD" | "UPDATE" | "DELETE"
    phone_id : database id of the affected phone (None if unknown)
    details  : dict of phone fields relevant to the event
    """
    message = {
        "event":     event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details":   details,
    }

    try:
        connection = _get_connection()
        channel    = connection.channel()

        # durable=True: queue survives a RabbitMQ restart
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,  # survive broker restart
                content_type="application/json",
            ),
        )
        connection.close()
        logging.debug(f"[PRODUCER] Published {event} event for phone_id={details.get('id')}")

    except pika.exceptions.AMQPConnectionError as e:
        # this exception only gets logged without crashing the app
        logging.warning(f"[PRODUCER] RabbitMQ unavailable, event not published: {e}")


def publish_add(phone):
    """
    Call this after a phone is successfully added to the DB in phone.py's addPhone().
    """
    _publish(
        event    = "ADD",
        details  = {
            "id":            phone.id,    
            "brand":         phone.brand,
            "model":         phone.model,
            "os":            phone.os,
            "os_version":    str(phone.os_version),
            "serial_number": phone.serial_number,
            "imei":          phone.imei,
            "status":        phone.status,
            "workstation":   phone.workstation,
        },
    )


def publish_update(changed_fields: dict):
    """
    Call this after a phone is successfully updated ... in phone.py's updatePhone().

    Parameters
    ----------
    phone          : the SQLAlchemy Phone object (post-commit)
    changed_fields : dict of only the fields that changed, e.g.
                     {"status": "RETIRED", "workstation": "UNASSIGNED"}
    """
    _publish(event = "UPDATE", details=changed_fields,)  # publish only the changed fields


def publish_delete(snapshot: dict):
    """
    Call this before or after a phone is deleted ... in phone.py's deletePhone().

    Parameters
    ----------
    phone_id : the id of the deleted phone
    snapshot : dict of the phone's fields at time of deletion
    """
    _publish(event = "DELETE", details=snapshot,)   # publish the snapshot (before it got deleted),
                                                    # Python allows the dangling comma at the end

