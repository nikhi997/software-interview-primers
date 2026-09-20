# Chapter 4: The same shape, different problem

*[← Chapter 3](lld-chapter-3.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

Last chapter, you saw a pattern: pull out the choice, hand it in. The shortener stopped knowing which storage it had.

This chapter, fresh problem. New domain. See if you spot the shape.

## The problem

> "Our API is getting hammered. We need rate limiting. Each user can make 100 requests per minute. After that, reject them."

Simple. Token bucket: each user gets 100 tokens at the start of each minute. Each request consumes one. Out of tokens → rejected.

```python
import time

class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_state = {}  # user_id -> [tokens_left, window_start]

    def allow(self, user_id):
        now = time.time()
        if user_id not in self.user_state:
            self.user_state[user_id] = [self.max_requests, now]

        tokens, window_start = self.user_state[user_id]

        # window expired? reset
        if now - window_start >= self.window_seconds:
            self.user_state[user_id] = [self.max_requests - 1, now]
            return True

        if tokens > 0:
            self.user_state[user_id][0] = tokens - 1
            return True

        return False
```

Try it:

```python
>>> limiter = RateLimiter(max_requests=3, window_seconds=10)
>>> limiter.allow("alice")
True
>>> limiter.allow("alice")
True
>>> limiter.allow("alice")
True
>>> limiter.allow("alice")
False
```

Works. Three through, fourth blocked.

## The twist

A few weeks pass. Product comes back.

> "Token bucket isn't precise enough. We need **sliding window**. If the user made 100 requests in the last 60 seconds *at any moment*, block them. Not 'in the last calendar minute.'"

Different algorithm. Sliding window keeps a list of recent timestamps; on each request, drops anything older than 60s, then checks count.

You might be tempted to add a `mode` parameter:

```python
def __init__(self, max_requests=100, window_seconds=60, mode="token_bucket"):
    self.mode = mode
    ...

def allow(self, user_id):
    if self.mode == "token_bucket":
        # current logic
    elif self.mode == "sliding_window":
        # new logic
```

**Stop.**

Look at that code. Read it.

Now look at the storage code at the start of Chapter 3 — the version *before* we fixed it.

It's the same code. Different domain, same shape.

## The shape, again

Two algorithms doing the same job (deciding allow/deny) with different internals. A class being forced to dispatch between them. Same smell as storage.

Same fix. Pull each algorithm into its own class. Let the rate limiter hold one.

```python
class TokenBucket:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_state = {}

    def allow(self, user_id):
        now = time.time()
        if user_id not in self.user_state:
            self.user_state[user_id] = [self.max_requests, now]

        tokens, window_start = self.user_state[user_id]

        if now - window_start >= self.window_seconds:
            self.user_state[user_id] = [self.max_requests - 1, now]
            return True

        if tokens > 0:
            self.user_state[user_id][0] = tokens - 1
            return True

        return False


class SlidingWindow:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_timestamps = {}  # user_id -> list of recent timestamps

    def allow(self, user_id):
        now = time.time()
        if user_id not in self.user_timestamps:
            self.user_timestamps[user_id] = []

        cutoff = now - self.window_seconds
        self.user_timestamps[user_id] = [
            t for t in self.user_timestamps[user_id] if t > cutoff
        ]

        if len(self.user_timestamps[user_id]) < self.max_requests:
            self.user_timestamps[user_id].append(now)
            return True

        return False


class RateLimiter:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def allow(self, user_id):
        return self.algorithm.allow(user_id)
```

Usage:

```python
>>> limiter = RateLimiter(TokenBucket(100, 60))
>>> other = RateLimiter(SlidingWindow(100, 60))
```

Same shape as storage. Two algorithm classes with matching method signatures. One umbrella class that takes one of them.

## What this chapter is actually about

It's not about rate limiters.

It's about the moment you saw the `mode` parameter and felt something. *I've done this before.* That feeling is the actual skill. **Pattern recognition.**

Patterns aren't memorized. They're recognized. First time you do this, it takes effort. Second time, you smell the `if mode == "X"` ladder faster. Third time, you reach for the right shape before writing the bad version.

That's the muscle this chapter is building.

## What if you didn't spot it?

That's fine — the first variation rep is *supposed* to be hard. Re-read Ch3, then implement the rate limiter from scratch in a new file: both the bad if/else version *and* the extracted version. Run them. Feel the shape.

Patterns build through repetition, not intellectual understanding. You can't "get it once" and move on. You repeat until recognition becomes automatic.

## Before you turn the page

**Exercise 1:** Add a third algorithm — **Fixed Window Counter**. Time is divided into fixed N-second windows. Count requests in the current window. If count >= max, reject; otherwise allow and increment. Don't change `RateLimiter`.

**Exercise 2 (the real rep):** Look at your work codebase. Find one `if mode == "X" elif mode == "Y"` or `if type == "X" elif type == "Y"`. Write down what it is. Don't refactor yet — just *spot* it. That's the actual skill.

The shape is yours now.

---

<div align="right">

[Chapter 5 →](lld-chapter-5.md)

</div>
