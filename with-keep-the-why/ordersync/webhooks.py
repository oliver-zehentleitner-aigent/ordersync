"""Receiving the payment provider's webhooks."""

import hashlib
import hmac
import json

from .store import Event


class SignatureError(ValueError):
    """The webhook's signature does not match the shared secret."""


class WebhookHandler:
    """Verifies, parses and stores incoming webhook deliveries."""

    def __init__(self, store, secret):
        self._store = store
        self._secret = secret.encode()

    def verify(self, body, signature):
        expected = hmac.new(self._secret, body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature or ""):
            raise SignatureError("signature mismatch")

    def handle(self, body, signature):
        """Verify and store one delivery; returns the stored Event."""
        self.verify(body, signature)
        data = json.loads(body)
        event = Event(event_id=data["id"], kind=data["type"], payload=data)
        self._store.record(event)
        return event
