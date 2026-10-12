# ordersync — the same project twice, once with Keep the Why

[![Keep the Why · live](https://oliver-zehentleitner-aigent.github.io/ordersync/keep-the-why-dashboard/badge-entries.svg)](https://oliver-zehentleitner-aigent.github.io/ordersync/keep-the-why-dashboard/)

`ordersync` is a small service: it receives a payment provider's webhooks, stores them in SQLite and forwards them to an order API. Standard library only, eleven tests. This repository holds it twice, with identical code:

| Directory | What is in it |
|---|---|
| [`without-keep-the-why/`](without-keep-the-why/) | the code and its tests, nothing else |
| [`with-keep-the-why/`](with-keep-the-why/) | the same code and tests, plus [`context/`](with-keep-the-why/context/index.md): the reasoning behind three places in the code, recorded with [Keep the Why](https://keepthewhy.com) |

It exists for three experiments. Each gives a coding agent the same task in both directories; the difference is whether the reasoning that is not in the code is available to it. [`DEMO.md`](DEMO.md) is the runbook: the prompt to type, where, and what to look for.

1. **Simplify code.** `retry_with_jitter` looks over-engineered. It isn't: the order API's `Retry-After` varies per request, and a plain loop was already tried and dropped. No commit records that, because nothing was changed. [`context/retries.md`](with-keep-the-why/context/retries.md) does.
2. **Rejected alternative.** "Webhooks arrive twice sometimes, add deduplication." The obvious fix, a set of seen ids in the handler, shipped once and caused an incident: the service runs as four worker processes. [`context/webhooks.md`](with-keep-the-why/context/webhooks.md) records the incident, the rejected set and the agreed replacement.
3. **Code review.** The branches `review/without-keep-the-why` and `review/with-keep-the-why` carry the same small change: a 5-second forward timeout and a faster SQLite journal mode. One half contradicts a recorded decision ([`context/forwarding.md`](with-keep-the-why/context/forwarding.md)), the other is a new decision without a recorded why.

The dashboard of the `with-keep-the-why/` directory is published on GitHub Pages: the entries, their Git history, the graph. The linter runs on every push.

```sh
cd with-keep-the-why && python -m unittest -q    # or without-keep-the-why
```
