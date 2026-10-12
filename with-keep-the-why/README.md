# ordersync

A small service that receives a payment provider's webhooks, stores them in SQLite and forwards them to an order API. Standard library only.

```sh
ORDERSYNC_WEBHOOK_SECRET=... python -m ordersync serve --port 8080   # receive webhooks
python -m ordersync forward                                          # forward stored events
python -m unittest -q                                                # tests
```

## Layout

- `ordersync/webhooks.py` — verifies the HMAC signature and stores each delivery
- `ordersync/store.py` — the SQLite event store
- `ordersync/forwarder.py` — POSTs events to the order API with an `Idempotency-Key`
- `ordersync/retry.py` — the retry wrapper the forwarder uses
- `ordersync/server.py` — the HTTP endpoint

## Why it is built this way

The reasoning behind the code lives in [`context/`](context/index.md), recorded with [Keep the Why](https://keepthewhy.com):

- [Retries](context/retries.md): why `retry_with_jitter` is not a plain retry loop.
- [Webhooks](context/webhooks.md): duplicate deliveries are filtered in the store, not in process memory, and the incident behind that.
- [Forwarding](context/forwarding.md): the 30-second timeout, and the provider's event id as idempotency key.
