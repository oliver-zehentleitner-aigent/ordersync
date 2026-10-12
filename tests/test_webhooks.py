import hashlib
import hmac
import json
import unittest

from ordersync.store import EventStore
from ordersync.webhooks import SignatureError, WebhookHandler

SECRET = "test-secret"


def signed(payload):
    body = json.dumps(payload).encode()
    return body, hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()


class WebhookHandlerTests(unittest.TestCase):
    def setUp(self):
        self.store = EventStore()
        self.addCleanup(self.store.close)
        self.handler = WebhookHandler(self.store, SECRET)

    def test_valid_delivery_is_stored(self):
        body, signature = signed({"id": "evt_1", "type": "payment.completed", "amount": 1200})
        event = self.handler.handle(body, signature)
        self.assertEqual(event.event_id, "evt_1")
        self.assertEqual(self.store.count(), 1)

    def test_bad_signature_is_rejected(self):
        body, _ = signed({"id": "evt_1", "type": "payment.completed"})
        with self.assertRaises(SignatureError):
            self.handler.handle(body, "0" * 64)
        self.assertEqual(self.store.count(), 0)

    def test_missing_signature_is_rejected(self):
        body, _ = signed({"id": "evt_1", "type": "payment.completed"})
        with self.assertRaises(SignatureError):
            self.handler.handle(body, None)


if __name__ == "__main__":
    unittest.main()
