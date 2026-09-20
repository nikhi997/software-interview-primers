# Chapter 1: The shortest URL shortener that could possibly work

*[Contents](lld-README.md)*

- [ ] **Mark as read**

Someone hands you this task at work: build a URL shortener. Like tinyurl or bit.ly. People paste a long URL, you give them a short code, and when they hit the short code, they go to the long URL.

You nod. Easy enough.

What does it actually have to do? Two operations:

1. Take a long URL, return a short code.
2. Take a short code, return the long URL.

That's it. Two things. Let's not pretend it's more.

Here's the first version. The shortest thing that could possibly work:

```python
import random
import string

urls = {}

def generate_code():
    return ''.join(random.choices(string.ascii_letters, k=6))

def shorten(long_url):
    code = generate_code()
    urls[code] = long_url
    return code

def expand(code):
    return urls[code]
```

> 💡 **Python notes — what's new in this code block**
> `string.ascii_letters` is a built-in string equal to `'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'` — all 52 letters pre-bundled, so you don't have to type them.
> `random.choices(population, k=n)` picks `n` items from `population` *with replacement* (so the same letter can be picked twice). It returns a *list*, which is why we wrap it in `''.join(...)` to glue the list of single characters into one string. `random.sample` is the without-replacement cousin.

Let's just try it:

```python
>>> code = shorten("https://en.wikipedia.org/wiki/Spaghetti")
>>> code
'xKqMnT'
>>> expand('xKqMnT')
'https://en.wikipedia.org/wiki/Spaghetti'
```

And we're done. We built a URL shortener. Thirteen lines of code. No classes. No design. No SOLID. No "considering scalability." Just functions that do the thing.

Here's the part most books get wrong. They look at this code and say, "but it's not real! Where's the database! Where's the API!" And then they introduce eight abstractions to fix problems we don't have.

We're not going to do that. We're going to keep this exact code and ask one question: what would actually make us change it?

---

## Pause. What is "design," really?

Let me say something blunt before we go further.

Design isn't about planning ahead. Design is about *responding to change.*

If a URL shortener never needs to do anything different than it does right now, the code above is the design. It's done. Calling it "bad" because it doesn't have classes is like calling a fork "bad" because it doesn't have wheels.

Code becomes badly designed when a new requirement lands and the code fights you. Not before.

So the only real design question, always, is:

> *What's the next thing someone might ask for, and will my code bend or break?*

Let's brainstorm. Pretend you're sitting with the product manager who gave you this task. What might they ask next?

- "Can users pick their own custom short codes?" (Like `bit.ly/my-blog`)
- "Can we track how many times each link is clicked?"
- "What happens when our app restarts? Do all the URLs disappear?"
- "Can the same long URL share a code, so we don't waste codes?"
- "Can codes expire after a year?"

Don't answer these yet. Just notice: each one of them would change our code. Some a little. Some a lot. The only real test of design is whether, when these requirements land, the code bends with you or fights you.

Let's land a few and see what happens.

---

## Requirement 1: Custom codes

"I want my short code to be `pasta`, not some random string."

Easy. Optional argument:

```python
def shorten(long_url, custom_code=None):
    code = custom_code if custom_code else generate_code()
    urls[code] = long_url
    return code
```

Try it:

```python
>>> shorten("https://en.wikipedia.org/wiki/Spaghetti", custom_code="pasta")
'pasta'
>>> expand("pasta")
'https://en.wikipedia.org/wiki/Spaghetti'
```

Works. We added one parameter and one ternary. The code bent.

But wait — what if someone passes `custom_code="pasta"` and `pasta` is already taken by another URL? Right now we silently overwrite the old one. That's a bug. Fix it:

```python
def shorten(long_url, custom_code=None):
    if custom_code:
        if custom_code in urls:
            raise ValueError(f"Code '{custom_code}' is already taken")
        code = custom_code
    else:
        code = generate_code()
    urls[code] = long_url
    return code
```

