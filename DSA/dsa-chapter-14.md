# Chapter 14: Stop re-solving the same subproblem — dynamic programming

*[← Chapter 13](dsa-chapter-13.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

Dynamic programming has a fearsome reputation, and it's undeserved. DP is not a new structure or a magic formula — it's a single, simple observation applied with discipline: **if you find yourself solving the same subproblem over and over, solve it once and remember the answer.** That's it. The reputation comes from people meeting DP as a wall of array-filling formulas, instead of meeting it where it's born: as a brute-force recursion that happens to repeat itself.

This chapter builds DP the honest way — start with the recursion, *see* the repetition, then kill it.

---

## The brute force and its waste — made visible

*Compute the `n`th Fibonacci number.* The definition is recursive, so the brute force is too:

```python
def fibonacci_brute_force(n):
    if n <= 1:
        return n
    return fibonacci_brute_force(n - 1) + fibonacci_brute_force(n - 2)
```

This is `O(2ⁿ)` — catastrophic. Why? Draw the call tree for `fib(5)`:

```
                    fib(5)
              /                \
          fib(4)              fib(3)
          /     \            /     \
      fib(3)   fib(2)    fib(2)   fib(1)
      /   \
  fib(2)  fib(1)        ... fib(2) computed 3 times, fib(3) twice ...
```

`fib(3)` is computed twice, `fib(2)` three times, and it explodes as `n` grows. **That repeated recomputation of identical subproblems is the waste** — the exact same waste, made dramatic. DP removes it.

---

## Fix #1: memoization (top-down) — just cache the recursion

Keep a cache. Before computing a subproblem, check if you already did. This changes *nothing* about the logic — you only add a memory.

```python
def fibonacci_top_down(n, cache=None):
    if cache is None:
        cache = {}
    if n <= 1:
        return n
    if n in cache:
        return cache[n]                  # already solved -> return instantly
    cache[n] = fibonacci_top_down(n - 1, cache) + fibonacci_top_down(n - 2, cache)
    return cache[n]
```

Now each subproblem `fib(0)..fib(n)` is computed **once**: `O(n)` time, `O(n)` space. Python even has a built-in: decorate any pure recursion with `@functools.lru_cache(None)` and it's memoized for free.

> 💡 **Concept notes — the two ingredients DP requires**
> DP applies when a problem has both: (1) **overlapping subproblems** — the same smaller problems recur (like `fib(3)` above); and (2) **optimal substructure** — the answer is built from answers to those subproblems. If subproblems *don't* overlap, caching buys nothing — that's plain recursion/backtracking (Chapter 13). The whole art of "spotting DP" is noticing the overlap, which is why **drawing the recursion tree and looking for repeated nodes** is the most reliable way to recognize a DP problem.

---

## Fix #2: tabulation (bottom-up) — fill an array in order

Memoization is recursion + cache. **Tabulation** flips it: solve the *smallest* subproblems first and build up, filling a table, no recursion at all. Same answers, often a little faster (no call overhead), and it makes the *space* optimization obvious.

```python
def fibonacci_bottom_up(n):
    if n <= 1:
        return n
    table = [0] * (n + 1)
    table[1] = 1
    for index in range(2, n + 1):
        table[index] = table[index - 1] + table[index - 2]    # build from smaller, already-known answers
    return table[n]
```

And since each value needs only the previous two, you can drop the array entirely — `O(1)` space:

```python
def fibonacci_constant_space(n):
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current   # roll forward, keep only what's needed
    return previous
```

> 💡 **Concept notes — top-down vs bottom-up, which to write**
> **Top-down (memoization)** is usually *easier to derive*: write the natural brute-force recursion, then add `@lru_cache`. Start here in an interview — it gets you to correct quickly. **Bottom-up (tabulation)** removes recursion overhead and makes **space optimization** visible (you can often keep just the last row or two, like Fibonacci's two variables). A common strong move: explain the recursion top-down, then mention you *could* convert to bottom-up and reduce space. They have the same time complexity — the difference is style and constant factors.

---

## The DP recipe (works for almost every DP problem)

Don't memorize solutions; derive them with this sequence:

1. **Define the state.** What does `dp[i]` (or `dp[i][j]`) *mean*? This is the hardest and most important step. E.g., "`dp[i]` = the longest increasing subsequence ending at index `i`."
2. **Write the recurrence.** How does a state depend on smaller states? E.g., "`dp[i] = 1 + max(dp[j])` for all `j < i` with `nums[j] < nums[i]`."
3. **Set the base cases.** The smallest states you know outright.
4. **Decide the order.** Top-down (recurse + memo) or bottom-up (fill in dependency order).
5. **Find the answer.** Is it `dp[n]`? The max over all `dp[i]`? Read it off the table.

> 💡 **Concept notes — "defining the state" is the whole game**
> 90% of DP difficulty is step 1: choosing what a subproblem *means*. Once `dp[i]` has a precise definition, the recurrence usually follows mechanically. Classic state shapes worth knowing: **1-D over an index** ("best ending at/using up to `i`" — house robber, climbing stairs, LIS); **2-D over two sequences** ("best matching of first `i` of A and first `j` of B" — edit distance, longest common subsequence); **2-D over a range** ("best on the interval `[i, j]`"); **knapsack** ("best using the first `i` items with capacity `c`"). Recognizing which shape fits often comes from having *seen* a few — which is why DP rewards deliberate practice more than any other topic.

---

## A real one: coin change

*Fewest coins to make `amount` from given denominations.* Follow the recipe's advice and start top-down, because the recursion is the easy part to *derive*. State the subproblem out loud: `fewest(remaining)` = the fewest coins to make amount `remaining`. To make it, try each coin, spend it, and ask the recursion for the rest:

```python
from functools import lru_cache

def fewest_coins_for_topdown(coins, amount):
    @lru_cache(maxsize=None)
    def fewest(remaining):
        if remaining == 0:
            return 0                           # base: 0 coins make amount 0
        if remaining < 0:
            return float("inf")                # this path overshot — dead end
        best = float("inf")
        for coin in coins:
            best = min(best, 1 + fewest(remaining - coin))   # spend one coin, recurse on the rest
        return best
    result = fewest(amount)
    return result if result != float("inf") else -1
```

Strip the `@lru_cache` and this *is* the brute force — it re-solves `fewest(2)` again and again down different coin orderings, exponential work. The cache remembers each `remaining` the first time it's computed and collapses the whole thing to `O(amount × coins)`. That is the entire DP move: an expensive recursion tree, memoized.

**Now flip it bottom-up.** Tabulation solves the same subproblems smallest-first, filling an array with no recursion — which makes the `O(amount × coins)` cost plain and drops the call overhead:

```python
def fewest_coins_for(coins, amount):
    unreachable = float("inf")
    fewest = [unreachable] * (amount + 1)
    fewest[0] = 0                              # base: 0 coins make amount 0
    for current_amount in range(1, amount + 1):
        for coin in coins:
            if coin <= current_amount:
                using_this_coin = fewest[current_amount - coin] + 1
                fewest[current_amount] = min(fewest[current_amount], using_this_coin)
    if fewest[amount] == unreachable:
        return -1
    return fewest[amount]
```

Same recipe, just read off a table instead of the recursion: state = "fewest coins for amount `a`," recurrence = "min over coins of `fewest[a - coin] + 1`," base = `fewest[0] = 0`, answer = `fewest[amount]`.

Trace the table for `coins = [1, 2]`, `amount = 4`, starting from `fewest = [0, ∞, ∞, ∞, ∞]`:

| amount `a` | best via coin 1 | best via coin 2 | `fewest[a]` |
| --- | --- | --- | --- |
| 1 | `fewest[0] + 1 = 1` | coin too big | 1 |
| 2 | `fewest[1] + 1 = 2` | `fewest[0] + 1 = 1` | 1 |
| 3 | `fewest[2] + 1 = 2` | `fewest[1] + 1 = 2` | 2 |
| 4 | `fewest[3] + 1 = 3` | `fewest[2] + 1 = 2` | 2 |

Each row builds only on rows already filled, so the answer `fewest[4] = 2` (a 2 and a 2) is read straight off the table — no recomputation, the whole point of DP.

---

## Recognizing a DP problem

- **"Maximum/minimum/longest/shortest ... such that ..."** with choices at each step.
- **"How many ways to ..."** (counting paths, decodings, combinations).
- **"Can you reach / partition / make ..."** (yes/no over choices).
- Your **backtracking** solution (Chapter 13) is correct but too slow, *and* the recursion tree has **repeated subproblems**.
- Keywords: **subsequence, substring, partition, knapsack, edit distance, paths in a grid, stairs, robbing houses.**

> 💡 **Concept notes — edge cases to surface**
> DP's edge cases are its **base cases** — say them as inputs, not just table entries: **`n == 0`** or an empty sequence, **amount `0`** in coin change (zero coins — `fewest[0] = 0`), and an **unreachable target** (coin change returns `-1`; the `float('inf')` sentinel is how you tell "impossible" from "expensive"). In Review, evaluate the smallest state by hand, confirm the base case, then check the answer you read off the table isn't itself the sentinel.

---

## Try it

1. *Climbing Stairs:* ways to climb `n` stairs taking 1 or 2 steps. Why is this Fibonacci in disguise? Define `dp[i]`.
2. *House Robber:* max money robbing non-adjacent houses. What's the state and the two choices at each house?
3. *Longest Common Subsequence:* this is the 2-D "two sequences" shape — what does `dp[i][j]` mean, and what are the match / no-match cases?
4. *Coin Change (count the ways):* adapt the table to count *how many* ways there are to make `amount`, rather than the fewest coins. What replaces the `min` in the recurrence, and what's the new base case?
5. For a problem of your choice, write out all five recipe steps (state, recurrence, base, order, answer) before coding.

*Write your answers in [dsa-chapter-14-tryit.md](code/dsa-chapter-14-tryit.md).*

---

## The bumper sticker

> *DP is brute-force recursion that stopped re-solving the same subproblem. Spot the overlap in the recursion tree, define what a subproblem *means*, write the recurrence — then cache it (top-down) or fill a table (bottom-up). Exponential becomes polynomial.*

Next: the final chapter — the interview ritual that turns all fourteen chapters into a calm, repeatable process under pressure.

---

<div align="right">

[Chapter 15 →](dsa-chapter-15.md)

</div>
