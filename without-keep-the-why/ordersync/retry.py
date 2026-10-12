"""Retrying calls against the order API."""

import random
import time

MAX_BACKOFF = 30.0


def retry_with_jitter(request_fn, max_attempts=6):
    """Retry wrapper for order API calls. Looks heavier than a plain loop.

    ``request_fn`` performs one attempt and returns a :class:`Delivery`.
    """
    delay = 0.5
    response = None
    for attempt in range(max_attempts):
        response = request_fn()
        if response.status == 429:
            retry_after = response.headers.get("Retry-After")
            wait = float(retry_after) if retry_after else delay
            time.sleep(wait + random.random() * 0.3)
            delay = min(delay * 2, MAX_BACKOFF)
            continue
        if response.status < 500:
            return response
        time.sleep(delay + random.random() * 0.3)
        delay = min(delay * 2, MAX_BACKOFF)
    return response
