"""
Token-bucket rate limiter — the demo referenced in HLD Chapter 8.

The core idea in ~10 lines: a bucket holds up to `capacity` tokens and refills
at `refill_rate` tokens/sec. Each request takes one token. No token -> rejected
(your API would return HTTP 429). It allows short BURSTS (up to capacity) while
capping the SUSTAINED rate (refill_rate).

    python3 rate_limiter.py
"""

import time


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity          # max burst size (B)
        self.refill_rate = refill_rate    # sustained tokens/sec (R)
        self.tokens = float(capacity)     # start full
        self.last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def allow(self) -> bool:
        """Return True if the request is allowed (a token was available)."""
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


def demo() -> None:
    # 5-token bucket, refilling 2 tokens/sec.
    bucket = TokenBucket(capacity=5, refill_rate=2)

    print("Burst of 8 requests at once (bucket holds 5):")
    for i in range(1, 9):
        verdict = "ALLOW" if bucket.allow() else "  429 (rejected)"
        print(f"  req {i}: {verdict}")
    print("  -> first 5 allowed (the burst), rest rejected.\n")

    print("Wait 1 second (refills 2 tokens), then 3 more requests:")
    time.sleep(1)
    for i in range(1, 4):
        verdict = "ALLOW" if bucket.allow() else "  429 (rejected)"
        print(f"  req {i}: {verdict}")
    print("  -> 2 allowed (the refill), 3rd rejected.\n")

    print("Steady 2 req/sec matches the refill rate -> all allowed:")
    for i in range(1, 5):
        time.sleep(0.5)  # 2 per second
        verdict = "ALLOW" if bucket.allow() else "  429 (rejected)"
        print(f"  req {i}: {verdict}")


# In a real system the counters live in a SHARED store (e.g. Redis), not in
# process memory, so all edge servers agree on each client's usage. Otherwise a
# client gets their full quota PER server by spreading requests across the fleet.
# Redis even has atomic primitives to do this safely across many nodes.

if __name__ == "__main__":
    demo()
