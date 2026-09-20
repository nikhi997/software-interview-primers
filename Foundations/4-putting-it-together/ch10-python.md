# Chapter 10: The Python you're assumed to know — data and iteration

*[← Chapter 9](ch9-concurrency.md) · [Contents](../foundations-README.md)*

- [ ] **Mark as read**

Every other chapter in this track goes one level *below* the code. This pair of chapters stays *at* the code — but it's the same bargain: feel the mechanism, not just the syntax. You already know `if`, `for`, `while`, and functions; these chapters aren't about those. They're about the Python idioms working engineers reach for constantly, that interviewers expect to see, and that quietly separate "writes Python" from "writes *Pythonic* code."

This first chapter is the half you'll lean on hardest in a coding or DSA round: turning data from one shape into another, and iterating without drowning in memory. The next chapter covers the other half — modeling things as objects. We won't list features; we'll do what the rest of the book does: start with the clunky version that works, feel exactly where it hurts, then reach for the idiom that removes the pain.

Core principle, one more time: **feel the boilerplate before reaching for the idiom.**

---

## Comprehensions: the loop that's really a transform

You want a list of squares of the even numbers. The honest beginner version:

```python
squares = []
for n in numbers:
    if n % 2 == 0:
        squares.append(n * n)
```

Four lines, a mutable accumulator, and an `append` you have to remember. The pain is small but constant — half your loops are "take a collection, filter some, transform the rest," and writing the scaffold every time is noise that buries the intent.

```python
squares = [n * n for n in numbers if n % 2 == 0]
```

One line that reads as *what you want*: "n squared, for each n, where n is even." The accumulator and `append` vanish.

Watch the position of the `if`. A trailing `if` *filters* — it drops items. But when you want to *transform* each item instead of dropping any, the condition moves to the front as a ternary:

```python
clamped = [x if x > 0 else 0 for x in values]   # keep positives, floor the rest at 0
```

Filter `if` goes at the *end* and may shrink the list; the `x if cond else y` ternary goes at the *front* and keeps every item. Mixing the two up is the most common comprehension bug.

> 💡 **Concept notes — comprehensions and when *not* to use them**
> A **list comprehension** is `[expr for item in iterable if condition]` — map and filter in one expression. They're faster than the equivalent loop (the work happens in C) and, more importantly, they signal "I'm building a collection by transforming another." The discipline: keep them to *one* logical step. The moment you'd need a nested `if/else` with side effects, or two levels of nesting you have to re-read, go back to a plain loop — a comprehension that needs decoding has lost its only advantage. Clarity first.

---

## Dict and set comprehensions: build a lookup, not a loop

Two-Sum and half the hash-map problems in the DSA track start the same way: you need a map from each value to where it lives. The loop version is the count-with-a-dict dance again:

```python
index = {}
for i, v in enumerate(nums):
    index[v] = i
```

The **dict comprehension** says it in one line — and reads as "value maps to index, for each value":

```python
index = {v: i for i, v in enumerate(nums)}
```

The same move inverts a mapping (swap keys and values) or builds a lookup from two parallel lists with `zip`:

```python
inverse = {v: k for k, v in mapping.items()}          # flip a dict
by_name = {name: score for name, score in zip(names, scores)}
```

And when you only care whether something has been *seen* — dedup, membership — the **set comprehension** drops duplicates for free:

```python
unique_lengths = {len(w) for w in words}    # a set: each distinct length once
```

> 💡 **Concept notes — dict/set comprehensions**
> Same syntax as a list comprehension, different brackets: `{k: v for ...}` builds a **dict**, `{x for ...}` builds a **set**. The dict form is the idiomatic way to build the value→index maps, frequency lookups, and adjacency structures that hash-map problems live on; `enumerate` hands you the index and `zip` pairs two sequences. The set form gives you O(1) membership and automatic dedup in one expression. Both beat the "create empty, loop, assign" scaffold and read as the thing you're building.

---

## Comprehensions for DSA: grids, flattening, and the aliasing trap

You need a `rows × cols` grid of zeros — a DP table, a visited matrix, a game board. The tempting one-liner is a trap:

```python
grid = [[0] * cols] * rows    # LOOKS right, is badly wrong
grid[0][0] = 1
# grid is now [[1, 0, ...], [1, 0, ...], [1, 0, ...]] — every row changed!
```

`[inner] * rows` doesn't copy the inner list — it stores the *same* list object `rows` times. Mutate one row and you've mutated all of them. This bug eats hours in contests. The comprehension builds a fresh inner list each pass, so the rows are independent:

```python
grid = [[0] * cols for _ in range(rows)]    # each row is its own list
```

The nested form also *flattens*: read the `for` clauses left to right, exactly as if they were nested loops:

```python
flat = [x for row in grid for x in row]     # outer row first, then each x in it
```

> 💡 **Concept notes — nested comprehensions and `[[0]*n]*m`**
> `[[0] * cols for _ in range(rows)]` is the correct 2-D initializer: the comprehension re-evaluates `[0] * cols` every iteration, giving each row a distinct list. The seductive `[[0] * cols] * rows` aliases one list into every slot — the single most common "why did my whole grid change?" bug in DSA. For flattening, a nested comprehension's clauses run in the same order you'd write nested `for` loops: `[x for row in grid for x in row]` means "for each row, for each x in that row." Keep flattening to two levels; deeper than that, a plain loop reads better.

---

## Generators: don't build what you can stream

Now the dataset is ten million rows and you only need the total. The list-comprehension reflex backfires:

