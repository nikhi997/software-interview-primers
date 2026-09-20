# Chapter 2: Trading space for time

*[← Chapter 1](dsa-chapter-1.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

Last chapter we took two-sum from `O(n²)` to `O(n)` with a `set` and promised to explain it. This chapter is that explanation, and it's the most important single tool in interviewing: the **hash map** (and its cousin the **hash set**). More problems are solved by "put it in a hash map" than by any other technique. Learn this one cold.

The pain it removes is always the same: **repeated lookups.** Whenever your brute force re-scans data to ask "have I seen this?" or "how many of these?" or "where is that?", a hash map answers in `O(1)` instead of `O(n)`.

---

## The brute force and its waste

Recall two-sum's brute force: for each number, scan the rest of the list for its complement.

```python
def has_sum_pair_brute(nums, target):
    for first in range(len(nums)):
        for second in range(first + 1, len(nums)):   # re-scan the rest, every time
            if nums[first] + nums[second] == target:
                return True
    return False
```

The waste is the inner loop. For every element we walk the whole remaining list asking "is `target - element` in here?" That's a *search*, and we redo it for every element — `n` searches of up to `n` items = `O(n²)`.

What if we could ask "is this value present?" *instantly*, without scanning? That's exactly what a hash map gives us.

---

## What a hash map actually is

A **hash map** (Python's `dict`) stores key→value pairs and answers three questions in `O(1)` *average* time:
- **Insert:** `table[key] = value`
- **Look up:** `table[key]` or `key in table`
- **Delete:** `del table[key]`

A **hash set** (Python's `set`) is the same thing without values — it just answers "is this key present?" in `O(1)`. Use a set when you only care about membership; a map when you need to associate data with each key.

> 💡 **Concept notes — how `O(1)` lookup is possible**
> A hash map uses a **hash function** to convert a key into an array index directly. Instead of *searching* for the key, it *computes* where the key would live and jumps straight there. That's why it's `O(1)` — no scanning. The cost is memory (the underlying array) and that keys must be **hashable** (immutable: numbers, strings, tuples — not lists). The `O(1)` is "average" because rare hash collisions can degrade it, but for interviews you treat hash-map operations as constant time.

---

## Removing the waste

Replace the inner-loop *search* with a hash-set *lookup*:

```python
def has_sum_pair_set(nums, target):
    seen = set()
    for num in nums:
        complement = target - num
        if complement in seen:        # O(1) — no scan
            return True
        seen.add(num)
    return False
```

One pass. As we walk the list, `seen` holds every number we've already passed. For each new number, we work out its `complement` and ask the set "did I already see the value that pairs with you?" in constant time. `O(n)` time, `O(n)` space. The inner loop is *gone* — we pay memory for the set and get back the entire quadratic cost.

> 💡 **Concept notes — the universal hash-map move**
> The shape is always: *as you iterate once, record what you've seen in a hash structure, and query it in `O(1)` to avoid re-scanning.* "Have I seen X?" → set. "How many X have I seen?" → map of counts. "Where did I see X?" → map of value→index. If your brute force has an inner loop that searches, counts, or locates, a hash map almost certainly deletes it.

### The "return the indices" variant

Interviewers usually want the *positions*, not just yes/no. Use a **map** of value→index instead of a set. Written with a plain index loop:

```python
def two_sum(nums, target):
    seen = {}                      # value -> index
    for index in range(len(nums)):
        num = nums[index]
        complement = target - num
        if complement in seen:
            return [seen[complement], index]
        seen[num] = index
    return []
```

Same pattern as before, but the map remembers *where* each value was, so we can return both indices. This is the canonical "Two Sum" problem — and the canonical demonstration that a hash map turns `O(n²)` into `O(n)`.

Notice the first two lines of the loop: we ask `range` for each `index`, then immediately look up `nums[index]` to get the value. That pairing — "walk the positions, then fetch the value at each one" — is so common that Python has a built-in for it: **`enumerate`**. It hands you the index *and* the value together on every pass, so you never write `nums[index]` by hand:

```python
def two_sum(nums, target):
    seen = {}                      # value -> index
    for index, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], index]
        seen[num] = index
    return []
```

Why the second version is better: one fewer line, and the intent reads straight off — `index, num` says "I want both" up front, instead of deriving `num` from `index` on a separate line where an off-by-one or a wrong variable could sneak in. It's the standard idiom you'll see (and be expected to write) in interviews, and it's the form this book uses from here on.

---

## The three things hash maps are for

Almost every hash-map problem is one of these. Recognize the shape:

**1. Membership / dedup — "have I seen this?"** → use a **set**.
```python
def has_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False
```

**2. Counting / frequency — "how many of each?"** → use a **map of counts**.

Start with the primitive version, using nothing but a plain `dict`. To count, we check whether we've seen the key yet, then bump it; to find the winner, we walk the map tracking the best so far:
```python
def most_common_char(word):
    counts = {}
    for char in word:
        if char in counts:         # seen before → add one
            counts[char] += 1
        else:                      # first time → start at one
            counts[char] = 1
    best_char, best_count = None, 0
    for char, count in counts.items():    # manual max: track the biggest so far
        if count > best_count:
            best_char, best_count = char, count
    return best_char
```

> 💡 **Concept notes — three ways to read a dict**
> Notice we touched `counts` two different ways. `key in table` tests **keys** only — "is this key present?", `O(1)`, returns True/False (that's the `if char in counts` check). To *loop* a dict you pick what you want out of it: `for key in table` gives keys, `for value in table.values()` gives values, and `for key, value in table.items()` gives both as a pair (that's the `for char, count in counts.items()` line — `char` is the character, `count` its count). So `in` asks a yes/no question; `.items()` walks every character with its count. `in` tests, `.items()` iterates.

That works, and you should be able to write it cold. But feel the two bits of noise: the `if char in counts / else` dance every single count, and the manual max loop. Python hands you a cleaner tool for each:
```python
from collections import Counter
def most_common_char(word):
    counts = Counter(word)         # {char: how many times}, no if/else dance
    char, count = counts.most_common(1)[0]   # top entry unpacked: (char, count)
    return char
```
`Counter(word)` builds the whole count map in one pass, and `.most_common(1)` returns a list with just the top entry — `[(char, count)]`. The `[0]` pulls that single tuple out of the list, and unpacking names its two parts, so we return `char`. Same result, none of the boilerplate. Counting is everywhere: anagrams (do two strings have the same letter counts?), "first non-repeating character," "majority element." The instant you hear "how many times does X appear," reach for a count map.

**3. Grouping / indexing — "where / under what key does this belong?"** → use a **map of key→list**.

Again, primitive first. Each word gets a signature, and words that share it land in the same bucket. With a plain `dict` we have to create the empty list the first time we meet a key:
```python
def group_anagrams(words):
    groups = {}
    for word in words:
        key = "".join(sorted(word))   # anagrams share a sorted-letters key
        if key not in groups:         # first word for this key → start a list
            groups[key] = []
        groups[key].append(word)
    return list(groups.values())
```
Here the hash map's *key* is a computed signature ("sorted letters") that collapses many inputs into buckets. The pain is that `if key not in groups: groups[key] = []` line — pure setup we repeat every grouping problem. `defaultdict(list)` deletes it by auto-creating the empty list the moment you touch a new key:
```python
from collections import defaultdict
def group_anagrams(words):
    groups = defaultdict(list)
    for word in words:
        key = "".join(sorted(word))
        groups[key].append(word)   # no init dance — the list appears on demand
    return list(groups.values())
```
"Group things that share property P" → map from P to a list.

> 💡 **Concept notes — `Counter` and `defaultdict` (Python gifts)**
> Now you've felt what they replace. `collections.Counter(iterable)` builds a frequency map in one line (no `if key in map` dance) and supports handy ops like `.most_common(k)`. `collections.defaultdict(list)` auto-creates an empty list the first time you touch a key, so you skip the `if key not in map: map[key] = []` boilerplate. Both are interview-legal and make hash-map code dramatically cleaner — but reach for them *because* you've seen the primitive pain they remove, not as magic. Know them cold.

---

## When NOT to reach for a hash map

The reflex is strong, but two cautions:
- **Order matters / you need sorting?** A hash map has *no order.* If the problem needs sorted output or "the k-th smallest," a hash map alone won't do it (you'll want sorting or a heap — Ch 10).
- **The data is already sorted?** Then **two pointers** (Ch 3) often solves it in `O(1)` space — no map needed. A hash map's `O(n)` space is wasteful if the structure already gives you what you need.

Recognizing when *not* to use the tool is as senior as knowing when to use it.

> 💡 **Concept notes — edge cases to surface**
> Hash-map solutions rarely need a guard clause, which is exactly why their edge cases go unspoken — say them anyway in Understand. For two-sum: an **empty array** or a **single element** can't form a pair (decide the "not found" return, usually `[]`); **duplicate values** are the subtle one — does `[3, 3]` with target `6` count? (Yes — you record each index as you pass it, so the second `3` sees the first.) In Review, trace a two-element input and a no-valid-pair input — the two cases interviewers probe.

---

## Try it

1. *Contains Duplicate within distance k:* given `nums` and `k`, return True if there are two equal values whose indices differ by at most `k`. State the brute force and its Big-O, then remove the waste with a hash structure. (Hint: a set of the last `k` values, or a map of value→last index.)
2. *Valid Anagram:* are two strings anagrams? Solve it two ways — sorting, and a count map — and compare their complexities.
3. *First Unique Character:* return the index of the first non-repeating character in a string. Which of the three hash-map shapes is this?
4. Explain in one sentence why two-sum on a *sorted* array doesn't need a hash map at all. (You'll prove it next chapter.)
5. What's the space cost of the hash-map two-sum, and when might an interviewer push you to avoid it?

*Write your answers in [dsa-chapter-2-tryit.md](code/dsa-chapter-2-tryit.md).*

---

## The bumper sticker

> *If your brute force re-scans to ask "have I seen it / how many / where," a hash map answers in `O(1)` — trade space for time and the inner loop disappears.*

Next: when the array is *sorted*, you can often delete the hash map too — two pointers walking from both ends gives you `O(n)` time and `O(1)` space.

---

<div align="right">

[Chapter 3 →](dsa-chapter-3.md)

</div>
