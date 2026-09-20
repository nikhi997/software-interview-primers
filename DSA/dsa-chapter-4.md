# Chapter 4: The window that slides instead of restarting

*[← Chapter 3](dsa-chapter-3.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

Two pointers found *pairs* in sorted data. This chapter is about *contiguous chunks* — subarrays or substrings — and the waste it removes is one of the most satisfying in all of DSA: **recomputing the overlap.**

The pattern is the **sliding window**, and once you see the waste it deletes, you'll spot it everywhere "contiguous" and "longest/shortest/sum" appear in the same sentence.

---

## The brute force and its waste

*Find the maximum sum of any contiguous subarray of length `k`.*

Brute force: for every starting position, sum the next `k` elements.

```python
def highest_window_sum_brute(nums, k):
    max_sum = float("-inf")
    for start in range(len(nums) - k + 1):
        window_sum = sum(nums[start:start + k])   # re-add k elements every time
        max_sum = max(max_sum, window_sum)
    return max_sum
```

`O(n × k)`. Now look at the waste. When the window moves from position `i` to `i+1`, it loses one element on the left and gains one on the right — but `sum(nums[i:i+k])` *recomputes all `k` elements from scratch* every time. The two consecutive windows overlap in `k-1` elements, and we pointlessly re-add all of them.

```
window at i:    [ a b c d ] e f
window at i+1:    a [ b c d e ] f      ← b,c,d are SHARED, re-summed for nothing
```

That re-summing of the shared part is the waste. The fix: don't rebuild — **slide.**

---

## The move: add the new, subtract the old

Keep a running `window_sum`. When the window slides one step: add the element entering on the right, subtract the element leaving on the left. Each slide is `O(1)`, not `O(k)`.

```python
def highest_window_sum(nums, k):
    window_sum = sum(nums[:k])               # first window, once
    max_sum = window_sum
    for entering in range(k, len(nums)):
        window_sum += nums[entering] - nums[entering - k]   # add entering, drop leaving
        max_sum = max(max_sum, window_sum)
    return max_sum
```

`O(n)` time, `O(1)` space. We compute the first window once, then every subsequent window is a single add and subtract. The `k-1` overlapping elements are never touched again. **`O(n·k)` became `O(n)`** by never recomputing the overlap.

> 💡 **Concept notes — the sliding-window insight**
> Consecutive windows share almost all their content. The brute force throws that away and rebuilds; the window *updates incrementally.* This is the same "don't recompute, reuse" instinct as caching in HLD and memoization in DP (Ch 14) — keep a running result and adjust it by the delta. Whenever you're scanning *contiguous* fixed or variable chunks and recomputing each from scratch, a sliding window deletes the redundancy.

That was a **fixed-size** window. The richer, more common interview version is the **variable-size** window.

---

## Variable-size windows: grow and shrink

Most window problems don't fix `k` — they ask for the *longest* or *shortest* contiguous run satisfying a condition. The template: a `right` pointer **grows** the window by one each step; whenever the window **violates** the condition, a `left` pointer **shrinks** it until it's valid again.

The canonical problem: *longest substring without repeating characters.*

The brute force just spells out the definition: try every substring, check each one for a repeat, keep the longest clean run.

```python
def longest_substring_without_repeat_brute(text):
    def is_unique(chunk):
        return len(set(chunk)) == len(chunk)    # a repeat makes the set smaller
    longest = 0
    for start in range(len(text)):
        for end in range(start, len(text)):
            if is_unique(text[start:end + 1]):  # re-scan the whole substring
                longest = max(longest, end - start + 1)
    return longest
```

That's `O(n³)` — `O(n²)` substrings, each re-scanned for uniqueness (and each slice `text[start:end+1]` is itself `O(n)`). The waste is glaring: every substring re-checks characters the previous one already cleared. A sliding window keeps a running `set` and adjusts it by the delta instead of rebuilding from scratch.

```python
def longest_substring_without_repeat(text):
    seen = set()
    left = 0
    longest = 0
    for right in range(len(text)):
        while text[right] in seen:           # window became invalid (a repeat)
            seen.remove(text[left])          # shrink from the left
            left += 1
        seen.add(text[right])                # now valid; include the new char
        longest = max(longest, right - left + 1)   # window size = right - left + 1
    return longest
```

Walk it: `right` marches forward including each new character. The moment we'd include a duplicate, we shrink from `left` — dropping characters until the duplicate is gone — then continue. Every character enters the window once and leaves at most once, so even with the inner `while`, it's **`O(n)` total**, not `O(n²)`.

Trace it on `"abba"` to see the window breathe:

| `right`, char | duplicate? | shrink | window `[left, right]` | `seen` | `longest` |
| --- | --- | --- | --- | --- | --- |
| 0 `a` | no | — | `a` | `{a}` | 1 |
| 1 `b` | no | — | `ab` | `{a, b}` | 2 |
| 2 `b` | yes | drop `a` then `b`; `left` → 2 | `b` | `{b}` | 2 |
| 3 `a` | no | — | `ba` | `{a, b}` | 2 |

The answer is 2. Notice the second `b` forces `left` all the way to index 2, dropping *both* earlier characters — the window never holds a repeat.

> 💡 **Concept notes — why two nested loops can still be `O(n)`**
> It *looks* like `O(n²)` because of the `while` inside the `for`. But `left` only ever moves forward, never resets — across the whole run it advances at most `n` times total. So `right` does `n` steps and `left` does ≤ `n` steps: `O(n)` combined. This "amortized" counting — *each element enters and exits the window once* — is the key to trusting variable windows are linear. Don't let the nested loop fool you.

---

## The variable-window template

Nearly every variable window fits this skeleton. Memorize the shape, not a specific problem:

```python
def window(text):
    left = 0
    state = ...                      # whatever tracks the window (counts, sum, set)
    best = ...
    for right in range(len(text)):
        # 1. EXPAND: include text[right] in state
        while CONDITION_VIOLATED:    # 2. SHRINK until the window is valid again
            # remove text[left] from state
            left += 1
        # 3. UPDATE the answer using the now-valid window [left, right]
    return best
```

The three moving parts you fill in per problem:
1. **What state describes the window?** A running sum, a character→count map, a set of seen items.
2. **What makes it invalid?** A repeat, a sum exceeding the target, more than `k` distinct characters.
3. **What are you optimizing?** Longest window (update on every valid window) or shortest (update right after expanding, then shrink greedily).

> 💡 **Concept notes — longest vs shortest changes where you update**
> For **longest valid** window: expand freely, shrink only when invalid, and record the size when valid. For **shortest valid** window (e.g., "smallest subarray with sum ≥ target"): expand until valid, then shrink *as much as possible while still valid*, recording the size each time you shrink. Same skeleton, but "shortest" greedily shrinks to find the minimum. Knowing which direction you're optimizing tells you where the `best = ...` line goes.

---

## Recognizing a sliding-window problem

The signals, almost always all present:
- The answer is a **contiguous** subarray or substring (not a subsequence — order-preserving but possibly gapped — which is usually DP).
- You want the **longest / shortest / max-sum / min-sum** chunk satisfying a condition.
- The brute force is "try every subarray" = `O(n²)` or worse, and consecutive subarrays **overlap.**

If it's contiguous and you're recomputing overlapping chunks, slide instead of restart.

> 💡 **Concept notes — edge cases to surface**
> Windows have their own boundary traps worth naming: an **empty array** or one **shorter than `k`** (the fixed-size window can't form even once — decide what to return); a window that's **never valid** (longest → the answer stays `0`; shortest → nothing qualifies, often return `0` or a sentinel); and **`k == 0`** or an all-identical string. In Review, confirm the first window forms correctly and `left` never overtakes `right`.

---

## Try it

1. *Minimum Size Subarray Sum:* shortest contiguous subarray with sum ≥ target. Which of the three template parts differ from the "longest" version, and where does the answer update?
2. *Longest Substring with At Most K Distinct Characters:* what's the window state, and what makes it invalid? (Hint: a char→count map; invalid when `len(map) > k`.)
3. *Maximum Average Subarray (size k):* a fixed-size window. Write the slide step.
4. Explain, in amortized terms, why the variable-window solution with a nested `while` is `O(n)` and not `O(n²)`.
5. Why is "longest subsequence" (gaps allowed) usually *not* a sliding-window problem? What changes when the chunk doesn't have to be contiguous?

*Write your answers in [dsa-chapter-4-tryit.md](code/dsa-chapter-4-tryit.md).*

---

## The bumper sticker

> *For contiguous chunks, don't rebuild each one — slide: add the entering element, drop the leaving one. Expand with `right`, shrink with `left` when invalid, and the overlap is never recomputed.*

Next: a different way to delete work — instead of reusing overlap, throw away *half* the remaining possibilities every step. Binary search.

---

<div align="right">

[Chapter 5 →](dsa-chapter-5.md)

</div>
