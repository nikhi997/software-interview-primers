# Chapter 8: Wrapping behavior around existing classes

*[← Chapter 7](lld-chapter-7.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

Remember the bonus reflection at end of Ch3? It said: *"DualStorage is both a storage AND a consumer of storages. Sit with that."*

Now we use it.

## The problem

Two new requirements. Different days, same week.

**A:** *"Encrypt the URLs on disk. Privacy is important."* This should work for *any* storage — file, Redis, future Postgres.

**B:** *"Log every save and load with a timestamp. For debugging."* Also for any storage.

The naive approach: `EncryptedFileStorage`, `EncryptedRedisStorage`, `LoggedFileStorage`, `LoggedRedisStorage`, `EncryptedLoggedFileStorage`...

That's a combinatorial explosion. Two cross-cutting concerns × N storages = 2N classes. Add a third (compression) and it's 4N. This dies fast.

## What the requirements really are

Look again. Both say "for any storage." Both add a *layer* on top of whatever storage already exists.

Encryption: take incoming data, encrypt it, hand to the underlying storage. On load, get encrypted data from the underlying storage, decrypt, return.

Logging: print "saving..." then call the underlying storage's save. Same for load.

Neither *replaces* storage. Each one *wraps* a storage.

## The move

A wrapper class with the same shape as a storage (`save` and `load`), that takes another storage in its constructor. The wrapper does its extra work, then delegates.

```python
import json


class EncryptedStorage:
    def __init__(self, inner_storage, key):
        self.inner = inner_storage
        self.key = key

    def save(self, data):
        encrypted = self._encrypt(data)
        self.inner.save(encrypted)

    def load(self):
        encrypted = self.inner.load()
        return self._decrypt(encrypted)

    def _encrypt(self, data):
        # toy XOR — DO NOT use for real secrets
        text = json.dumps(data)
        return {"_encrypted": [ord(c) ^ self.key for c in text]}

    def _decrypt(self, encrypted):
        if "_encrypted" not in encrypted:
            return encrypted
        text = "".join(chr(b ^ self.key) for b in encrypted["_encrypted"])
        return json.loads(text)


class LoggedStorage:
    def __init__(self, inner_storage, label="storage"):
        self.inner = inner_storage
        self.label = label

    def save(self, data):
        print(f"[{self.label}] saving {len(str(data))} bytes")
        self.inner.save(data)

    def load(self):
        print(f"[{self.label}] loading")
        return self.inner.load()
```

Usage:

```python
>>> raw = FileStorage("urls.json")
>>> encrypted = EncryptedStorage(raw, key=42)
>>> logged = LoggedStorage(encrypted, label="urls")
>>> s = URLShortener(logged)
>>> s.shorten("https://example.com", "ex")
[urls] saving 47 bytes
'ex'
>>> s.expand("ex")
[urls] loading
'https://example.com'
```

`logged` wraps `encrypted` wraps `raw`. When `s._save` calls `logged.save(data)`:

1. `logged.save` prints the log line, calls `encrypted.save(data)`
2. `encrypted.save` encrypts, calls `raw.save(encrypted_data)`
3. `raw.save` writes encrypted data to disk

The shortener doesn't know any of this. It still just calls `self.storage.save(data)`. The storage *happens to be* three layers wrapped together.

## What this bought us

**1. No combinatorial explosion.** Two wrappers + N storages = N + 2 classes total, not 2N. Linear, not multiplicative.

**2. Wrappers compose.** Logged on top of encrypted on top of file. Or encrypted on top of dual on top of two redises. Mix and match.

**3. Each wrapper has one responsibility.** Encryption knows encryption. Logging knows logging. Neither cares what storage they wrap.

**4. Nothing existing changed.** The shortener didn't change. The original storage classes didn't change. You added behavior without modifying anything.

## The shape

Both wrappers have the same structure:

1. Implement the same interface as the wrapped thing (here, `save` and `load`)
2. Take an instance of that interface in the constructor
3. Each method does its extra work, then calls the wrapped instance's method
4. From outside, the wrapper looks identical to the underlying thing

This is the **Decorator pattern**. "Decorator" here means "decoration" — added behavior — not the Python `@decorator` syntax (which is related but a different thing that shares the name).

## Decorator vs other shapes you know

- **Strategy:** "Pick one of N algorithms." Strategies don't wrap each other.
- **Observer:** "Tell many listeners about an event." Listeners don't wrap each other.
- **State:** "Behavior changes as lifecycle progresses." States replace each other.
- **Decorator:** "Add behavior to an existing object without modifying it." Decorators *wrap* each other.

Visual: decorators stack like Russian dolls. Innermost is the original. Each layer outside adds something.

## A real-world example you've seen

Web servers do this. An HTTP request goes through *middleware*:

```
request → auth middleware → logging middleware → rate limit middleware → your handler
```

Each middleware is a decorator. It does its job, then calls the next thing. The next thing doesn't know it's being wrapped.

## Before you turn the page

**Exercise 1:** Add a `CompressionStorage` wrapper. On save, compress (use `gzip` from the standard library). On load, decompress. Combine with `EncryptedStorage` and `LoggedStorage`. Order matters — encrypt-then-compress vs compress-then-encrypt give different results. Try both, notice.

**Exercise 2:** Add a `CachingStorage` wrapper. On load, return cached data if you have it; otherwise call the inner storage and cache the result. On save, update the cache AND call the inner storage. Think about when the cache should invalidate.

**Exercise 3 (recognition):** In any web framework you've used (Express, Django, Flask, Spring), middleware *is* Decorator. Each middleware function takes the next handler and returns a new handler.

---

<div align="right">

[Chapter 9 →](lld-chapter-9.md)

</div>
