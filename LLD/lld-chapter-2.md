# Chapter 2: One folder for the loose papers

*[← Chapter 1](lld-chapter-1.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

End of last chapter, we had a working URL shortener with a problem: globals everywhere, `save()` calls scattered across functions, and no single place that said "this is the shortener."

We named the feeling: state and behavior wanted to live together, but we'd spread them apart. A class is the folder for those loose papers.

Let's make the folder.

---

## The translation

Here's the code from end of Chapter 1, rewritten as a class. Read it first. We'll talk about what changed and what didn't.

```python
import random
import string
import json


class URLShortener:
    def __init__(self, storage_file="urls.json"):
        self.storage_file = storage_file
        self.urls = {}
        self.clicks = {}
        self._load()

    def shorten(self, long_url, custom_code=None):
        if custom_code:
            if custom_code in self.urls:
                raise ValueError(f"Code '{custom_code}' is already taken")
            code = custom_code
        else:
            code = self._generate_code()
        self.urls[code] = long_url
        self._save()
        return code

    def expand(self, code):
        self.clicks[code] = self.clicks.get(code, 0) + 1
        self._save()
        return self.urls[code]

    def click_count(self, code):
        return self.clicks.get(code, 0)

    def _generate_code(self):
        return ''.join(random.choices(string.ascii_letters, k=6))

    def _save(self):
        with open(self.storage_file, "w") as f:
            json.dump({"urls": self.urls, "clicks": self.clicks}, f)

    def _load(self):
        try:
            with open(self.storage_file) as f:
                data = json.load(f)
                self.urls = data["urls"]
                self.clicks = data["clicks"]
        except FileNotFoundError:
            pass
```

> 💡 **Python notes — the class vocabulary, just from this code**
> `class URLShortener:` declares a blueprint. No actual shortener exists yet — this is just the shape definition. Class names use `CamelCase` by Python convention.
> `def __init__(self, storage_file="urls.json"):` is the *constructor*. It runs once, automatically, the moment you write `URLShortener()`. Its job is to put the new instance into a usable state. The `storage_file="urls.json"` part means the parameter is optional and defaults to `"urls.json"` if you don't pass one.
> `self` is the convention for "this specific instance." Inside methods, `self.urls` means *this shortener's urls*, distinguishing it from any other shortener that exists. `self` gets passed in automatically when you call `s.shorten(...)` — Python silently translates that into `URLShortener.shorten(s, ...)`. You write `self` as the first parameter in every method (except a couple of advanced cases we'll meet much later).
> `self.urls = {}` creates an *attribute* on the instance — a piece of data that belongs to this specific shortener. Different from a local variable, which only lives during one function call.
> The `_` prefix on `_save`, `_load`, `_generate_code` is a Python *convention* (not an enforced rule) meaning "this is internal — don't call it from outside the class." Python won't actually stop you. It's a polite sign on the door saying *staff only.*

Let's use it:

```python
>>> s = URLShortener()
>>> code = s.shorten("https://en.wikipedia.org/wiki/Spaghetti", custom_code="pasta")
>>> s.expand("pasta")
'https://en.wikipedia.org/wiki/Spaghetti'
>>> s.expand("pasta")
'https://en.wikipedia.org/wiki/Spaghetti'
>>> s.click_count("pasta")
2
```

Same behavior. Different shape.

---

## What changed, line by line

If you put the old code and new code side by side, here's everything that's different. Nothing more, nothing less.

**`urls` and `clicks` got a prefix.** `urls` is now `self.urls`. `clicks` is now `self.clicks`. The data didn't move to a different place in any meaningful way — it just got *labeled* as belonging to this specific shortener.

**Functions got a prefix too.** `shorten(...)` is now `self.shorten(...)`. Same logic. Same body. Just a name change saying "this function belongs to a shortener."

**A new function appeared: `__init__`.** This runs once, when you make a new shortener. It sets up empty dictionaries and loads from disk. Before, we ran `load()` manually. Now it happens automatically the moment you write `URLShortener()`.

**Some functions got a `_` prefix.** `_generate_code`, `_save`, `_load`. The underscore is a Python convention meaning "this is internal — don't call it from outside the class." Nothing enforces it; it's a polite sign on the door saying *staff only.* The methods without underscore (`shorten`, `expand`, `click_count`) are the public ones, the things a user of the class is meant to call.

That's it. That's everything that changed.

---

## What did *not* change

The thing I want you to notice — really notice — is what stayed identical:

- The algorithm for generating a code (`random.choices(string.ascii_letters, k=6)`)
- The if/else logic for custom codes
- The way clicks are counted (`get(code, 0) + 1`)
- The JSON shape on disk
- The order operations happen in

The logic of the URL shortener didn't change at all. We just *moved the furniture.* The bed is still a bed, the desk is still a desk — we just stopped having them in three different rooms.

This is one of the most common misunderstandings about OOP: people think wrapping things in classes makes the code "smarter" or "more correct." It doesn't. The class doesn't compute anything new. The class is purely about *organization* — where things live, who can see what, and how they hang together.

If you forget everything else from this chapter, remember this:

> Classes don't add logic. They add a home.

---

## What we got from the move

Even though the logic is identical, the new version is genuinely better in three specific ways. Let's name them.

**1. No more forgotten `save()` calls.**

In Chapter 1, every function that touched state had to remember `save()`. Forget it once, you get a bug. Now `_save` is sitting right inside the class, next to the methods that need it, and `__init__` automatically wires `_load` so we never forget. The save calls are *still manual* — `self._save()` is written in `shorten` and `expand` — but they're sitting in a folder with their data, not loose on the floor. Easier to remember, easier to audit.

