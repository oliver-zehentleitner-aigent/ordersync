import unittest

from ordersync.store import Event, EventStore


class EventStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = EventStore()
        self.addCleanup(self.store.close)

    def test_record_and_pending(self):
        self.store.record(Event("evt_1", "payment.completed", {"id": "evt_1", "amount": 1200}))
        self.store.record(Event("evt_2", "payment.refunded", {"id": "evt_2", "amount": 300}))
        pending = self.store.pending()
        self.assertEqual([e.event_id for e in pending], ["evt_1", "evt_2"])
        self.assertEqual(pending[0].payload["amount"], 1200)

    def test_mark_forwarded_removes_from_pending(self):
        self.store.record(Event("evt_1", "payment.completed", {"id": "evt_1"}))
        self.store.mark_forwarded("evt_1")
        self.assertEqual(self.store.pending(), [])
        self.assertEqual(self.store.count(), 1)


if __name__ == "__main__":
    unittest.main()
