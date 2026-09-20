# DSA Waste Map: the transformation ledger

*[← Chapter 15](dsa-chapter-15.md) · [Contents](dsa-README.md)*

This is not a second appendix table. The appendix helps you look up signals after you already know the catalog. This file makes you do the interview move: start with an unlabelled fragment, name the waste, try the tempting patch, then decide whether the structural optimization is actually valid.

The role split is four-way:

- **Chapters teach** the pattern by making you feel one pain at a time.
- **The appendix looks up** complexity, signals, and practice lists.
- **This waste map diagnoses** the gap between brute force and the right optimization.
- **The cold drills retrieve** the whole ritual under time pressure.

Use one entry after each matching chapter, and again after every failed problem. Cover the headings after **Problem fragment** and force yourself to fill the ledger before reading the answer.

One warning before the ledger: **one waste does not always imply one pattern.** A nested loop over pairs may become hashing, two pointers, sorting, or even DP depending on sortedness, space limits, and output requirements. Chapter 3's tradeoff is the model: unsorted + indices points one way; sorted + `O(1)` space points another.

---

## 1. A fixed-size score window

**Problem fragment.** You receive `n` daily scores and a number `k`. Return the largest total from exactly `k` consecutive days. `n` may be 100,000; `k` may be large; the scores can be negative.

**Naive approach and cost.** For each start position, add the next `k` scores from scratch. There are about `n` starts and each sum costs `k`, so this is `O(nk)` time and `O(1)` extra space.

**Exact wasted operation.** Consecutive windows share `k - 1` scores, but the naive sum re-adds all shared scores every time.

**Tempting patch.** Build a prefix-sum array where `prefix[i]` is the sum before index `i`. Then each window sum is `prefix[start + k] - prefix[start]`.

- What it fixes: each window query becomes `O(1)`, so total time is `O(n)`.
- What remains: the prefix array costs `O(n)` space even though you only need the previous window while scanning left to right.

**Structural optimization.** Replace the prefix table with a rolling sum: compute the first window once, then add the entering score and subtract the leaving score on each slide.

- Invariant: before comparing at position `start`, `window_sum` equals `sum(scores[start:start + k])`.
- Complexity: `O(n)` time, `O(1)` extra space.
- Chapter check: this is the fixed-window move in [Chapter 4](dsa-chapter-4.md) and [code/sliding_window.py](code/sliding_window.py).

**Counterexample — when this optimization is invalid.** If the query is not a single left-to-right pass, for example "answer 100,000 arbitrary range-sum queries after the array is built," the rolling sum no longer helps because queries jump around. Prefix sums are the right patch there: `O(n)` preprocessing, `O(1)` per query.

**Transfer prompt.** What changes if the chunk may be **at most** `k` days instead of exactly `k`, and all numbers can be negative? What state would you track, and why is a simple fixed slide no longer enough?

---

## 2. Three values that cancel out

**Problem fragment.** Return every unique triple of values whose sum is zero. Input length may be a few thousand. Values may repeat. Output triples should not repeat, but order inside the output does not matter.

**Naive approach and cost.** Try every `(first, second, third)` index triple: `O(n^3)` time. It also emits duplicate value triples when repeated numbers appear.

**Exact wasted operation.** After fixing one value, the inner two loops are still blindly searching for a pair. On top of that, repeated equal values generate the same output again through different indices.

**Tempting patch.** Sort the array, fix one anchor, then walk the remaining suffix with two pointers. This deletes one loop and gives `O(n^2)` time, but it still generates duplicates. The blunt patch after that is a `set` of triples.

- What it fixes: the set makes the output unique and keeps the `O(n^2)` time shape.
- What remains: you still generate duplicates and pay extra space to swallow them after the fact.

**Structural optimization.** Keep the sorted two-pointer search, but skip duplicate anchors and duplicate pointer values during generation.

- Invariant: for each distinct anchor value, the two-pointer walk emits each distinct suffix-pair value combination at most once.
- Complexity: sorting costs `O(n log n)`, the nested anchor/walk costs `O(n^2)`, and extra space is `O(1)` beyond the output.
- Chapter check: compare the rungs in [Chapter 3](dsa-chapter-3.md) and [code/ch3.py](code/ch3.py); do not memorize the final shape without the duplicate-output pain.

