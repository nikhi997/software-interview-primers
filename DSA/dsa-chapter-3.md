# Chapter 3: Walking from both ends

*[← Chapter 2](dsa-chapter-2.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

End of last chapter, a hint: two-sum on a *sorted* array doesn't need a hash map. This chapter shows why, and introduces a pattern that gives you `O(n)` time with `O(1)` space — no extra memory at all — whenever the data has structure you can exploit from the ends inward.

It's called **two pointers**, and the pain it removes is the same nested-loop waste — but instead of paying memory (a hash map), it pays *nothing*, by being clever about *which* pairs to check.

---

## The brute force and its waste

*Given a **sorted** array, find two numbers that sum to a target.*

Brute force, same as always:

```python
def two_sum_sorted_brute(nums, target):
    for first in range(len(nums)):
        for second in range(first + 1, len(nums)):
            if nums[first] + nums[second] == target:
                return [first, second]
    return []
```

`O(n²)`. But notice we're ignoring a gift: **the array is sorted.** The brute force checks pairs blindly, learning nothing from the fact that values increase left to right. That ignored structure *is* the waste.

---

## The move: one pointer at each end

Put a pointer at the **left** (smallest) and one at the **right** (largest). Look at their sum:

- Sum **too small**? The only way to *increase* it is to move `left` rightward (to a bigger number). Moving `right` would only shrink it.
- Sum **too big**? Move `right` leftward (to a smaller number).
- Sum **exactly right**? Found it.

```python
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        pair_sum = nums[left] + nums[right]
        if pair_sum == target:
            return [left, right]
        elif pair_sum < target:
            left += 1          # need bigger -> move left up
        else:
            right -= 1         # need smaller -> move right down
    return []
```

Each step moves one pointer inward, so they meet after at most `n` steps: **`O(n)` time, `O(1)` space.** No hash map, no extra memory. We beat the previous chapter's space cost by *using the sortedness* instead of paying for a map.

> 💡 **Concept notes — why this is correct, not just fast**
> Every step *safely eliminates* a candidate. When the sum is too small, `nums[left]` paired with *anything* `≤ nums[right]` is also too small — so `left` can never be part of the answer with a smaller-or-equal partner, and we discard it forever by moving right. We never miss a valid pair because each move only rules out pairs that *can't* work. That "each move eliminates a whole set of impossible candidates" is the soul of two pointers — and why it needs sorted (or otherwise monotonic) data to be valid.

---

## The two flavors of two pointers

**1. Opposite ends (converging).** Start wide, move inward. For: pair-sum in sorted arrays, palindrome checks, container-with-most-water, reversing.

```python
def is_palindrome(text):
    left, right = 0, len(text) - 1
    while left < right:
        if text[left] != text[right]:
            return False
        left += 1
        right -= 1
    return True
```

**2. Same direction (slow/fast, a.k.a. read/write).** Both start at the left; one moves only when a condition holds. For: removing duplicates in-place, partitioning, "move zeros to the end." The trailing pointer marks "where the next good element goes" — the *write* position; the leading pointer scans ahead — the *read* position.

```python
def remove_duplicates(nums):                  # sorted array, edit in place
    if not nums:
        return 0
    write = 0                                  # last unique position — where we write next
    for read in range(1, len(nums)):
        if nums[read] != nums[write]:
            write += 1
            nums[write] = nums[read]           # place the next unique value
    return write + 1                           # length of the unique prefix
```

That `if not nums` guard is load-bearing, not decoration: without it an empty array skips the loop and falls through to `return write + 1 = 1`, claiming one unique element that isn't there. Empty and single-element arrays are exactly the inputs to say out loud before you start coding.

> 💡 **Concept notes — the read/write mental model**
> In the same-direction flavor, name the two pointers for their *jobs*: a `write` position (the boundary of the "good" region you're building) and a `read` position (scanning every element). `read` always moves; `write` advances only when you find something worth keeping. This in-place rearrangement is `O(n)` time and `O(1)` space — no second array. The same two-pointer idea returns in Chapter 7 for linked lists, but there the pointers move at different *speeds*, so we'll call them `slow` and `fast` — speed, not read/write, is the point there.

---

## How to recognize a two-pointer problem

The signal lights:
- The array (or string) is **sorted**, or sortable without losing the answer.
- You're looking for a **pair** or **triple** that meets a condition (sum, difference).
- You need to do it in **`O(1)` space** (interviewer says "can you avoid the extra memory?").
- It's a **palindrome / reversal / in-place rearrangement.**

> 💡 **Concept notes — hash map vs two pointers, the decision**
> Both can solve pair-sum. Choose by the constraints:
> - **Unsorted + indices needed + extra space OK** → hash map (Ch 2), `O(n)` time, `O(n)` space.
> - **Sorted (or you may sort) + want `O(1)` space** → two pointers, `O(n)` time, `O(1)` space (plus `O(n log n)` if you must sort first).
> If sorting is free (already sorted) or its `O(n log n)` is acceptable, two pointers wins on space. If the array is unsorted and you can't afford to sort, the hash map wins. Stating this tradeoff out loud is exactly the senior signal.

---

## Scaling up: three-sum (the classic)

*Find all unique triples that sum to zero.* Start with the obvious brute force — three nested loops trying every triple:

```python
def three_sum_brute(nums):
    count = len(nums)
    triples = []
    for first in range(count):
        for second in range(first + 1, count):
            for third in range(second + 1, count):        # every triple
                if nums[first] + nums[second] + nums[third] == 0:
                    triples.append(sorted([nums[first], nums[second], nums[third]]))
    return triples
```

`O(n³)` — three nested loops, billions of checks on a few thousand numbers. And run it on `[-1, 0, 1, 2, -1, -4]` to see a *second* problem staring back:

```
[[-1, 0, 1], [-1, -1, 2], [-1, 0, 1]]     # [-1, 0, 1] shows up twice
```

Two pains, then. The **cubic wall**, and **duplicate triples** — the same three values reached through different index combinations (the two `-1`s sit at different positions). Fix the speed first; hold the duplicate problem, we come back to it.

**Delete a loop.** Sort the array, then fix one element and two-pointer the rest. Once sorted, fixing `nums[anchor]` turns the rest into "find two values summing to `-nums[anchor]`" — the exact sorted-pair problem two pointers already solve in `O(n)`:

```python
def three_sum_two_pointer(nums):
    nums.sort()
    triples = []
    for anchor in range(len(nums)):
        left, right = anchor + 1, len(nums) - 1
        while left < right:
            triple_sum = nums[anchor] + nums[left] + nums[right]
            if triple_sum == 0:
                triples.append([nums[anchor], nums[left], nums[right]])
                left += 1
                right -= 1
            elif triple_sum < 0:
                left += 1
            else:
                right -= 1
    return triples
```

`O(n²)` now — one anchor loop, an `O(n)` two-pointer walk inside. The cubic wall is gone. But run it on the same input and the duplicates are *still there*:

```
[[-1, -1, 2], [-1, 0, 1], [-1, 0, 1]]     # sorting lined the two -1s up, so the anchor lands on -1 twice
```

**Patch the duplicates.** The blunt, obvious fix: don't trust the list — dump every triple into a set so copies collapse on their own. A list can't be a set key, so store each triple as a sorted tuple:

```python
def three_sum_dedup_with_set(nums):
    nums.sort()
    triples = set()
    for anchor in range(len(nums)):
        left, right = anchor + 1, len(nums) - 1
        while left < right:
            triple_sum = nums[anchor] + nums[left] + nums[right]
            if triple_sum == 0:
                triples.add((nums[anchor], nums[left], nums[right]))
                left += 1
                right -= 1
            elif triple_sum < 0:
                left += 1
            else:
                right -= 1
    return [list(triple) for triple in triples]
```

Correct and clear, and the cost is named out loud: an extra set holding every triple we find, plus a hash of three numbers on each insert. In an interview this version already passes. Now buy the memory back.

**Optimize: skip the duplicates instead of storing them.** The set exists only to swallow repeats. If we simply *never generate* a repeat, we don't need it. Two skips do exactly that: once an anchor value has been used, jump past any copies of it; and after recording a hit, walk `left` past any copies of the value it just matched.

```python
def three_sum(nums):
    nums.sort()
    triples = []
    for anchor in range(len(nums)):
        if anchor > 0 and nums[anchor] == nums[anchor - 1]:
            continue                                      # this anchor value already did its work
        left, right = anchor + 1, len(nums) - 1
        while left < right:
            triple_sum = nums[anchor] + nums[left] + nums[right]
            if triple_sum == 0:
                triples.append([nums[anchor], nums[left], nums[right]])
                left += 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1                             # skip repeated left values
            elif triple_sum < 0:
                left += 1
            else:
                right -= 1
    return triples
```

Still `O(n²)` time, but `O(1)` extra space instead of a set of every triple — we spent two cheap comparisons to buy back all that memory. The only difference from the previous version is those two skip lines; everything else is the same two-pointer walk. This "sort, then fix-one-and-two-pointer, then skip repeats" template solves a whole family of k-sum problems.

> 💡 **Concept notes — edge cases to surface**
> Two-pointer code lives and dies on its boundaries, so name them in Understand: **empty input** and a **single element** (no pair or triple exists); an **all-equal array** (`remove_duplicates` collapses to length 1, and `three_sum` must not emit the same triple repeatedly); and **duplicates** in general — the reason `three_sum` skips repeated anchors and repeated values. In Review, trace the pointers on a two-element array, the smallest case where `left < right` runs exactly once.

---

## Try it

1. *Valid Palindrome (alphanumeric only):* check if a string reads the same forwards and backwards, ignoring non-letters and case. Use opposite-end pointers.
2. *Move Zeroes:* push all zeros to the end of an array in place, keeping the order of non-zeros. Which flavor (slow/fast or converging)?
3. *Container With Most Water:* given heights, two lines form a container; maximize the water area. Start with pointers at both ends — which one do you move, and why? (Hint: move the *shorter* line inward.)
4. State the exact tradeoff between the hash-map and two-pointer solutions to pair-sum, in terms of both time and space, including the cost of sorting.
5. Why does two pointers *require* sorted (or monotonic) data to be correct? What breaks if the array is unsorted?

*Write your answers in [dsa-chapter-3-tryit.md](code/dsa-chapter-3-tryit.md).*

---

## The bumper sticker

> *When data is sorted, two pointers walking inward (or slow/fast in one direction) deletes the nested loop for free — `O(n)` time, `O(1)` space — because each move eliminates a whole set of impossible candidates.*

Next: a pointer pattern for *contiguous* chunks — the sliding window, which stops you from recomputing the overlap between one subarray and the next.

---

<div align="right">

[Chapter 4 →](dsa-chapter-4.md)

</div>
