# Chapter 5: Throwing away half the answers

*[← Chapter 4](dsa-chapter-4.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

Every pattern so far deleted *repeated* work. This one deletes *most of the search space itself.* Each step, binary search throws away **half** the remaining possibilities — which is why it turns `O(n)` into `O(log n)`, the difference between 1,000,000 steps and 20.

It's the most famous algorithm in interviewing, and also the most subtly bug-prone. We'll get the mechanics exactly right, then learn the move that makes it powerful: **binary search on the answer**, which solves problems that don't look like search at all.

---

## The brute force and its waste

*Find the index of a target in a **sorted** array.*

Brute force: scan left to right.

```python
def find_brute(nums, target):
    for index, num in enumerate(nums):
        if num == target:
            return index
    return -1
```

`O(n)`. The waste: **the array is sorted and we're ignoring it.** When we check the middle element and it's larger than the target, *every element to its right is also larger* — we could discard the entire right half in one comparison. Linear scan throws that away, checking elements one at a time.

---

## The move: probe the middle, discard a half

Keep a `low` and `high` bound. Look at the middle. Three cases:
- Middle **equals** target → found it.
- Middle **less than** target → the answer must be in the **right** half; discard the left.
- Middle **greater than** target → answer is in the **left** half; discard the right.

```python
def binary_search(nums, target):
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = (low + high) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            low = mid + 1           # discard left half (including mid)
        else:
            high = mid - 1          # discard right half (including mid)
    return -1
```

Each step halves the range, so it finishes in `O(log n)`. A million elements → ~20 steps. `O(1)` space.

> 💡 **Concept notes — the three bugs everyone hits**
> Binary search is short but treacherous. The three classic mistakes:
> 1. **Loop condition:** use `while low <= high` (with `≤`) when searching for an exact value, so the final single-element range is still checked. Using `<` skips it.
> 2. **Updating bounds:** always move *past* mid — `low = mid + 1` and `high = mid - 1`. Writing `low = mid` (without +1) can loop forever when the range stops shrinking.
> 3. **Midpoint overflow:** in languages with fixed-size ints, `(low + high)` can overflow; `low + (high - low) // 2` avoids it. Python ints don't overflow, but say it — interviewers in Java/C++ care.
> Get these three right and binary search stops being scary.

---

## The deeper idea: search on a *condition*, not a value

Here's the leap that makes binary search a power tool. The exact-match version is the *least* important form. The real pattern is: **find the boundary where a yes/no condition flips.**

If you can arrange your possibilities so the condition goes `False False False ... True True True` (monotonic), you can binary-search for the *first* `True` — even if there's no literal "target" to match.

Two things change from the exact-match template, and both are forced by one fact: **the `mid` that satisfies the condition might itself be the answer.** In exact match, once we look at `mid` and it isn't equal, we *discard* it (`high = mid - 1`) — we've ruled it out. But here a `True` at `mid` could be the very first `True`, so we must **keep** `mid` in the range: `high = mid`, not `high = mid - 1`. And because `high = mid` can leave the range one element wide without shrinking, we switch the loop to `while low < high` — converging until a single survivor remains — instead of `while low <= high`. (Keep the old `low <= high` with `high = mid` and you get an infinite loop: when `low == high == mid` and the condition is true, `high = mid` changes nothing and the loop spins forever.)

```python
def first_true(low, high, condition):
    """Find the smallest value in [low, high] where condition(value) is True."""
    while low < high:
        mid = (low + high) // 2
        if condition(mid):
            high = mid          # mid might be the answer; keep it in range
        else:
            low = mid + 1       # mid is too small; discard it
    return low
```

> 💡 **Concept notes — the monotonic-predicate insight**
> Binary search doesn't need a sorted array of *numbers* — it needs a **monotonic predicate**: a yes/no test that, once it becomes true, stays true. "Is `x` ≥ target?" is monotonic over a sorted array. But so is "Can we finish in `x` days at this speed?" or "Does a value ≥ `x` exist?" Whenever your answer space can be ordered so the property flips exactly once, you can binary-search for that flip in `O(log n)` — *even when the problem never mentions searching.* This is the single most underused idea in interviews.

This unlocks two huge families: **finding boundaries** (first/last occurrence, insertion point) and **binary search on the answer.**

---

## Finding boundaries

"Find the *first* position where ..." or "*how many* are less than X" are boundary problems. Python's `bisect` does this, but know the manual version:

```python
def first_occurrence(nums, target):
    low, high = 0, len(nums)
    while low < high:
        mid = (low + high) // 2
        if nums[mid] >= target:     # predicate: "is this >= target?"
            high = mid
        else:
            low = mid + 1
    return low                      # first index where nums[index] >= target
```

The predicate "is `nums[mid] >= target`?" is `False...False True...True`. We binary-search the flip point. Change the predicate and you get last-occurrence, count-less-than, insertion-index — all `O(log n)`.

---

## Binary search on the answer (the interview favorite)

This is where it gets surprising. Some problems ask for a *number* — a minimum speed, a smallest capacity, the largest minimum — and don't look like search at all. But if you can write a function "is answer `x` feasible?" that's monotonic, you binary-search the *answer itself.*

Classic: *Koko eating bananas. Given piles and a number of `hours`, find the minimum eating speed so she finishes all bananas in time.*

```python
import math

def min_eating_speed(piles, hours_available):
    def hours_needed(speed):
        hours = 0
        for pile in piles:
            hours += math.ceil(pile / speed)   # this pile: ceil(size / speed) hours
        return hours

    def can_finish(speed):
        return hours_needed(speed) <= hours_available   # faster -> fewer hours

    low, high = 1, max(piles)                # speed range
    while low < high:
        mid = (low + high) // 2
        if can_finish(mid):
            high = mid                       # this speed works; try slower
        else:
            low = mid + 1                    # too slow; must go faster
    return low
```

We never sorted anything. We binary-searched over *possible speeds* (1 to max pile), using "can she finish at this speed?" as the monotonic predicate (faster speed → fewer hours → stays feasible). `O(n log(max_pile))`. The brute force — try every speed from 1 upward — is `O(n · max_pile)`; binary search makes the speed search logarithmic.

> 💡 **Concept notes — how to spot "binary search on the answer"**
> Three signals fire together: (1) the problem asks for a **minimum/maximum value** ("smallest capacity," "minimum speed," "largest minimum distance"); (2) you can **easily check** if a given candidate value works (a feasibility test); and (3) feasibility is **monotonic** (if `x` works, everything bigger — or smaller — also works). When all three hold, binary-search the answer range and call the feasibility test at each midpoint. "Minimize the maximum" / "maximize the minimum" phrasings are dead giveaways.

---

## Recognizing a binary-search problem

- The array (or answer space) is **sorted or monotonic.**
- The brute force is a **linear scan or trying every candidate value**, and each probe could rule out a whole half.
- Phrasing like **"first/last," "minimum/maximum value such that," "minimize the maximum."**
- A target complexity of **`O(log n)`** or `O(n log n)` is hinted ("can you do better than linear?").

> 💡 **Concept notes — edge cases to surface**
> Binary search is where boundary bugs breed, so surface them explicitly: an **empty array**, a **single element**, and a **target smaller or larger than everything** (the answer sits at index `0` or `n`, or "not found"). For "first/last occurrence," **duplicates** are the whole point — decide which end you're pinning. This is the chapter's "three bugs everyone hits" restated as inputs: trace them in Review and the off-by-one and infinite-loop bugs surface before the interviewer finds them.

---

## Try it

1. *Search Insert Position:* find where a target should be inserted in a sorted array to keep it sorted. Which predicate?
2. *Find First and Last Position:* return the range of a target's occurrences in a sorted array. (Two binary searches — different predicates.)
3. *Capacity to Ship Packages in D Days:* minimum ship capacity to ship all packages within `D` days. Identify the answer range and the monotonic feasibility test — it's binary-search-on-the-answer.
4. Write out the three classic binary-search bugs and how each is avoided.
5. Explain why "minimize the maximum X" is a tell for binary search on the answer, using the Koko example's structure.

*Write your answers in [dsa-chapter-5-tryit.md](code/dsa-chapter-5-tryit.md).*

---

## The bumper sticker

> *Binary search deletes half the possibilities per step. Its real power isn't matching a value — it's finding where a monotonic yes/no condition flips, which lets you binary-search the answer itself.*

That closes Part 1 — the array/string patterns. You can now take a sequence problem, state the brute force, and decide whether hashing, two pointers, sliding window, or binary search removes the waste. Part 2 moves to *structures* — stacks, linked lists, trees, and heaps — each of which exists to make one specific operation fast.

---

<div align="right">

[Chapter 6 →](dsa-chapter-6.md)

</div>
