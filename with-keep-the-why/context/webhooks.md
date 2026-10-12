# Webhooks

## Duplicate deliveries are filtered in the store, not in process memory

**Id:** 5d5a0733-ba10-4dff-8732-956d659a6910
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** incident 2026-08-14, duplicate forwards after a provider retry storm; team decision the same week
**Revisit when:** ordersync runs as a single process, or the store moves off SQLite
**See:** forwarding.md#the-idempotency-key-is-the-providers-event-id — 3788b232-2392-454a-9f99-7dcbc00b5615 — as of 2026-08-15

The provider redelivers a webhook whenever it does not get a 2xx within its
own timeout, and it may redeliver the same event for up to 72 hours. Duplicate
deliveries are to be filtered where the event is stored: a unique constraint on
`event_id` in the `events` table, with the insert ignoring a duplicate and
`record()` reporting whether the event was new. The store is the one place all
workers share.

**Reason:** ordersync runs as four worker processes behind the reverse proxy,
and the provider's retries land on whichever worker is free. A filter that
lives in one process sees only a quarter of the deliveries. The store already
holds every event, so the constraint costs one index and nothing else, and it
survives a restart, which matters when redeliveries arrive for three days.

**Rejected alternative:** a set of seen event ids held in the handler. It was
built and shipped first, and it was the cause of the incident: each worker had
its own set, so a redelivery that hit another worker went through and was
forwarded a second time. Reverted the same day. The constraint is the agreed
replacement; it has not been built yet.

**Rejected alternative:** deduplicating at forwarding time, by asking the
order API whether it has seen the idempotency key. It would move the problem
to the slow side of the service and add a round trip per event.
