# Chapter 1: How slow is slow?

*[Contents](dsa-README.md)*

- [ ] **Mark as read**

Someone hands you a list of numbers and asks: *are there two of them that add up to a target, say 10?*

You nod. Easy enough. Here's the obvious solution — the one you'd write knowing nothing:

```python
def has_sum_pair_brute(nums, target):
    for first in range(len(nums)):
        for second in range(first + 1, len(nums)):
            if nums[first] + nums[second] == target:
                return True
    return False
```

Try it:

```python
>>> has_sum_pair_brute([2, 7, 4, 1], 10)   # 4 + ... no; 2+7=9; 7+1=8... wait
False
>>> has_sum_pair_brute([3, 5, 2, 8], 10)   # 2 + 8
True
```

It works. Every pair gets checked. Done.

This is where we start *every single chapter*: the brute force. The slow, obvious, nested-loop solution. Don't be embarrassed by it — in an interview, a working brute force is a perfectly good first answer, and it's the thing we're going to *improve.* But to improve it, we need a way to say how slow it is. That's Big-O.

---

## What "slow" actually means

Look at the two loops. For a list of `n` numbers, the outer loop runs `n` times, and for each of those the inner loop runs up to `n` times. So we do roughly `n × n = n²` comparisons.

That count — *how the work grows as the input grows* — is what we measure. We call it **time complexity**, written with **Big-O notation**:

$$\text{this solution is } O(n^2)$$

> 💡 **Concept notes — what Big-O is really saying**
> Big-O describes the *shape* of the growth, not the exact number. We drop constants and lower terms: `3n² + 5n + 2` is just `O(n²)`, because for large `n` the `n²` dominates and the rest is noise. We don't care whether it's 3n² or 7n² — we care that *doubling the input roughly quadruples the work.* That's the useful, machine-independent truth.

Why does this matter? Because the difference between complexities is staggering at scale:

| Input size `n` | `O(n)` work | `O(n²)` work |
|---|---|---|
| 10 | 10 | 100 |
| 1,000 | 1,000 | 1,000,000 |
| 1,000,000 | 1,000,000 | 1,000,000,000,000 |

At a million items, `O(n)` does a million steps (instant) while `O(n²)` does a *trillion* (minutes to hours). In an interview, an `O(n²)` solution to a problem that has an `O(n)` answer is often the difference between pass and fail. **The whole game of DSA is lowering the exponent.**

---

## The complexity ladder

From fastest to slowest, the complexities you'll meet in this book:

| Big-O | Name | Doubling `n` does what? | Typical source |
|---|---|---|---|
| `O(1)` | constant | nothing | a hash-map lookup, arithmetic |
| `O(log n)` | logarithmic | adds one step | binary search (Ch 5) |
| `O(n)` | linear | doubles work | one loop over the data |
| `O(n log n)` | linearithmic | a bit more than doubles | good sorting, heap operations |
| `O(n²)` | quadratic | quadruples | two nested loops |
| `O(2ⁿ)` | exponential | *squares* the work | trying every subset (Ch 13) |

> 💡 **Concept notes — log n, intuitively**
> `O(log n)` shows up whenever each step *halves* the problem. If you have a million items and you can throw away half each step, you're done in ~20 steps (because 2²⁰ ≈ 1,000,000). That's why `log n` is almost as good as constant — even huge inputs need only a handful of steps. Memorize the reflex: **"halve each step" → `O(log n)`.**

---

## Space complexity — the other axis

Time isn't the only cost. **Space complexity** measures *extra memory* your solution uses as the input grows, same Big-O notation.

The brute force above uses `O(1)` space — just a couple of loop variables, no matter how big the list. But many speed-ups *buy time with space*: they use extra memory to avoid repeated work. You'll see that trade constantly, starting next chapter. When an interviewer asks "can you do better?", they sometimes mean time, sometimes space — and there's usually a tradeoff between them.

> 💡 **Concept notes — the central tradeoff**
> Most optimizations in this book are **space-for-time**: use extra memory (a hash map, a cache, a precomputed table) so you stop recomputing things. Occasionally you go the other way (time-for-space) when memory is tight. Always be ready to state *both* complexities — "this is `O(n)` time and `O(n)` space" — because the interviewer is judging the trade, not just the speed.

---

## The brute-force habit (your most important skill)

Here's the discipline this whole book is built on. When you see a problem:

1. **Write the brute force first** — in your head or out loud. The slow, obvious, check-everything solution. It proves you understand the problem and gives you a working baseline.
2. **State its complexity** — "this is `O(n²)` time." Naming the cost is what makes the next step possible.
3. **Find the waste** — ask: *what is this doing repeatedly that it shouldn't?* In our two-sum, for every element we re-scan the entire rest of the list looking for its complement. That re-scanning is the waste.
4. **Remove the waste with a pattern** — whatever data structure or technique deletes that specific repeated work. (For two-sum, it's a hash map — Chapter 2. We'll take this exact problem from `O(n²)` to `O(n)`.)

Notice we did *not* start by recognizing "oh, this is a hash-map problem." We started slow, found the waste, and the pattern revealed itself. That's the reflex that works on problems you've never seen — because unfamiliar problems don't come labeled.

> 💡 **Concept notes — why brute force first beats pattern-matching**
> Beginners try to leap straight to the clever solution and freeze when they don't recognize the problem. Strong candidates *always* have a brute force in their pocket, so they're never stuck with nothing — and improving a working solution is far easier than conjuring a perfect one from thin air. In the interview, saying "the brute force is `O(n²)`, let me see if I can do better" buys you a baseline *and* signals exactly the thinking the interviewer wants.

---

## A worked taste of the rest of the book

Just so you see where this goes, here's the two-sum waste removed (full explanation in Ch 2 — don't worry about the mechanics yet):

```python
def has_sum_pair_set(nums, target):
    seen = set()
    for num in nums:
        complement = target - num
        if complement in seen:
            return True
        seen.add(num)
    return False
```

One loop. For each number we work out the `complement` that would complete the pair and ask "have I already seen it?" — an `O(1)` set lookup — instead of re-scanning. That's `O(n)` time, `O(n)` space. We traded a little memory (the `seen` set) to delete the inner loop entirely. **Quadratic became linear.** That move, in a hundred costumes, is the entire book.

---

## Try it

1. State the time and space complexity of each, in your own words:
   - a single loop summing a list
   - two nested loops over the same list
   - a loop that halves a number until it reaches 1 (`while n > 1: n //= 2`)
2. For `n = 1,000,000`, roughly how many steps is `O(n)`, `O(n log n)`, and `O(n²)`? Which are feasible in an interview's "instant"?
3. Write the brute-force solution to: *"given a list, does it contain any duplicate?"* State its Big-O. Then describe (don't code yet) what waste a hash set would remove and the new complexity.
4. Explain "space-for-time" using the two `has_sum_pair` functions above: what extra memory did the fast version use, and what work did it buy back?

*Write your answers in [dsa-chapter-1-tryit.md](code/dsa-chapter-1-tryit.md).*

---

## The bumper sticker

> *Big-O is how work grows with input. Always write the brute force, name its complexity, find the repeated work — the pattern is whatever deletes it.*

Next: the single most useful waste-remover in all of interviewing — the hash map, and how trading space for time turns scans into instant lookups.

---

<div align="right">

[Chapter 2 →](dsa-chapter-2.md)

</div>
