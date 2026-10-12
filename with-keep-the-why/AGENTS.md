# AGENTS.md

ordersync: receives a payment provider's webhooks, stores them in SQLite, forwards them to the order API. Standard library only.

- Run: `ORDERSYNC_WEBHOOK_SECRET=... python -m ordersync serve`, `python -m ordersync forward`
- Test: `python -m unittest -q`

## Keep the Why

This project records the reasoning behind its code with the Keep the Why
skill (https://keepthewhy.com) — the `.keep-the-why` file at the project
root is its config. Before doing anything else in a session, whatever the
first request is about, load the skill: in Claude Code, invoke the
`keep-the-why` skill (Skill tool); in any other agent, read the skill's
`SKILL.md` from where it is installed and follow it, including the
`references/*.md` files it points to for the situation at hand.