```python
total = sum([row.amount for row in read_rows()])   # builds a 10M-item list first
```

That `[...]` materializes all ten million amounts in memory *before* `sum` adds them up. You feel it as a memory spike — or an outright crash. But you never needed the list; you needed the numbers *one at a time*, briefly.

Drop the brackets and it becomes a **generator expression** — same syntax, lazy evaluation:

```python
total = sum(row.amount for row in read_rows())      # one row in memory at a time
```

For your own functions, `yield` does the same thing — it produces values on demand instead of returning a finished list:

```python
def read_rows():
    with open("huge.csv") as f:
        for line in f:                  # the file object is itself lazy
            yield parse(line)           # hand back one row, pause, resume on next request
```

> 💡 **Concept notes — `yield`, laziness, and `StopIteration`**
> A function containing `yield` is a **generator**: calling it doesn't run the body, it returns a *generator object*. Each time something asks for the next value (a `for` loop, `sum`, `next()`), the body runs until the next `yield`, hands that value back, and *freezes* — local variables and all — until the next request. When the function ends, Python raises `StopIteration` internally, which is how a `for` loop knows to stop. The payoff is **constant memory regardless of data size** and the ability to represent *infinite* sequences. The tradeoff: a generator is single-use (once consumed, it's exhausted) and you can't index it or take its `len`. Reach for generators the moment a dataset is large, streamed, or you only need a one-pass scan — exactly the "feel the memory pain" instinct from the OS chapter.

---

## Unpacking and multiple return: stop indexing tuples

A function needs to return two things. The clumsy way leaks indices everywhere:

```python
def min_max(nums):
    return (min(nums), max(nums))

result = min_max(data)
lowest = result[0]      # what was [0] again?
highest = result[1]
```

`result[0]` and `result[1]` are exactly the primitive-obsession smell from the LLD track — positional access with the meaning living in your head. Python lets you unpack directly:

```python
lowest, highest = min_max(data)
```

> 💡 **Concept notes — tuple unpacking and the star**
> Python assigns tuples/lists positionally: `a, b = b, a` swaps without a temp; `first, *rest = [1, 2, 3, 4]` gives `first=1, rest=[2, 3, 4]` (the starred name soaks up the remainder). It works in `for` loops too — `for key, value in d.items():` unpacks each pair. This is why functions returning a tuple feel so natural in Python: the caller names the pieces at the call site. It reads better than a positional index *and* better than inventing a class for a throwaway pair.

---

## The collections you should reach for

You're counting word frequencies. The plain-dict version is all bookkeeping:

```python
counts = {}
for word in words:
    if word not in counts:
        counts[word] = 0
    counts[word] += 1
```

That "is the key there yet?" dance shows up constantly, and it's pure noise. The standard library already solved it:

```python
from collections import Counter
counts = Counter(words)          # done — {'the': 4, 'cat': 2, ...}
counts.most_common(3)            # the three most frequent, sorted
```

> 💡 **Concept notes — the `collections` workhorses**
> - **`Counter`** — a dict that counts. `Counter(iterable)` tallies everything; `.most_common(n)` ranks them. Kills the count-with-a-dict pattern.
> - **`defaultdict(list)`** — a dict that auto-creates a default for missing keys, so `d[key].append(x)` works without first checking the key exists. Perfect for grouping (build an adjacency list, bucket items by category).
> - **`deque`** — a double-ended queue with O(1) `append`/`popleft` at *both* ends. A plain list's `pop(0)` is O(n) because it shifts everything; `deque` is the right structure for a BFS queue or a sliding window (the DSA track leans on it).
> These three turn a dozen lines of manual bookkeeping into one expressive line, and using them signals you know the standard library instead of reinventing it under interview pressure.

---

## Try it

1. You have a loop that starts with an empty `result` list, walks `users`, and for each `u` that is `u.active` appends `u.email.lower()`. Rewrite it as a single comprehension — then say when you'd *refuse* to collapse a loop this way.
2. You have a 50 GB log file and need the count of lines containing `"ERROR"`. Write it so memory stays flat regardless of file size. Which idiom makes that possible, and what would the naive version do?
3. Build a dict that maps each value in `nums` to its index in one line. Then clamp a list of numbers so negatives become `0` — and explain why one `if` goes at the *end* of the comprehension and the other goes in the *middle*.
4. Write a `rows × cols` grid of zeros you can safely mutate one cell of. Show the version that *looks* right but corrupts every row, and explain in one sentence why it breaks.
5. A function returns `(min(nums), max(nums))`. Show how the caller names both results without indexing, and give the one-line swap `a, b = b, a` — what makes both work?
6. You're grouping a list of `(department, employee)` pairs into `{department: [employees]}`. Show the `defaultdict` version and explain what bookkeeping line it removes versus a plain dict.

*Write your answers in [ch10-python-tryit.md](../code/ch10-python-tryit.md).*

---

## The bumper sticker

> *The idioms that carry a coding round are about moving data between shapes without ceremony: comprehensions for transforms (filter-`if` at the end, ternary in the middle), dict/set comprehensions for the lookups hash-map problems live on, `[[0]*cols for _ in range(rows)]` for a grid that won't alias itself, generators when the data is too big to hold, and the `collections` workhorses instead of hand-rolled bookkeeping. Feel the clunky version first; let the idiom earn its place.*

Next, the other half of the Python you're assumed to know: modeling things as objects — dataclasses, dunder methods, context managers, and type hints — the idioms that make your classes behave like built-ins.

---

<div align="right">

[Chapter 11 →](ch11-python-objects.md)

</div>
