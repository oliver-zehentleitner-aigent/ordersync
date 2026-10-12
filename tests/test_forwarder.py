import unittest
from unittest import mock

from ordersync.forwarder import Delivery, forward_pending
from ordersync.store import Event, EventStore


class ForwardPendingTests(unittest.TestCase):
    def test_delivered_events_are_marked(self):
        store = EventStore()
        self.addCleanup(store.close)
        store.record(Event("evt_1", "payment.completed", {"id": "evt_1"}))
        store.record(Event("evt_2", "payment.completed", {"id": "evt_2"}))
        posted = []

        def fake_post(url, event, timeout):
            posted.append((event.event_id, timeout))
            return Delivery(202)

        with mock.patch("ordersync.retry.time.sleep"):
            delivered = forward_pending(store, post=fake_post)
        self.assertEqual(delivered, 2)
        self.assertEqual(store.pending(), [])
        self.assertEqual(posted, [("evt_1", 30), ("evt_2", 30)])


if __name__ == "__main__":
    unittest.main()
