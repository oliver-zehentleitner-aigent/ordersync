import unittest
from unittest import mock

from ordersync.forwarder import Delivery
from ordersync.retry import retry_with_jitter


class RetryWithJitterTests(unittest.TestCase):
    def setUp(self):
        self.sleeps = []
        patcher_sleep = mock.patch("ordersync.retry.time.sleep", self.sleeps.append)
        patcher_random = mock.patch("ordersync.retry.random.random", return_value=0.0)
        patcher_sleep.start()
        patcher_random.start()
        self.addCleanup(patcher_sleep.stop)
        self.addCleanup(patcher_random.stop)

    def test_success_returns_at_once(self):
        result = retry_with_jitter(lambda: Delivery(200))
        self.assertEqual(result.status, 200)
        self.assertEqual(self.sleeps, [])

    def test_client_error_is_not_retried(self):
        calls = []
        result = retry_with_jitter(lambda: calls.append(1) or Delivery(400))
        self.assertEqual(result.status, 400)
        self.assertEqual(len(calls), 1)

    def test_429_waits_for_retry_after(self):
        responses = iter([Delivery(429, {"Retry-After": "7"}), Delivery(200)])
        result = retry_with_jitter(lambda: next(responses))
        self.assertEqual(result.status, 200)
        self.assertEqual(self.sleeps, [7.0])

    def test_server_errors_back_off_exponentially(self):
        responses = iter([Delivery(503), Delivery(503), Delivery(503), Delivery(201)])
        result = retry_with_jitter(lambda: next(responses))
        self.assertEqual(result.status, 201)
        self.assertEqual(self.sleeps, [0.5, 1.0, 2.0])

    def test_gives_up_after_max_attempts(self):
        result = retry_with_jitter(lambda: Delivery(500), max_attempts=3)
        self.assertEqual(result.status, 500)
        self.assertEqual(len(self.sleeps), 3)


if __name__ == "__main__":
    unittest.main()
