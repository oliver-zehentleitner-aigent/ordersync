# AGENTS.md

ordersync: receives a payment provider's webhooks, stores them in SQLite, forwards them to the order API. Standard library only.

- Run: `ORDERSYNC_WEBHOOK_SECRET=... python -m ordersync serve`, `python -m ordersync forward`
- Test: `python -m unittest -q`