**2. The shortener is now a *thing* you can hold.**

Before, "the URL shortener" was an idea spread across six functions. To use it, you imported the module and called functions. To talk about it, you said "the file."

Now it's a thing:

```python
s = URLShortener()
```

`s` *is* the shortener. You can pass it to a function. You can put it in a list. You can have two of them. Try this:

```python
>>> personal = URLShortener("personal.json")
>>> work = URLShortener("work.json")
>>> personal.shorten("https://en.wikipedia.org/wiki/Spaghetti", custom_code="pasta")
'pasta'
>>> work.shorten("https://docs.aws.amazon.com/s3", custom_code="s3")
's3'
>>> personal.expand("s3")
Traceback (most recent call last):
  ...
KeyError: 's3'
```

Two completely independent shorteners. Different files. Different data. The personal one doesn't know about the work one. The global version couldn't do this without major surgery — there was only ever one `urls` dict.

This sounds small. It isn't. Almost every real-world use of classes comes down to *"I want to have more than one of these, and they shouldn't tangle."*

**3. The boundary is now visible.**

If someone new opens the file and asks "what does the URL shortener actually do?", the answer is right there: read the public methods of `URLShortener`. There are three — `shorten`, `expand`, `click_count`. That's the contract. Everything else (`_save`, `_load`, `_generate_code`) is plumbing.

In the Chapter 1 version, there was no boundary. Every function was equally public. Every dict was equally accessible. Someone could modify `urls[code]` from anywhere in the file and no one would know.

A class is not a security mechanism. The underscore doesn't stop anyone. But it does *say* something. It says: here is what this thing offers. Here is what it expects to do internally. If you reach inside, you're on your own.

---

## Demystifying the vocabulary (the recap)

Now that we have a class in front of us, let me name the four things that show up in every class. We met them inline above; here they are in one place for reference:

**Class.** A blueprint. `URLShortener` is the blueprint. Writing the `class URLShortener:` line doesn't *do* anything yet — it just defines the shape.

**Instance.** An actual one. `s = URLShortener()` creates an instance. That's the moment the blueprint becomes a real thing in memory. `personal` and `work` from earlier are two different instances of the same class. Same blueprint, different houses.

**`self`.** Inside a method, `self` is "this specific instance, the one we're working with right now." When you write `personal.shorten(...)`, Python silently passes `personal` in as `self`. So inside `shorten`, `self.urls` means *personal's urls*, not work's. The `self` parameter is how methods know which instance they belong to.

**`__init__`.** The setup ritual. Runs once, the moment you do `URLShortener()`. Its job is to put the instance into a usable starting state — empty dicts, file path remembered, data loaded from disk. After `__init__` runs, the instance is ready to be used.

That's the whole vocabulary. Four words. You'll see them in every class for the rest of your career.

A note on tone: a lot of OOP material treats these concepts like a philosophy course — "encapsulation," "abstraction," "polymorphism," whole chapters of definitions before you see a line of code. We're not going to do that. Those words *are* useful, eventually. But they describe things you already do once you have a few classes in your hands. We'll meet each one when it actually shows up in the code, not before.

---

## The next pain point

Run the new code. Use it. Make a few shorteners. Click a few links.

Notice something? It works. It's tidier. But it's still doing exactly the same thing as Chapter 1. We didn't unlock any new capability — we just organized.

So let me plant a seed for the next requirement.

Look at `_save` and `_load`. They write to a JSON file. That's fine for a toy project. But imagine the product manager comes back:

> "We're moving to production. We need to use Redis instead of a file. And eventually maybe a real database. Can you change it?"

You look at the code. `_save` and `_load` have *Redis-incompatible* assumptions baked in — they use `open()`, they use `json.dump`, they assume a filename. You can't just swap them out. You'd have to rewrite both methods, and any method that calls them, every time you want a different backend.

You could solve this the obvious way: an `if` statement.

```python
def _save(self):
    if self.backend == "file":
        # file logic
    elif self.backend == "redis":
        # redis logic
    elif self.backend == "postgres":
        # postgres logic
```

And it would work. For a while. Until you need a fourth backend. Or until you want to write a unit test without hitting any real storage. Then this `if` becomes the new pain.

There is a much cleaner way. It has a name — *Strategy pattern* — but I'm not going to tell you about it yet. In Chapter 3, we're going to feel the pain of that `if` ladder, and then *we will reach for the right shape ourselves.* When you reach for it before being told its name, you've actually learned it. When you're told the name first, you've just memorized vocabulary.

See you in chapter 3.

---

## Before you turn the page

Two small exercises. Do them in your file:

**Exercise 1.** Add a method called `delete(code)` that removes a code from the shortener. Think about: should it delete the click count too? What happens if the code doesn't exist?

> 💡 **Python hint — `del` and `dict.pop`**
> Two ways to remove a key from a dict: `del self.urls[code]` (crashes if missing) or `self.urls.pop(code, None)` (returns the value, or `None` if missing — no crash). Pick the one that matches your intent.

**Exercise 2.** Without changing the class, write a tiny function *outside* the class:

```python
def transfer(source_shortener, dest_shortener, code):
    ...
```

It should move a code from one shortener to another. Notice how naturally you can pass two shorteners around now. This was awkward-to-impossible with the Chapter 1 version.

Both exercises are small. The point isn't the code — it's getting your fingers used to thinking *"the shortener is a thing I can hold and operate on."* That mental shift is half of what classes are for.

---

<div align="right">

[Chapter 3 →](lld-chapter-3.md)

</div>
