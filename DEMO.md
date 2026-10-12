# Runbook for the three experiments

Each experiment is one prompt, run twice in fresh agent sessions: once in `without-keep-the-why/`, once in `with-keep-the-why/`. The code is identical. Only the second directory has `context/` and a `.keep-the-why` file, so only there does the agent get the reasoning that is not in the code.

Before recording: `claude --version`, the Keep the Why skill installed on the machine, a terminal with a large font, nothing else on screen. Run the prompt in the directory itself (`cd without-keep-the-why`, then `cd ../with-keep-the-why`), so the agent's project root is that directory. Reset the directory between takes (`git checkout -- . && git clean -fd` inside it) when the agent changed files.

## 1. Simplify code

**File on screen first:** `ordersync/retry.py`, cursor on `retry_with_jitter`, the docstring "Looks heavier than a plain loop." visible.

**Prompt:**

```
This retry_with_jitter wrapper looks over-engineered — a plain retry loop would do the same thing. Simplify it.
```

**Without:** the agent finds the `Retry-After` branch, cannot tell design from accident, and either simplifies or puts "drop the Retry-After handling" on the menu. Nothing in the repository says a plain loop was already tried.

**With:** the agent reads `context/retries.md`, cites it and declines: the simplification was considered on 2026-07-22 and not made, because the header varies per request. No code changes.

**Show afterwards:** the entry in `context/retries.md`, in particular the **Considered:** line — a change that produced no diff, no commit, no PR, and is recorded anyway.

## 2. Rejected alternative

**File on screen first:** `ordersync/webhooks.py`, the `handle()` method.

**Prompt:**

```
Incoming webhooks arrive twice sometimes and we forward them twice. Add deduplication.
```

**Without:** the quickest fix is a set of seen event ids in `WebhookHandler`. Nothing in the code says the service runs as four worker processes, so nothing stops the agent from building what already failed in production.

**With:** `context/webhooks.md` records the incident, names the set as the rejected alternative and the unique constraint in the store as the agreed replacement that has not been built yet. The agent builds the constraint, `INSERT OR IGNORE`, and says why not the set. Keep the Why may offer to update the entry ("has not been built yet" is now false) — that is the capture side of the skill, show it.

**Show afterwards:** the two diffs side by side, then the **Rejected alternative:** paragraph in `context/webhooks.md`.

## 3. Code review

Two branches, same change, one per directory: `review/without-keep-the-why` and `review/with-keep-the-why`. The change drops the forward timeout from 30 to 5 seconds ("fail fast") and switches the SQLite store to WAL with `synchronous=OFF` ("faster writes"); the test is adjusted.

**Prompt** (in `without-keep-the-why/`):

```
Review the branch review/without-keep-the-why against main before I merge it.
```

and in `with-keep-the-why/`:

```
Review the branch review/with-keep-the-why against main before I merge it.
```

**Without:** a tidy change, tests pass; at most a general remark about `synchronous=OFF` and durability.

**With:** the 5-second timeout contradicts `context/forwarding.md` — it is the exact value that caused duplicate orders on 2026-07-03, recorded as a rejected alternative — and the agent says so with the entry's reasoning. The WAL change is a new decision with no recorded why, and the agent asks for one (or offers to write the entry). Reasoning diff beside code diff.

**Show afterwards:** the entry in `context/forwarding.md`, and on GitHub the pull request from the `with-keep-the-why` branch with the review as a comment.

## What to expect, measured

Experiment 1 is the prompt of the [rejected-change experiment](https://github.com/oliver-zehentleitner/keep-the-why/tree/main/experiments/rejected-change) in the Keep the Why repository, run on 2026-09-08 with Claude Code and Claude Sonnet 5, ten fresh sessions per arm on the same `retry_with_jitter`: with the entry, 10 of 10 sessions declined to simplify; without it, 7 of 10 offered the rejected change as an option. The transcripts are in that directory. Experiments 2 and 3 were not run in bulk; the control answer varies between sessions, so record both takes and keep the one that shows the difference — and say in the description that it is one take.

Reset between takes, inside the directory you ran in:

```sh
git checkout -- . && git clean -fd
```
