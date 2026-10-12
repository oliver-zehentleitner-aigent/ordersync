# ordersync

[![Keep the Why · live](https://oliver-zehentleitner-aigent.github.io/ordersync/keep-the-why-dashboard/badge-entries.svg)](https://oliver-zehentleitner-aigent.github.io/ordersync/keep-the-why-dashboard/)

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

The [dashboard](https://oliver-zehentleitner-aigent.github.io/ordersync/keep-the-why-dashboard/) shows the entries with their Git history; the linter runs on every push.

## The same project without Keep the Why

The branch [`without-keep-the-why`](../../tree/without-keep-the-why) holds exactly this code and these tests, and nothing else: no `context/`, no `.keep-the-why`. It exists for three experiments that give a coding agent the same task on both branches — the difference is whether the reasoning that is not in the code is available to it. [`DEMO.md`](DEMO.md) is the runbook.

1. **Simplify code.** `retry_with_jitter` looks over-engineered. It isn't: the order API's `Retry-After` varies per request, and a plain loop was already tried and dropped. No commit records that, because nothing was changed. [`context/retries.md`](context/retries.md) does.
2. **Rejected alternative.** "Webhooks arrive twice sometimes, add deduplication." The obvious fix, a set of seen ids in the handler, shipped once and caused an incident: the service runs as four worker processes. [`context/webhooks.md`](context/webhooks.md) records the incident, the rejected set and the agreed replacement.
3. **Code review.** The pull requests from `review/faster-timeouts` (into `main`) and `review/faster-timeouts-without` (into `without-keep-the-why`) carry the same small change: a 5-second forward timeout and a faster SQLite journal mode. One half contradicts a recorded decision ([`context/forwarding.md`](context/forwarding.md)), the other is a new decision without a recorded why.
