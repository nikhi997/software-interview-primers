# Chapter 3: When the class needs to stop knowing

*[← Chapter 2](lld-chapter-2.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

End of last chapter, we had a clean shortener. One thing was still hardcoded: the storage. `_save` opens a file. `_load` reads a file. JSON, with a filename. Baked in.

A new requirement lands.

> "We're going to production. We want to use Redis instead of a JSON file. Also, for our tests, we want a version that just keeps everything in memory and never touches disk."

Three storage options. Same shortener.

---

## The obvious move

Most people do this first. Add a switch.

```python
class URLShortener:
    def __init__(self, backend="file", filename="urls.json", redis_client=None):
        self.backend = backend
        self.filename = filename
        self.redis_client = redis_client
        self.urls = {}
        self.clicks = {}
        self._load()

    def _save(self):
        if self.backend == "file":
            with open(self.filename, "w") as f:
                json.dump({"urls": self.urls, "clicks": self.clicks}, f)
        elif self.backend == "redis":
            self.redis_client.set("urls", json.dumps(self.urls))
            self.redis_client.set("clicks", json.dumps(self.clicks))
        elif self.backend == "memory":
            pass  # already in memory

    def _load(self):
        if self.backend == "file":
            try:
                with open(self.filename) as f:
                    data = json.load(f)
                    self.urls = data.get("urls", {})
                    self.clicks = data.get("clicks", {})
            except FileNotFoundError:
                pass
        elif self.backend == "redis":
            self.urls = json.loads(self.redis_client.get("urls") or "{}")
            self.clicks = json.loads(self.redis_client.get("clicks") or "{}")
        elif self.backend == "memory":
            pass
```

It works. Three backends. One shortener. Ship it?

---

## Look at it before you ship

Read `_save`. It does three different things in three different `if` branches. You can't read it and answer the question *"what does saving do?"* — you have to ask back, *"saving which kind?"*

Read `__init__`. It takes `backend`, `filename`, AND `redis_client`. If `backend="file"`, the `redis_client` is dead weight. If `backend="redis"`, the `filename` is dead weight. The constructor signature is half-lying no matter how you call it.

Now imagine the next requirement: *"We also need Postgres."*

You'd go into `_save`, add an `elif`. Into `_load`, add another `elif`. Into `__init__`, add a `postgres_connection` parameter that's irrelevant unless `backend="postgres"`. Three places to touch for one new backend. And the new parameter joins the pile of "ignore me unless you're a certain kind of shortener" arguments.

And testing — the worst part. To test the shortener's logic, you need a working file system, or a real Redis, or mocks of both. The shortener and the storage are welded together. There's no way to exercise the shortener in isolation.

This is the smell. It works. It's also wrong.

---

## What is the shortener actually trying to do?

Step back. When `_save` runs, what does the shortener *need*?

It needs to say: *"here is some data. Make it durable somehow. I don't care how."*

When `_load` runs, it needs: *"give me back the data, if any."*

That's it. The shortener doesn't care if the data ends up in a file, in Redis, in Postgres, or written on a napkin. It just needs *something* that can save and load.

So the problem isn't that we need three implementations — we do. The problem is that the *shortener* is doing the choosing. It shouldn't. The shortener should know shortener things: codes, URLs, clicks. Storage is a different concern, and it's not the shortener's job to dispatch between options.

---

## The move

Take storage *out* of the shortener. Give it its own classes. Then *hand one* to the shortener.

```python
class FileStorage:
    def __init__(self, filename):
        self.filename = filename

    def save(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f)

    def load(self):
        try:
            with open(self.filename) as f:
                return json.load(f)
        except FileNotFoundError:
            return {"urls": {}, "clicks": {}}


class MemoryStorage:
    def __init__(self):
        self.data = {"urls": {}, "clicks": {}}

    def save(self, data):
        self.data = data

    def load(self):
        return self.data


class RedisStorage:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def save(self, data):
        self.redis_client.set("shortener_data", json.dumps(data))

    def load(self):
        raw = self.redis_client.get("shortener_data")
        if raw is None:
            return {"urls": {}, "clicks": {}}
        return json.loads(raw)
```

Three classes. Each one knows exactly one way to save and load. Each has the same two methods: `save(data)` and `load()`. That's the shape they share.

Now watch what happens to the shortener:

```python
class URLShortener:
    def __init__(self, storage):
        self.storage = storage
        data = self.storage.load()
        self.urls = data.get("urls", {})
        self.clicks = data.get("clicks", {})

    def _save(self):
        self.storage.save({"urls": self.urls, "clicks": self.clicks})

    # shorten, expand, click_count, delete — all unchanged from Ch2
```

That's the whole shortener now. No `if`. No `backend` argument. No filename. No redis client. Just `storage`, whatever it happens to be.

Usage:

```python
>>> s1 = URLShortener(FileStorage("urls.json"))
>>> s2 = URLShortener(MemoryStorage())
>>> s3 = URLShortener(RedisStorage(my_redis))
```

Three shorteners. Three different storage backends. *Same shortener class.*

---

## What this bought us

**1. The shortener stopped knowing.** It doesn't know what kind of storage it has. It doesn't have to. It just calls `.save(data)` and `.load()` on whatever was given to it.

**2. Adding a fourth backend is one new class.** Write `PostgresStorage` with a `save` and a `load`. The shortener doesn't change. Not one line.

**3. Testing got easy.** Want to test the shortener without touching any real storage? Pass it `MemoryStorage()`. The shortener behaves identically. No mocks, no file system, no Redis instance running.

**4. The constructors stopped lying.** `FileStorage(filename)` takes a filename — because it needs one. `RedisStorage(redis_client)` takes a client — because it needs one. Every parameter on every class is real.

---

## The deeper principle

What we just did has a one-line description that's worth memorizing:

> The shortener doesn't *use a file*. The shortener *uses a storage*. The storage *happens to be* a file.

The shortener depends on a *role* — "something that can save and load" — not on a *specific implementation* like a JSON file. The role is what stays. The implementation is what swaps.

When you find yourself writing `if backend == "X" elif backend == "Y"`, that's almost always the signal that one class has been forced to know about choices it shouldn't be making. The fix is the same fix every time: extract the choices into their own classes, and hand the right one in.

---

## A small Python note

You might notice we didn't declare anything that says "FileStorage, MemoryStorage, and RedisStorage all have a `save` method and a `load` method." We just wrote three classes that happen to have those methods, and the shortener calls them on whatever it gets.

> 💡 **Python concept — duck typing**
> The saying goes: *if it walks like a duck and quacks like a duck, it's a duck.* Python doesn't ask "is this a Storage?" — it asks "does this thing have a `save` and a `load` I can call?" If yes, it works. The three storage classes share a shape because *we wrote them to*. That's the whole contract. There's no formal interface declaration anywhere.
> The upside: less boilerplate, less ceremony. The downside: if you mistype a method name in one of the classes, you won't find out until runtime, when the shortener calls a method that doesn't exist.

---

## The shape has a name

What you just built is a pattern with a name. It's called the **Strategy pattern**.

The shortener has one job — track URLs and clicks — and it delegates a *different* job (storage) to a separate object whose only purpose is to do that job. The shortener doesn't know which strategy it has. It just uses it.

The shape, in five lines:

1. A class has a choice to make about *how* to do something.
2. Instead of making the choice with `if/else`, extract each variant into its own class.
3. All the variants share the same method signatures.
4. The original class takes one of the variants as a parameter.
5. From then on, it just *uses* whatever it was given.

If you can do the shape, you've learned the pattern. The label is filing-cabinet trivia — useful when talking to engineers, useless when writing code. The shape is the actual thing.

---

## Before you turn the page

**Exercise:** Add a new storage class. Pick one:

- **`EncryptedFileStorage(filename, key)`** — encrypts the JSON before writing, decrypts on read. (You can use a toy encryption — e.g., XOR each byte with the key. Don't use this for real secrets.)
- **`LoggingFileStorage(filename)`** — wraps a file save/load with `print` statements showing what was saved and what was loaded.
- **`DualStorage(primary, backup)`** — takes two storages. On save, writes to both. On load, tries primary first, falls back to backup if primary returns empty.

Pick whichever sounds interesting. The check on yourself: **did you have to change `URLShortener` at all to add it?** If you did, something's off — the shortener should be untouched.

Bonus reflection question, no code required: in the `DualStorage` option above — that class itself has `save` and `load` methods, and it takes two other storages. So `DualStorage` is *both* a storage AND a consumer of storages. Sit with that for a second. It's a hint about something powerful that we'll do more of later.

---

<div align="right">

[Chapter 4 →](lld-chapter-4.md)

</div>
