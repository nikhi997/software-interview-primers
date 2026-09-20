# Chapter 13: Trying everything, cleanly — recursion and backtracking

*[← Chapter 12](dsa-chapter-12.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

Some problems have no clever shortcut: you genuinely must *explore all the possibilities* — every subset, every permutation, every way to place the queens. The skill isn't avoiding the exploration; it's exploring it **systematically**, without duplicating work or tangling yourself in loops. That skill is **backtracking**: build a candidate one choice at a time, and the moment a choice can't lead anywhere, **undo it and try the next.**

First, though, recursion itself — because backtracking is just recursion with an undo step.

---

## Recursion: trust the smaller answer

> 💡 **Concept notes — the two parts of every recursion**
> A recursive function has exactly two responsibilities: (1) a **base case** — the smallest input it answers directly, without recursing (this stops the recursion); and (2) a **recursive case** — it reduces the problem to a *smaller* version, calls itself, and combines the result. The leap of faith: *assume the recursive call already works for the smaller input*, and just figure out how to use its answer. Don't trace the whole call tree in your head — define the contract ("`f(n)` returns ___") and trust it. Every recursion that lacks a reachable base case loops until the stack overflows.

```python
def factorial(n):
    if n <= 1:              # base case
        return 1
    return n * factorial(n - 1)    # trust factorial(n-1); just multiply by n
```

This is the same "trust the recursion" mindset from tree problems (Chapter 8) — trees are just recursion with two branches.

---

## Backtracking: the choose / explore / un-choose template

Backtracking explores a tree of decisions. At each step you **choose** an option, **explore** the consequences recursively, then **un-choose** (undo) so you're clean to try the next option. That undo is the whole trick — it lets one data structure serve the entire search.

The canonical example: *generate all subsets of `[1,2,3]`.*

```python
def subsets(nums):
    result = []
    path = []                          # the candidate we're building

    def backtrack(start):
        result.append(path[:])         # every node is a valid subset; record a COPY
        for index in range(start, len(nums)):
            path.append(nums[index])   # CHOOSE nums[index]
            backtrack(index + 1)       # EXPLORE with it included
            path.pop()                 # UN-CHOOSE (backtrack)

    backtrack(0)
    return result
```

Read the loop body as a ritual: **choose** (`append`), **explore** (recurse), **un-choose** (`pop`). The `path[:]` copy matters — `path` keeps mutating, so you must snapshot it when recording. This same three-line skeleton generates permutations, combinations, partitions — anything "list all the ways."

> 💡 **Concept notes — why backtracking beats naive brute force**
> Naive brute force might build every candidate from scratch (re-creating shared prefixes over and over) or generate invalid ones and filter at the end. Backtracking **shares the partial work** (one `path` mutated in place) and can **prune early** — abandon a branch the instant it's doomed, before wasting time deeper. The choose/un-choose pair is what makes sharing one structure safe across millions of branches.

---

## Pruning: the difference between feasible and hopeless

The exponential cost is real — `n` items have `2ⁿ` subsets and `n!` permutations. Backtracking stays tractable on real inputs by **pruning**: cutting a branch as soon as it can't possibly succeed. The N-Queens problem is the classic — don't place a queen where it's already attacked.

First, the intuitive version. Place queens row by row; before placing one at `(row, col)`, ask the plain question in your head — *does it clash with any queen already on the board?* — by walking the queens placed so far:

```python
def solve_n_queens_scan(n):
    result = []
    board = []                                 # board[row] = column of that row's queen

    def render():                              # turn column positions into ".Q.." rows
        rows = []
        for col in board:
            rows.append("." * col + "Q" + "." * (n - col - 1))   # place Q at that column
        return rows

    def is_safe(row, col):
        for earlier_row in range(row):         # check every queen already placed
            earlier_col = board[earlier_row]
            if earlier_col == col:
                return False                   # same column
            if row - earlier_row == abs(col - earlier_col):
                return False                   # same diagonal: row gap equals column gap
        return True

    def backtrack(row):
        if row == n:                           # base case: all rows filled
            result.append(render())
            return
        for col in range(n):
            if not is_safe(row, col):
                continue                       # PRUNE: this square is attacked
            board.append(col)                  # CHOOSE
            backtrack(row + 1)                 # EXPLORE
            board.pop()                        # UN-CHOOSE
    backtrack(0)
    return result
```

That reads exactly like the rule in your head. Its cost: `is_safe` scans up to `row` earlier queens, so each safety check is `O(n)` — and we recompute the same conflicts over and over as the recursion goes deeper.

Buy that back with bookkeeping. A queen at `(row, col)` occupies one column, one `\` diagonal (constant `row - col`), and one `/` diagonal (constant `row + col`). Keep those three occupied-line sets and the safety check collapses to `O(1)`:

```python
def solve_n_queens(n):
    result = []
    columns, diagonals, anti_diagonals = set(), set(), set()   # occupied lines
    board = []                                 # board[row] = column of that row's queen

    def render():                              # turn column positions into ".Q.." rows
        rows = []
        for col in board:
            rows.append("." * col + "Q" + "." * (n - col - 1))   # place Q at that column
        return rows

    def backtrack(row):
        if row == n:                           # base case: all rows filled
            result.append(render())
            return
        for col in range(n):
            if col in columns or (row - col) in diagonals or (row + col) in anti_diagonals:
                continue                       # PRUNE: this square is attacked
            columns.add(col); diagonals.add(row - col); anti_diagonals.add(row + col)
            board.append(col)                  # CHOOSE
            backtrack(row + 1)                 # EXPLORE
            board.pop()                        # UN-CHOOSE
            columns.remove(col); diagonals.remove(row - col); anti_diagonals.remove(row + col)
    backtrack(0)
    return result
```

The `continue` is still the prune — we never even *enter* a branch that places a queen under attack — but the conflict test is now three set-membership checks instead of a scan of earlier rows. Each "diagonal" is identified by `row - col` (same `\` diagonal) and `row + col` (same `/` diagonal) — a tidy `O(1)` conflict check. Same search tree, cheaper gate at every node.

> 💡 **Concept notes — recognizing the need to prune**
> If a backtracking solution is "correct but too slow," the fix is almost always a **stronger prune**: detect doomed branches *earlier*. Track just enough state (here, occupied columns/diagonals) to reject a choice in `O(1)` before recursing. Good pruning is what separates a solution that runs in milliseconds from one that times out — the asymptotic worst case stays exponential, but real inputs finish fast because most of the tree is never explored.

---

## Recognizing a backtracking problem

- **"Generate all ...," "find all ...," "list every ..."** — subsets, permutations, combinations, partitions.
- **"Does there exist a way to ..."** where you must try arrangements — N-Queens, Sudoku, word search on a grid.
- The answer is a **combinatorial structure** and `n` is **small** (the exponential blowup is acceptable because inputs are tiny — often `n ≤ 20`).
- You can describe the solution as **a sequence of choices**, each opening more choices.

> 💡 **Concept notes — backtracking vs dynamic programming**
> Both explore many possibilities, but: **backtracking** *enumerates* the actual solutions (you need to see every subset/arrangement), and the subproblems usually don't overlap. **Dynamic programming** (Chapter 14) only wants an *optimum or a count*, and the subproblems **overlap heavily** so you cache them. Tell them apart by the ask: "list/produce all the ways" → backtracking; "the best/most/fewest/number of ways" → suspect DP. If you're backtracking but only returning a count or a max, and you notice repeated subproblems — that's the signal to switch to DP.

> 💡 **Concept notes — edge cases to surface**
> Backtracking's edge cases are small inputs and the base case: an **empty input** (subsets of `[]` is `[[]]` — one empty subset, not nothing), **`n == 0`** in N-Queens (one trivial arrangement), an arrangement that's **impossible** (`solve_n_queens(2)` and `(3)` return `[]`), and **duplicate elements** in the input, which force an explicit skip if the output must be unique. In Review, run the smallest input and confirm you emit the empty solution, not an empty list.

---

## Try it

1. *Permutations:* generate all orderings of a list. How does the choose/explore/un-choose template change from `subsets` (no `start` index — why)?
2. *Combination Sum:* all combinations summing to a target (numbers reusable). Where's the prune (stop when the running sum exceeds the target)?
3. *Word Search:* does a word exist in a grid via adjacent cells? Combine backtracking with the grid DFS of Chapter 11 — what do you un-choose?
4. *Generate Parentheses:* all valid combinations of `n` pairs. What two counters prune invalid branches early?
5. State the choose / explore / un-choose lines for the `subsets` problem and explain why the `path[:]` copy is necessary.

*Write your answers in [dsa-chapter-13-tryit.md](code/dsa-chapter-13-tryit.md).*

---

## The bumper sticker

> *When you must try every possibility, backtrack: choose, explore, un-choose. One mutated structure serves the whole search, and early pruning — abandoning doomed branches before recursing — keeps the exponential tree tractable on real inputs.*

Next: the other side of "try everything" — when subproblems overlap, stop re-solving them. Dynamic programming.

---

<div align="right">

[Chapter 14 →](dsa-chapter-14.md)

</div>