**Counterexample — when this optimization is invalid.** If the problem asks for **original indices** of every triple, sorting values without carrying indices loses information. If the problem asks for **all index triples**, then skipping equal values is wrong because two equal values at different positions may represent different required outputs.

**Transfer prompt.** Suppose the input is unsorted, you need one pair of **indices**, and memory is allowed. Which earlier chapter now beats sorting, and what exact requirement changed the decision?

---

## 3. A recursive number that keeps asking the same question

**Problem fragment.** Compute the `n`th value where each value depends on the previous two. `n` may be 50,000. You only need the final number, not the whole sequence.

**Naive approach and cost.** Write the definition as recursion: `value(n) = value(n - 1) + value(n - 2)`. The call tree repeats the same subproblems, so the time is exponential, `O(2^n)` for Fibonacci-style recurrence, and recursion stack space is `O(n)`.

**Exact wasted operation.** The same subproblem, such as `value(30)`, is recomputed through many branches even though its answer never changes.

**Tempting patch.** Memoize the recursion. Cache `value(i)` the first time it is solved and return it instantly after that.

- What it fixes: each `i` from `0` to `n` is solved once, so time drops to `O(n)`.
- What remains: the cache costs `O(n)` space, and the recursion stack can still be a practical problem for very large `n`.

**Structural optimization.** Tabulate bottom-up, then notice the recurrence only needs the previous two values. Roll two variables forward.

- Invariant: before each step, `previous` and `current` hold the two most recent completed values.
- Complexity: `O(n)` time, `O(1)` extra space.
- Chapter check: this is the full DP ladder in [Chapter 14](dsa-chapter-14.md) and [code/dynamic_programming.py](code/dynamic_programming.py): exponential recursion → memoization → tabulation → rolling space.

**Counterexample — when this optimization is invalid.** If the task asks you to return the **entire table**, reconstruct a path, or answer many later queries for arbitrary `i`, rolling space throws away information you still need. Keep the table.

**Transfer prompt.** Coin change asks for the fewest coins for every smaller amount on the way to the target. Which parts of the Fibonacci ladder transfer, and why does the final `O(1)` space trick usually not transfer directly?

---

## 4. The largest few, not the sorted many

**Problem fragment.** From `n` readings, return the `k` largest values. `n` may be in the millions; `k` may be 20. The output does not need to be sorted.

**Naive approach and cost.** Sort everything and take the last `k`: `O(n log n)` time, usually `O(n)` or implementation-dependent extra space.

**Exact wasted operation.** Sorting decides the order of values you will discard. You only need to know which `k` survive.

**Tempting patch.** Put all `n` values into a heap and pop the extreme `k` times.

- What it fixes: it uses the right structure for repeated extremes.
- What remains: heapifying all `n` values costs `O(n)` and popping `k` times costs `O(k log n)`; if you push one by one, building the heap is `O(n log n)`. Either way, space is still `O(n)` even when `k` is tiny.

**Structural optimization.** Keep a min-heap capped at size `k`. Every new value enters; if the heap grows past `k`, evict the smallest kept value.

- Invariant: after processing each reading, the heap contains exactly the largest `min(k, processed_count)` values seen so far, unordered.
- Complexity: `O(n log k)` time, `O(k)` space.
- Chapter check: this is the size-capped heap move in [Chapter 10](dsa-chapter-10.md).

**Counterexample — when this optimization is invalid.** If `k` is close to `n` and you need the whole result sorted, a full sort may be simpler and just as good. If values arrive as a stream and you must answer after each insert, the same capped heap can work for top-k, but not for median; median needs two balanced heaps.

**Transfer prompt.** Change the problem to "report the median after every reading." What invariant replaces "heap contains the top k," and why is one capped heap not enough?

---

## 5. The smallest setting that works

**Problem fragment.** You can choose an integer setting `x`. A simulator can tell you whether setting `x` finishes all work by the deadline. Larger `x` never hurts. Find the smallest working setting. The setting range may be up to one billion.

