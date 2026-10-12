# Forwarding

## Forwards wait up to 30 seconds for the order API

**Id:** 3c21af9f-5913-446b-8498-a52845dcf3bc
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** incident 2026-07-03, duplicate orders after a 5-second timeout; the order API team's latency figures from the same review
**Revisit when:** the order API's p99 under load drops well below 10 seconds, or it starts honouring `Idempotency-Key` for longer than a minute
**See:** forwarding.md#the-idempotency-key-is-the-providers-event-id — 3788b232-2392-454a-9f99-7dcbc00b5615 — as of 2026-07-04

`TIMEOUT` in `ordersync/forwarder.py` is 30 seconds, and `forward()` passes it
to every attempt.

**Reason:** the order API processes a request to completion even when the
client has hung up, and its p99 under load is around 20 seconds. With a
5-second timeout, ordersync gave up on requests that were going to succeed,
retried them after the backoff, and the API — which deduplicates on
`Idempotency-Key` only within 60 seconds — created a second order for the
same event. 30 seconds covers the p99 with margin; a forward that takes longer
is an outage on their side, and the next run picks the event up again.

**Rejected alternative:** a 5-second timeout, to fail fast and keep the
forwarder's queue moving. It is what caused the duplicate orders.

**Rejected alternative:** no timeout at all. One hung connection then blocks a
worker until the operating system gives up, which is minutes.

## The idempotency key is the provider's event id

**Id:** 3788b232-2392-454a-9f99-7dcbc00b5615
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** design note at the start of the project, 2026-06-18

Every forward carries `Idempotency-Key: <event_id>`, the id the provider
assigned to the webhook, and nothing ordersync generates itself.

**Reason:** the provider's id is stable across its own redeliveries, so a
duplicate delivery that reaches the order API within its deduplication window
is recognised as the same order. A key minted by ordersync would differ per
attempt and defeat the purpose.

**Rejected alternative:** a hash of the payload. Two legitimately different
events can carry the same payload (a retry of a payment with the same amount),
and they must become two orders.
