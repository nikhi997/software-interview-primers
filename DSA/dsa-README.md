# DSA Primer — Reading order and study contract

A 15-chapter primer on Data Structures & Algorithms for coding interviews, written in the conversational style of Aditya Bhargava's *Grokking Algorithms* and Alex Xu's *System Design Interview*. Built around a single principle: *feel the brute force before reaching for the pattern.*

This is the companion to the LLD and HLD primers. LLD asks "does your code bend when requirements change?" HLD asks "does your system bend when traffic lands?" DSA asks a sharper, smaller question: *given a problem, can you find the trick that turns the slow obvious solution into a fast one?*

## The one idea

Every DSA course throws a catalog of algorithms at you — sliding window, binary search, dynamic programming — as if you're supposed to recognize them on sight. You memorize the templates, then freeze in the interview because the problem doesn't announce which template it wants.

We're not doing that.

We start every topic with the **brute force**: the slow, obvious, two-nested-loops solution you'd write if you knew nothing. It *works.* Then we ask one question: *what is it doing that's wasteful?* The pattern is whatever removes that specific waste. Sliding window removes recomputed overlap. Hashing removes repeated lookups. Binary search removes half the search space each step. You won't memorize templates — you'll *derive* them from the waste they eliminate, which is exactly what lets you recognize them on an unfamiliar problem.

## How DSA interviews are actually scored

Most candidates think the interviewer wants the optimal answer instantly. They don't. They're checking whether you can:

1. **Find a working solution first** — brute force is a valid start; a working slow answer beats a broken clever one.
2. **Spot the waste** — articulate *why* it's slow (the repeated work, the Big-O).
3. **Improve it** — apply the pattern that removes the waste, and state the new complexity.
4. **Communicate while coding** — think out loud, name your approach, handle edge cases.
5. **Verify** — trace an example, check the boundaries.

This book builds those five, in that order. The pattern is almost a side effect of asking "what's wasteful here?"

## Reading order

Read in sequence. Each chapter assumes the previous ones.

**Part 1 — Foundations & the first patterns**
- Chapter 1: How slow is slow? *(Big-O, the brute-force habit)*
- Chapter 2: Trading space for time *(hashing / hash maps)*
- Chapter 3: Walking from both ends *(two pointers)*
- Chapter 4: The window that slides instead of restarting *(sliding window)*
- Chapter 5: Throwing away half the answers *(binary search + search on answer)*

**Part 2 — Linear structures, trees, heaps**
- Chapter 6: The structure that remembers the last thing *(stack + monotonic stack)*
- Chapter 7: Two pointers at different speeds *(linked lists, fast/slow)*
- Chapter 8: Branching data *(trees + traversals)*
- Chapter 9: Ordered branching and prefixes *(BST + trie)*
- Chapter 10: Always knowing the best so far *(heap / priority queue)*

**Part 3 — Graphs, recursion, DP, and the ritual**
- Chapter 11: Everything is a graph *(BFS + DFS)*
- Chapter 12: Weighted, grouped, ordered graphs *(Dijkstra, Union-Find, topological sort)*
- Chapter 13: Try everything, undo, try again *(recursion + backtracking)*
- Chapter 14: Remembering subproblems *(dynamic programming)*
- Chapter 15: The interview ritual *(UMPIRE + worked problems)*

**Appendix:** Complexity cheat sheet, the pattern→signal table, the curated problem list (what to solve and in what order), common pitfalls.

## Runnable code

A few chapters ship verified, runnable snippets in [code/](code) — run them with `python3`:
- [code/sliding_window.py](code/sliding_window.py) — Chapter 4 (fixed + variable windows)
- [code/binary_search_answer.py](code/binary_search_answer.py) — Chapter 5 (binary search on the answer)
- [code/dynamic_programming.py](code/dynamic_programming.py) — Chapter 14 (brute force vs memo vs tabulation, coin change)

Type the *other* chapters' code blocks in yourself — the typing is part of the learning.

## Prerequisites

- Comfort writing basic Python: variables, loops, functions, lists, dicts.
- No prior algorithms knowledge. We build Big-O and every structure from scratch.

## Study contract — do not skip

DSA is the one track where **solving beats reading.** Each chapter is **3 sessions, NOT one sitting:**

**Session 1 (45–60 min):** Read the chapter once. Type every code block into a Python file and run it — don't just read it. Do the inline "try it" prompts. Don't take notes.

**Session 2 (45–60 min, next day):** Solve the **2–3 listed problems** for that chapter's pattern (links in the appendix), from scratch. When stuck for more than ~25 minutes, read the editorial, understand it, close it, and re-solve from memory. The struggle is the learning.

**Session 3 (30 min, day after):** Re-solve one problem you found hard, cold. Then explain the pattern to yourself in 4–5 sentences: what brute force looks like, what waste it has, what the pattern removes, how to recognize it next time.

≈2.5 hours per chapter over 3 days, **plus ongoing problem reps.** DSA fluency comes from *volume* — these 15 chapters teach you the patterns; the appendix's problem list is where you grind them in. Budget 2–3 months of steady solving alongside and after the reading.

## Active companions

Use these as practice tools, not replacements for reps:

- [Waste Map](dsa-waste-map.md) — use it after each chapter, and after any failed problem, to diagnose the exact wasted operation, the tempting patch, and the invariant that makes the final optimization valid.
- [Mixed Cold Drills](dsa-mixed-cold-drills.md) — start from Chapter 5 onward, then use heavily after Chapter 15 for 30–35 minute unlabelled packets under interview pressure.

The chapters teach, the appendix looks up, the waste map diagnoses, and the cold drills retrieve under time pressure. None of these replaces solving the appendix problems from scratch.

## Checkpoints

Every 5 chapters, stop and assess:

- **After Ch5:** Given an array problem, can you state the brute force, its Big-O, and decide whether hashing / two pointers / sliding window / binary search removes the waste?
- **After Ch10:** Can you pick the right *structure* (hash map, stack, heap, tree) for an unfamiliar problem and justify it?
- **After Ch15:** Can you run the full UMPIRE ritual on a medium problem you've never seen in ~35 minutes, talking the whole time?

If a checkpoint fails, **stop and redo** the prior chapters and their problems. Don't proceed.

## The bumper sticker

> *A pattern is just the thing that deletes the specific waste in your brute force. Find the waste, and the pattern names itself.*

---

<div align="right">

[Chapter 1 →](dsa-chapter-1.md)

</div>