**Naive approach and cost.** Test `x = 1, 2, 3, ...` until the simulator returns true. If each simulation scans `n` jobs and the answer range is `R`, this is `O(nR)`.

**Exact wasted operation.** Once some setting works, every larger setting also works. Linear testing ignores that monotonic boundary and probes candidates one at a time.

**Tempting patch.** Write a clean feasibility predicate first: `can_finish(x)`. This is a real improvement because it separates correctness from search.

- What it fixes: you can reason about the yes/no boundary explicitly.
- What remains: if you still call it for every `x`, the search is linear in the answer range.

**Structural optimization.** Binary-search the first true value in the ordered answer space.

- Invariant: the answer always lies inside `[low, high]`; when `can_finish(mid)` is true, `mid` remains a candidate, so move `high = mid`; when false, move `low = mid + 1`.
- Complexity: `O(n log R)`, where `R` is the numeric range.
- Chapter check: this is [Chapter 5](dsa-chapter-5.md)'s binary search on the answer, demonstrated in [code/binary_search_answer.py](code/binary_search_answer.py).

**Counterexample — when this optimization is invalid.** If feasibility is not monotonic — for example, `x = 4` works, `x = 5` fails, and `x = 6` works because of a parity rule — binary search can discard the true answer. You need a different search or a new predicate.

**Transfer prompt.** How would you set `low` and `high` for "minimum ship capacity to deliver packages in `D` days"? What does `can_finish(capacity)` count?

---

## 6. The next larger thing to the right

**Problem fragment.** For each day's temperature, return how many days until a warmer temperature. If no warmer day exists, return `0`. `n` may be 100,000.

**Naive approach and cost.** For each day, scan the suffix to the right until you find a warmer day. Worst case is `O(n^2)` time and `O(1)` extra space.

**Exact wasted operation.** Descending stretches are re-scanned for many earlier days. A warmer day that resolves several waiting days is rediscovered separately by each scan.

**Tempting patch.** Cache answers for days you've already solved and try to jump using them.

- What it fixes: some suffix scans get shorter when a solved day gives a useful jump.
- What remains: the cache is hard to make correct for all shapes, and "next greater for day B" does not automatically tell you "next greater for day A" when `A` has a different temperature. You can still degrade or skip valid candidates.

**Structural optimization.** Keep a decreasing stack of unresolved day indices. When a warmer temperature arrives, pop every colder waiting day and record the gap.

- Invariant: the stack holds indices whose answer is not known yet, and their temperatures are decreasing from bottom to top.
- Complexity: `O(n)` time and `O(n)` space; each index is pushed once and popped once.
- Chapter check: this is the monotonic-stack invariant from [Chapter 6](dsa-chapter-6.md).

**Counterexample — when this optimization is invalid.** If the question changes to "next day with temperature exactly 70" or "next warmer day within at most three days," the monotonic pop rule no longer directly matches the predicate. The stack solves domination by greater/smaller values, not arbitrary future filters.

**Transfer prompt.** Change "warmer" to "next smaller price to the left." Which direction do you traverse, and should the stack be increasing or decreasing?

---

## 7. Reaching a place in a maze

**Problem fragment.** A grid has open cells and walls. From a start cell, find the fewest moves to a target cell using up/down/left/right moves. Every move costs one.

**Naive approach and cost.** Enumerate every possible walk and keep the shortest. In a grid with cycles, there are infinitely many walks unless you artificially cap length; even simple paths can be exponential.

**Exact wasted operation.** Different walks revisit the same cells and replay the same prefixes. Without memory, cycles send you around forever.

**Tempting patch.** Use DFS with a `visited` set to stop infinite loops.

- What it fixes: every reachable cell is explored at most once, so traversal becomes `O(rows * cols)`.
- What remains: DFS does not visit cells by distance. The first time DFS reaches the target may be a long route, not the shortest route.

**Structural optimization.** Use BFS with a queue of `(cell, distance)` and mark cells visited when enqueuing.

