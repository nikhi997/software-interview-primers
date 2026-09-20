# Chapter 6: The thing there's only ever one of

*[← Chapter 5](lld-chapter-5.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

Different problem. You need a logger. Across your whole app — every file, every class — you want to write log messages somewhere consistent.

You write a class.

```python
class Logger:
    def __init__(self, filename="app.log"):
        self.filename = filename

    def log(self, message):
        with open(self.filename, "a") as f:
            f.write(f"{message}\n")
        print(message)
```

Now in your code:

```python
# in orders.py
logger = Logger()
logger.log("Order placed")

# in users.py
logger = Logger()
logger.log("User created")
```

It works. But you just created *two* `Logger` objects. They don't share state. If you change the filename on one, the other doesn't know.

You realize: you don't *want* multiple loggers. You want one. The whole app should write to the same logger, with the same config, with one place to change settings.

## The instinct

"What if I just make `logger` a global?"

```python
# in setup.py
logger = Logger()

# everywhere else
from setup import logger
logger.log("...")
```

That works. It's also a global variable, which brings its own problems (anyone can reassign it; constructed at import time; no control).

But the underlying urge is right: *one instance, shared everywhere.*

## The move

Build a class that *enforces* "only ever one." The first time you ask for it, it creates an instance. Every time after, it returns the same one.

```python
class Logger:
    _instance = None

    def __new__(cls, filename="app.log"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.filename = filename
        return cls._instance

    def log(self, message):
        with open(self.filename, "a") as f:
            f.write(f"{message}\n")
        print(message)
```

> 💡 **Python notes — `__new__`, `cls`, class attributes**
> `__new__` is a dunder that runs *before* `__init__`. Its job is actually creating the object. Normally Python uses a default `__new__` and you never touch it. Here we override it to control creation: if the class already has an instance stored, return that instance instead of making a new one.
> `cls` is the class itself (vs `self`, which is an instance). `cls._instance` is a class-level attribute, shared across all calls. Like a static variable belonging to the class, not any specific instance.
> `super().__new__(cls)` calls the default `__new__` from the parent class to actually allocate the object. Without this line, the override would loop forever.

Usage:

```python
>>> a = Logger("app.log")
>>> b = Logger("doesnt_matter.log")
>>> a is b
True
```

`a` and `b` are the *same object*. The second `Logger(...)` call just returns the existing instance. The filename argument was silently ignored — there was already a logger.

## What this is and isn't

This pattern is the **Singleton**. It enforces "exactly one of this class, ever."

Honest take: Singleton is controversial. Many experienced engineers consider it an anti-pattern. The reasons:

1. **It's a global in a costume.** Singletons are accessed from anywhere, which means dependencies become invisible. A class using `Logger()` doesn't *declare* that it needs a logger — it just reaches out and grabs one.

2. **Testing gets harder.** Singletons persist across tests unless you explicitly reset them. Forget to reset, tests leak state into each other.

3. **The filename trap above.** `b = Logger("doesnt_matter.log")` silently ignored its argument. That's surprising behavior — `b` looks like it configures a new logger but doesn't.

So why teach it? Two reasons:

1. **Interviewers ask about it.** It's a named pattern. You need to know it.
2. **Sometimes it's the right answer.** When you genuinely have one shared resource (connection pool, config registry, logger) and the alternative is passing it through every constructor, Singleton can be cleaner.

The honest rule: **prefer dependency injection** (passing the logger in, like we passed `storage` to URLShortener). Use Singleton only when injection becomes impractical *and* you accept the tradeoffs.

## The Factory side

Related but different question. What if your logger has multiple types — file, console, JSON-structured, syslog — and you want to pick one based on config?

You don't want callers to know about all the types. They just want *a logger.*

```python
import json
import time


class FileLogger:
    def __init__(self, filename):
        self.filename = filename
    def log(self, message):
        with open(self.filename, "a") as f:
            f.write(f"{message}\n")


class ConsoleLogger:
    def log(self, message):
        print(message)


class JSONLogger:
    def __init__(self, filename):
        self.filename = filename
    def log(self, message):
        with open(self.filename, "a") as f:
            json.dump({"message": message, "time": time.time()}, f)
            f.write("\n")


def create_logger(config):
    if config["type"] == "file":
        return FileLogger(config["filename"])
    elif config["type"] == "console":
        return ConsoleLogger()
    elif config["type"] == "json":
        return JSONLogger(config["filename"])
    else:
        raise ValueError(f"Unknown logger type: {config['type']}")
```

Usage:

```python
>>> logger = create_logger({"type": "file", "filename": "app.log"})
>>> logger.log("Hello")
```

This is a **Factory function**. It hides construction details. Callers ask for "a logger configured this way" and get back something with a `log` method. They don't care which class.

## Factory vs Strategy — careful

These look similar but solve different problems.

**Strategy:** *"I have a job. I take an algorithm as a parameter. It does the job."* The algorithm is chosen by the caller and lives alongside the user.

**Factory:** *"I want an object configured a certain way. The factory builds it."* The factory hides *how* to build the object.

You can combine them. A factory can produce strategies — `create_rate_limiter(config)` returns a `TokenBucket` or `SlidingWindow` based on config; that gets passed to a `RateLimiter`. Normal.

## Before you turn the page

**Exercise 1:** Make `Logger` a singleton that takes a filename on first call, but raises an error if subsequent calls pass a *different* filename. (Hint: store on first creation, compare on later calls.)

**Exercise 2:** Write a factory function `create_storage(config)` for the storages from Ch3. Config might be `{"type": "file", "filename": "urls.json"}` or `{"type": "memory"}` or `{"type": "redis", "host": "localhost"}`.

**Exercise 3 (real-world rep):** Find a place in your codebase with `if type == "X" elif type == "Y"` scattered across multiple constructors. That's a factory waiting to happen.

---

<div align="right">

[Chapter 7 →](lld-chapter-7.md)

</div>
