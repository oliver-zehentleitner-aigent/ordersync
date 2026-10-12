"""Forwards stored events to the order API."""

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from .retry import retry_with_jitter

ORDER_API_URL = "https://orders.example.com/v2/events"
TIMEOUT = 30


@dataclass
class Delivery:
    status: int
    headers: dict = field(default_factory=dict)


def post_once(url, event, timeout=TIMEOUT):
    """One POST of ``event`` to ``url``; HTTP errors become a Delivery, not an exception."""
    body = json.dumps(event.payload).encode()
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": event.event_id,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return Delivery(response.status, dict(response.headers))
    except urllib.error.HTTPError as error:
        return Delivery(error.code, dict(error.headers))


def forward(event, url=ORDER_API_URL, timeout=TIMEOUT, post=post_once):
    """Deliver one event to the order API, retrying as the API asks."""
    return retry_with_jitter(lambda: post(url, event, timeout))


def forward_pending(store, url=ORDER_API_URL, post=post_once):
    """Forward every event the store has not marked as forwarded yet."""
    delivered = 0
    for event in store.pending():
        result = forward(event, url, post=post)
        if result is not None and 200 <= result.status < 300:
            store.mark_forwarded(event.event_id)
            delivered += 1
    return delivered