> 💡 **Python note — f-strings**
> `f"Code '{custom_code}' is already taken"` is an *f-string* (formatted string). The `f` before the quote tells Python to evaluate anything in `{...}` and inject its actual value. So if `custom_code = "pasta"`, the string becomes `"Code 'pasta' is already taken"`. Without the `f`, Python would print `{custom_code}` literally.
> `raise ValueError(...)` stops the function and signals "something invalid was passed in." `ValueError` is one of Python's built-in error types — you'll see others like `TypeError`, `KeyError`. The caller of `shorten` can catch it with `try/except` (we'll see this pattern later).

Five new lines. Still readable. The function reads top to bottom like a sentence: "if they gave a custom code, check it's free, use it; otherwise make a random one; either way, save it."

A small voice in your head might whisper, *"this is getting a bit if-y, should this be a class?"* Ignore that voice. We have fifteen lines of working code. Don't reach for a hammer because someone left one on the table.

---

## Requirement 2: Click tracking

"Tell me how many times each short link has been clicked."

Clicks happen during `expand`. So `expand` needs to remember something. Add it:

```python
clicks = {}

def expand(code):
    clicks[code] = clicks.get(code, 0) + 1
    return urls[code]

def click_count(code):
    return clicks.get(code, 0)
```

> 💡 **Python note — `dict.get(key, default)`**
> `clicks.get(code, 0)` returns the value for `code` if it exists in the dict, or `0` if it doesn't. Without `.get`, the line `clicks[code]` would crash with a `KeyError` the very first time we click a new link.
> The pattern `clicks[code] = clicks.get(code, 0) + 1` is the standard Python way to do "increment a counter, starting from zero if it's new." There's also `collections.Counter` for this exact use case, but `.get` is fine when you're tracking one thing.

Done. Try it:

```python
>>> shorten("https://en.wikipedia.org/wiki/Spaghetti", custom_code="pasta")
>>> expand("pasta")
>>> expand("pasta")
>>> expand("pasta")
>>> click_count("pasta")
3
```

Now stop and look at what's sitting on the screen. We have:

- A `urls` dictionary, global
- A `clicks` dictionary, global
- A `shorten` function
- An `expand` function
- A `generate_code` function
- A `click_count` function

Two pieces of data. Four functions that touch them. All floating around at the top of the file.

Take a screenshot of this in your head. We're about to feel something.

---

## Requirement 3: Survive a restart

"When our app restarts, all the URLs disappear because they're in memory. Save them somewhere."

Fine. Save to a file. Whenever something changes, write the dict to disk. When the program starts, read it back.

```python
import json

def save():
    with open("urls.json", "w") as f:
        json.dump({"urls": urls, "clicks": clicks}, f)

def load():
    global urls, clicks
    try:
        with open("urls.json") as f:
            data = json.load(f)
            urls = data["urls"]
            clicks = data["clicks"]
    except FileNotFoundError:
        pass
```

> 💡 **Python notes — `with open`, `json`, `try/except`, `global`**
> `with open("urls.json", "w") as f:` opens a file and *automatically closes it* when the indented block ends — even if something crashes inside. `f` is the file handle. The `"w"` means write mode (overwrites the file each time). `"r"` is read mode (the default, used if you omit the second argument as we do in `load`). Always prefer `with open(...)` over manual `open()` + `f.close()`.
> `json.dump(obj, f)` writes a Python dict (or list, string, number, bool, None) to file `f` as JSON text. `json.load(f)` does the reverse — reads JSON text back into a Python value. They only handle basic types — custom classes need extra work to serialize.
> `try: ... except FileNotFoundError: pass` says: "try this; if it fails specifically because the file doesn't exist, do nothing and continue." This is normal on first run, when `urls.json` hasn't been created yet. `pass` is Python's way of saying "do nothing here, but I need a statement to satisfy the syntax."
> `global urls, clicks` says: "the `urls` and `clicks` I'm about to assign inside this function refer to the module-level ones, not new local variables." Without `global`, Python would create new local variables when you assign to them, and the load wouldn't actually update the dicts the rest of the code is using. This is a quirk that often confuses people coming from other languages — *reading* a global doesn't need the keyword; *assigning* to one does.

And now we have to call `save()` every time something changes:

```python
def shorten(long_url, custom_code=None):
    if custom_code:
        if custom_code in urls:
            raise ValueError(f"Code '{custom_code}' is already taken")
        code = custom_code
    else:
        code = generate_code()
    urls[code] = long_url
    save()        # <-- new
    return code

def expand(code):
    clicks[code] = clicks.get(code, 0) + 1
    save()        # <-- new
    return urls[code]
```

It works. But notice what just happened.

Every function that *changes* state has to remember to call `save()`. If I add a new function tomorrow that touches `urls` and forget the `save()` line, I introduce a silent bug. Data on disk and data in memory drift apart, and nothing tells me.

Also: `save`, `load`, `urls`, `clicks`, `shorten`, `expand`, `generate_code`, `click_count` are now all loose in the same file, no organization. If a new teammate opens this file and asks, "what *is* the URL shortener?", the only honest answer is "scroll around and figure it out."

This is the feeling. The code is starting to fight back. Not loudly — quietly. You can keep going like this for a while. But something is misaligned.

---

## Naming the feeling

Let me say it carefully, because this is the only abstract idea I'll introduce in this chapter.

We have two pieces of data — `urls` and `clicks` — that always change together. And a bunch of functions that all have to remember to keep that data in sync with disk. The data and the operations on the data want to be near each other. Physically, in the file. Mentally, in your head. They are not.

When state and behavior want to live together, but you've spread them apart, *that's* when a class earns its keep.

Not because OOP is good. Not because some principle said so. But because right now, on this screen, in this specific code, the cost of keeping them separate is showing up. Forgotten `save()` calls. Functions floating without context. Reading the code takes more effort than it should.

> A class is the file folder you reach for when the loose papers on your desk start blowing around.

That's the whole motivation. Not in chapter 9. Not after SOLID. Not after a tour of the four pillars of OOP. Right here, in chapter 1, because the code itself asked for one.

---

## What we're not going to do (yet)

We are *not* going to make the class in this chapter. That's chapter 2.

What I want you to do is read the current code one more time, slowly, and just *feel* it. Notice:

- The globals (`urls`, `clicks`) that anyone could modify from anywhere
- The repeated `save()` calls scattered across functions
- The lack of any single place that says "this is the URL shortener"

Don't be mad at the code. It worked. It got us this far. We learned what we needed from it. But the next requirement — any of them — will make this version hurt more than it should.

Chapter 2: we wrap all this into a single class, and watch what changes and what doesn't. (Spoiler: less changes than you'd think. The logic is the logic. What we're really doing is moving the furniture so we can find it again.)

---

## A note before you turn the page

You might have noticed I didn't draw any UML. I didn't talk about Single Responsibility. I didn't define "encapsulation." I didn't tell you what a class even *is* (we'll get there, but only when we have one in front of us).

This is deliberate.

Every one of those concepts is a name for a feeling. If you don't have the feeling yet, the name is just trivia. We're going to do feelings first, names later. By the time we get to SOLID — many chapters from now — you'll have already done four of the five things SOLID names, and the chapter will read like, *"oh, that's what that was called."*

That's the trade. Read these chapters in order. In exchange, you don't have to memorize anything, ever. The patterns will stick because you'll have earned them.

See you in chapter 2.

---

<div align="right">

[Chapter 2 →](lld-chapter-2.md)

</div>
