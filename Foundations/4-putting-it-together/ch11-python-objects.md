# Chapter 11: The Python you're assumed to know — objects and idioms

*[← Chapter 10](ch10-python.md) · [Contents](../foundations-README.md)*

- [ ] **Mark as read**

The previous chapter handled data and iteration — the idioms you reach for *inside* a coding problem. This one is the other half: the Python you use to *model* things. The moment a problem has entities — a user, a money amount, a point on a board — you stop transforming lists and start defining types. Done clumsily, that means walls of boilerplate; done well, your objects behave like the language's own built-ins.

Same bargain as before: write the clunky version, feel exactly where it hurts, then reach for the idiom that removes the pain.

Core principle, once more: **feel the boilerplate before reaching for the idiom.**

---

## Dataclasses: the class that's mostly boilerplate

You need a small class to hold data. The manual version is a wall of `self.x = x`:

```python
class Point:
    def __init__(self, x, y, label=""):
        self.x = x
        self.y = y
        self.label = label

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, label={self.label!r})"

    def __eq__(self, other):
        return (self.x, self.y, self.label) == (other.x, other.y, other.label)
```

Every attribute is typed *three times* (parameter, then `self.x = x`), and you hand-wrote `__repr__` and `__eq__` just to get printing and comparison. That repetition is pure ceremony — and ceremony is where bugs hide (forget one field in `__eq__` and equality lies).

```python
from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float
    label: str = ""
```

That's the whole class. The `@dataclass` decorator generates `__init__`, `__repr__`, and `__eq__` from the fields you declared once.

> 💡 **Concept notes — `@dataclass` and what it generates**
> A **dataclass** auto-writes the boilerplate methods for a class that's mostly a bundle of fields. You declare each field once, with a type hint; the decorator builds `__init__`, a readable `__repr__`, and field-wise `__eq__`. Defaults work (`label: str = ""`); `frozen=True` makes instances immutable (and hashable, so they work as dict keys or set members). This is the direct answer to LLD's "replace primitive with object" — turning a bare tuple into a named, typed thing now costs three lines, so there's no excuse to pass `(x, y, label)` tuples around. In an interview, reaching for `@dataclass` to model entities reads as fluent and lets you skip writing constructors by hand.

---

## Dunder methods: make your objects behave like built-ins

You wrote a `Money` class, and now this happens:

```python
print(total)            # <__main__.Money object at 0x10f3c2a90>
a == b                  # False, even though both are $5.00
```

Useless printing, and equality compares *identity* (are they the same object?) instead of *value*. The pain is that your object is a second-class citizen — the language's own operators don't understand it. **Dunder** ("double underscore") methods are the hooks that fix that:

```python
class Money:
    def __init__(self, cents):
        self.cents = cents

    def __repr__(self):
        return f"${self.cents / 100:.2f}"

    def __eq__(self, other):
        return self.cents == other.cents

    def __lt__(self, other):
        return self.cents < other.cents

    def __add__(self, other):
        return Money(self.cents + other.cents)
```

Now `print(total)` shows `$5.00`, `a == b` compares value, `a + b` returns `Money`, and `sorted(prices)` just works because you defined `__lt__`.

> 💡 **Concept notes — the dunders worth knowing**
> Dunder methods let your class plug into Python's syntax and built-ins:
> - `__init__` (construct), `__repr__` (developer-readable string — define this one always), `__str__` (user-facing string).
> - `__eq__` / `__lt__` (comparison — `__lt__` alone unlocks `sorted()`, `min`, `max`).
> - `__len__` (so `len(obj)` works), `__getitem__` (so `obj[i]` and iteration work), `__iter__` / `__next__` (custom iteration).
> - `__enter__` / `__exit__` (context-manager protocol — next section), `__hash__` (use as dict key / set member).
> You saw `__new__` in the LLD Singleton. The mental model: Python's syntax (`+`, `==`, `[]`, `len`, `with`, `for`) is *sugar* that calls these methods. Implementing the right dunder makes your object indistinguishable from a built-in at the call site — which is the whole point of duck typing the LLD patterns leaned on.

