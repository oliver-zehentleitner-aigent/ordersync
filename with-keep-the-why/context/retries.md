# Retries

## Why retry_with_jitter isn't a plain retry loop

**Id:** 0bdee002-ecc2-4212-a968-28616168caf0
**Type:** constraint
**Status:** active
**Evidence:** confirmed
**Source:** discovered while considering simplifying it, 2026-07-22

The order API's rate limiter answers 429 with a `Retry-After` header whose
value varies per request: it says how long this client has to wait before the
limiter resets, and that is rarely the same number twice. A fixed-delay retry
loop would frequently retry before the reset and get 429 again, and under load
every forwarder worker does that at once — repeated 429s instead of deliveries.
That is why `retry_with_jitter` in `ordersync/retry.py` reads the header and
sleeps for exactly that long, with a little jitter so the workers do not come
back in lockstep.

**Considered:** replacing the wrapper with a plain retry loop (fixed delay,
fixed attempts), since it looked like unnecessary complexity with nothing
documenting why. Not adopted once the `Retry-After` behaviour surfaced while
reviewing the change. No code changed, so this entry is the only trace.
