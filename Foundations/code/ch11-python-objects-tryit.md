# Chapter 11: The Python you're assumed to know — objects and idioms — Try it

*Answers for the Try it questions in [ch11-python-objects.md](../4-putting-it-together/ch11-python-objects.md).*

1. Turn this into a dataclass and say which methods you got for free: a `class Book` holding `title`, `author`, and `year` (default `2024`), that should print readably and compare by value.


2. Your `Temperature` class prints as `<Temperature object at ...>` and `sorted([t1, t2, t3])` raises `TypeError`. Which two dunder methods fix each problem, and why does one of them also enable `min()`/`max()`?


3. Rewrite with `with`: open a file, read it, close it — guaranteeing the file closes even if reading raises. What exactly does `__exit__` guarantee that a manual `close()` at the end does not?


4. Add type hints to `def process(rows, config)`: `rows` is a list of dicts, `config` is a `Config`, and it returns a count. What do the hints buy you, and what do they pointedly *not* do at runtime?


5. You have a `frozen=True` dataclass `Point`. Why does that one keyword let you use it as a dictionary key or set member, when a plain class or a mutable dataclass can't?