---

## Context managers: never leak a resource

You open a file, a lock, a database connection. Each one must be released — even if the code in between raises. The defensive version is noisy and easy to get wrong:

```python
f = open("data.txt")
try:
    process(f)
finally:
    f.close()        # must remember this, every time, or the handle leaks
```

Forget the `finally` and a thrown exception leaks the file handle (the OS chapter's resource-leak pain, made concrete). The `with` statement guarantees cleanup:

```python
with open("data.txt") as f:
    process(f)
# f is closed here, automatically — even if process() raised
```

> 💡 **Concept notes — `with` and the context-manager protocol**
> A **context manager** is any object with `__enter__` (runs on entering the block, its return value is bound by `as`) and `__exit__` (runs on leaving — *always*, whether the block finished normally or raised). `with` is the sugar that calls them. It's the right tool for any *acquire-then-must-release* pair: files, `threading.Lock()` (the LLD concurrency appendix used `with self.lock:` for exactly this), database sessions, network connections. You can write your own with a class, or the lightweight way — `@contextlib.contextmanager` over a generator, where code before `yield` is setup and code after is teardown. The signal it sends: you don't leak resources, and you know cleanup must survive exceptions.

---

## Type hints: say what you mean

A function signature that tells you nothing:

```python
def process(data, config):
    ...
```

What is `data` — a list? a dict? of what? You find out by reading the whole body or crashing at runtime. **Type hints** put the answer in the signature:

```python
def process(rows: list[dict], config: Config) -> int:
    ...
```

> 💡 **Concept notes — type hints (and what they don't do)**
> Hints annotate parameters and returns: `name: str`, `-> bool`, `list[int]`, `dict[str, float]`, `Optional[int]` (i.e. `int | None`). Crucially, **Python does not enforce them at runtime** — they're documentation that tools read. Their value: your editor autocompletes and catches mismatches, a checker like `mypy` finds bugs before you run, and the next reader (future you) sees the contract without spelunking. They pair naturally with dataclasses (which need the hints anyway). You don't have to type *everything* — but typing function signatures and dataclass fields is increasingly the baseline expectation in senior interviews and real codebases.

---

## Try it

1. Turn this into a dataclass and say which methods you got for free: a `class Book` holding `title`, `author`, and `year` (default `2024`), that should print readably and compare by value.
2. Your `Temperature` class prints as `<Temperature object at ...>` and `sorted([t1, t2, t3])` raises `TypeError`. Which two dunder methods fix each problem, and why does one of them also enable `min()`/`max()`?
3. Rewrite with `with`: open a file, read it, close it — guaranteeing the file closes even if reading raises. What exactly does `__exit__` guarantee that a manual `close()` at the end does not?
4. Add type hints to `def process(rows, config)`: `rows` is a list of dicts, `config` is a `Config`, and it returns a count. What do the hints buy you, and what do they pointedly *not* do at runtime?
5. You have a `frozen=True` dataclass `Point`. Why does that one keyword let you use it as a dictionary key or set member, when a plain class or a mutable dataclass can't?

*Write your answers in [ch11-python-objects-tryit.md](../code/ch11-python-objects-tryit.md).*

---

## The bumper sticker

> *Modeling in Python is about deleting ceremony once you feel it: `@dataclass` for plain objects so you never hand-write `__init__`/`__repr__`/`__eq__`, dunder methods so your class plugs into `+`, `==`, `[]`, and `sorted()` like a built-in, `with` so a resource can't leak past an exception, and type hints so the contract lives in the signature. Feel the boilerplate first; let the idiom earn its place.*

Next, the closing chapter: the pop-quiz ritual — how to answer any fundamentals question cleanly under pressure, with a fast-review grid for the whole track.

---

<div align="right">

[Chapter 12 →](ch12-ritual.md)

</div>