- Invariant: cells leave the queue in nondecreasing distance from the start; the first target pop is shortest.
- Complexity: `O(rows * cols)` time and space.
- Chapter check: this is [Chapter 11](dsa-chapter-11.md)'s unweighted shortest-path guarantee.

**Counterexample — when this optimization is invalid.** If moves have different costs — mud costs 5, road costs 1 — BFS's first arrival is no longer cheapest. Use Dijkstra from [Chapter 12](dsa-chapter-12.md) for non-negative weights.

**Transfer prompt.** If several starting cells are already active at minute 0, how do you initialize the BFS queue so the distance invariant still holds?

---

## 8. Groups that merge over time

**Problem fragment.** You receive a stream of undirected connections between numbered accounts. After each connection, you may be asked whether two accounts are already in the same group.

**Naive approach and cost.** After each new edge, run BFS or DFS from one account to see if it reaches the other. One query costs `O(V + E)`; many queries repeat almost the same traversal.

**Exact wasted operation.** Connectivity information is rebuilt from scratch even though each new edge only merges two existing groups.

**Tempting patch.** Maintain a visited component label by running one full graph traversal after batches of edges.

- What it fixes: repeated queries inside the same batch can read labels quickly.
- What remains: every new edge that merges components can invalidate many labels, so relabeling large components is still expensive.

**Structural optimization.** Use union-find. `find(node)` returns the group's representative; `union(a, b)` merges representatives, with path compression and union by rank keeping trees shallow.

- Invariant: two accounts are connected exactly when their roots are equal.
- Complexity: effectively `O(1)` per `find` or `union` for interview purposes, with `O(V)` space.
- Chapter check: this is the dynamic-connectivity tool in [Chapter 12](dsa-chapter-12.md).

**Counterexample — when this optimization is invalid.** Union-find handles edges being added. If edges can be deleted and queries continue, old unions cannot be undone cheaply. You need a different dynamic-graph strategy or periodic rebuilds.

**Transfer prompt.** If the graph is fixed and you need the actual path between two nodes, not just whether they share a component, why might BFS/DFS be the better tool again?

---

## 9. Work that must happen before other work

**Problem fragment.** There are `num_tasks` tasks and pairs `(before, after)`. Return one valid order that satisfies every pair, or report impossible.

**Naive approach and cost.** Repeatedly scan the whole task list to find a task whose prerequisites are all already done. If you check prerequisites by scanning edges each time, this drifts toward `O(VE)` or worse.

**Exact wasted operation.** You recompute "how many prerequisites remain?" from scratch after every choice.

**Tempting patch.** Sort tasks by their original number of prerequisites.

- What it fixes: it feels like tasks with fewer blockers should go earlier.
- What remains: prerequisite counts change as tasks complete. A task that starts blocked may become ready later, and a static sort can put it too early or miss cycles.

**Structural optimization.** Track in-degrees. Start a queue with tasks at in-degree `0`; when you take a task, decrement its neighbors and enqueue any that just became ready.

- Invariant: the queue contains exactly the tasks whose remaining prerequisites are zero.
- Complexity: `O(V + E)` time and space.
- Chapter check: this is Kahn's topological sort from [Chapter 12](dsa-chapter-12.md).

**Counterexample — when this optimization is invalid.** If dependencies can change while you are producing the order, the in-degree invariant can become stale. Also, if the graph is undirected, "before" and "after" have no meaning; topological order is a directed-acyclic-graph idea.

**Transfer prompt.** How does the algorithm prove a cycle exists, and what should you return when only seven of ten tasks make it into the order?

---

## How to use this ledger after a failed problem

Write one sentence for each line:

1. The brute force I stated was...
2. Its exact wasted operation was...
3. My tempting patch was...
4. The patch still wasted or broke...
5. The invariant I should have used was...
6. The optimization would be invalid if...
7. The changed constraint that would pick a different tool is...

If you cannot fill line 2, reread the chapter. If you cannot fill line 6, you may be memorizing the pattern instead of understanding its boundary.

---

<div align="right">

[Mixed cold drills →](dsa-mixed-cold-drills.md)

</div>
