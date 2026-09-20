# Appendix: cheat sheets, pattern signals, and a curated problem list

*[← Chapter 15](dsa-chapter-15.md) · [Contents](dsa-README.md)*

Everything in the fifteen chapters, compressed into reference tables you can scan the night before an interview. Use this *after* you've read the chapters — these tables are reminders, not teachers.

For active practice, pair this lookup sheet with the [Waste Map](dsa-waste-map.md) when you miss a pattern and the [Mixed Cold Drills](dsa-mixed-cold-drills.md) when you need unlabelled timed retrieval.

---

## A. Big-O complexity cheat sheet

**The complexity ladder** (best to worst), with the rough largest `n` that finishes in ~1 second:

| Complexity | Name | Largest workable `n` | Typical source |
|---|---|---|---|
| $O(1)$ | constant | any | hash lookup, array index, heap peek |
| $O(\log n)$ | logarithmic | astronomically large | binary search, balanced-BST op, heap push/pop |
| $O(n)$ | linear | ~100,000,000 | single scan, BFS/DFS over `V+E` |
| $O(n \log n)$ | linearithmic | ~5,000,000 | sorting, heap-based top-k |
| $O(n^2)$ | quadratic | ~10,000 | nested loops, naive pair checks |
| $O(2^n)$ | exponential | ~22 | subsets, naive recursion |
| $O(n!)$ | factorial | ~11 | permutations, brute-force TSP |

> **Reading the constraints:** the input size in the problem statement *tells you the target complexity.* `n ≤ 10⁵` → you need `O(n)` or `O(n log n)`. `n ≤ 5000` → `O(n²)` is fine. `n ≤ 20` → exponential (backtracking/bitmask DP) is expected. Use this backwards: the constraint hints at the pattern.

**Common data-structure operation costs:**

| Structure | Access | Search | Insert | Delete | Notes |
|---|---|---|---|---|---|
| Array / list | $O(1)$ | $O(n)$ | $O(n)$ | $O(n)$ | `O(1)` append at the end |
| Hash map / set | — | $O(1)$* | $O(1)$* | $O(1)$* | *amortized; worst case `O(n)` |
| Stack / queue | — | — | $O(1)$ | $O(1)$ | LIFO / FIFO |
| Linked list | $O(n)$ | $O(n)$ | $O(1)$† | $O(1)$† | †given a pointer to the spot |
| Binary heap | $O(1)$ peek | — | $O(\log n)$ | $O(\log n)$ | extreme element only |
| Balanced BST | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | ordered queries |
| Trie | — | $O(L)$ | $O(L)$ | $O(L)$ | `L` = string length |

---

## B. Pattern → signal table

The heart of the book. When you read a problem, scan for these signals and match.

| If the problem says / has... | Reach for | Chapter |
|---|---|---|
| "Have I seen this?", counts, frequencies, pairs by value, dedup | **Hash map / set** | 2 |
| **Sorted** array + find a pair/triple, `O(1)` space, palindrome, in-place | **Two pointers** | 3 |
| **Contiguous** subarray/substring + longest/shortest/max-sum | **Sliding window** | 4 |
| **Sorted / monotonic** + "first/last", "min value such that", "minimize the max" | **Binary search** (incl. on the answer) | 5 |
| "Next greater/smaller", nearest larger, matching brackets, undo | **Stack / monotonic stack** | 6 |
| Linked list: middle, cycle, nth-from-end, reverse, palindrome | **Slow/fast pointers, dummy head** | 7 |
| Tree: depth, path, balanced, symmetric / level-by-level | **DFS recursion / BFS** | 8 |
| "In sorted order", kth smallest, prefix/autocomplete | **BST (inorder) / trie** | 9 |
| "Top k", "k closest", "merge k", streaming median, priority | **Heap** | 10 |
| Networks, grids, mazes, "shortest steps", "connected", "islands" | **BFS / DFS + visited** | 11 |
| Weighted shortest path / "order, prerequisites" / "same group?" | **Dijkstra / topo sort / union-find** | 12 |
| "Generate all", "find all ways", permutations, subsets, N-Queens | **Backtracking** | 13 |
| "Best/most/fewest/number of ways" + overlapping subproblems | **Dynamic programming** | 14 |

---

## C. The brute-force-to-pattern map

The book's one idea, in one table. *Find the waste in the brute force, and the pattern names itself.*

| Waste in the brute force | Pattern that deletes it |
|---|---|
| Re-scanning to check membership or count | Hash map |
| Nested loop over sorted data | Two pointers |
| Recomputing overlapping subarrays | Sliding window |
| Linearly scanning sorted/monotonic data | Binary search |
| Re-finding the next greater/smaller element | Monotonic stack |
| Re-walking a list to find middle/cycle | Slow/fast pointers |
| Re-sorting to grab the extreme element | Heap |
| Re-visiting already-explored nodes | BFS/DFS + visited set |
| Rebuilding shared partial candidates | Backtracking |
| Re-solving identical subproblems | Dynamic programming |

---

## D. Curated problem list (ordered by chapter)

A Blind-75 / NeetCode-style set, grouped so you practice **one pattern at a time** until its signal is instant. Roughly easy → hard within each group. Solve brute-force-first, then rebuild from memory.

**Ch 2 — Hashing**
- Two Sum · Contains Duplicate · Valid Anagram · Group Anagrams · Top K Frequent Elements · Longest Consecutive Sequence

**Ch 3 — Two pointers**
- Valid Palindrome · Two Sum II (sorted) · 3Sum · Container With Most Water · Trapping Rain Water (hard)

**Ch 4 — Sliding window**
- Best Time to Buy/Sell Stock · Longest Substring Without Repeating Characters · Longest Repeating Character Replacement · Minimum Window Substring (hard) · Permutation in String

**Ch 5 — Binary search**
- Binary Search · Search Insert Position · Find Minimum in Rotated Sorted Array · Search in Rotated Sorted Array · Koko Eating Bananas · Median of Two Sorted Arrays (hard)

**Ch 6 — Stack**
- Valid Parentheses · Min Stack · Daily Temperatures · Evaluate Reverse Polish Notation · Largest Rectangle in Histogram (hard)

**Ch 7 — Linked list**
- Reverse Linked List · Merge Two Sorted Lists · Linked List Cycle · Remove Nth Node From End · Reorder List · Reverse Nodes in k-Group (hard)

**Ch 8 — Trees**
- Invert Binary Tree · Maximum Depth · Diameter of Binary Tree · Balanced Binary Tree · Same Tree · Level Order Traversal · Right Side View

**Ch 9 — BST & trie**
- Validate BST · Kth Smallest in a BST · Lowest Common Ancestor of a BST · Implement Trie · Add and Search Word (wildcard) · Word Search II (hard)

**Ch 10 — Heap**
- Kth Largest Element · K Closest Points to Origin · Task Scheduler · Find Median from Data Stream (hard) · Merge K Sorted Lists (hard)

**Ch 11 — Graph BFS/DFS**
- Number of Islands · Clone Graph · Max Area of Island · Pacific Atlantic Water Flow · Rotting Oranges · Word Ladder (hard)

**Ch 12 — Weighted / ordering graphs**
- Course Schedule · Course Schedule II · Number of Connected Components · Redundant Connection · Network Delay Time · Cheapest Flights Within K Stops

**Ch 13 — Backtracking**
- Subsets · Permutations · Combination Sum · Word Search · Generate Parentheses · Palindrome Partitioning · N-Queens (hard)

**Ch 14 — Dynamic programming**
- Climbing Stairs · House Robber · Coin Change · Longest Increasing Subsequence · Longest Common Subsequence · Word Break · Unique Paths · Edit Distance (hard)

**Ch 15 — Mixed / ritual practice**
- Do a random mix from all the above on a timer, running full UMPIRE each time.

---

## E. Common pitfalls checklist

Scan this before every problem and during Review:

- **Silently guarded edge cases:** every empty/boundary guard in your code (`if not nums`, `if not root`, an off-grid check) *is* an edge case — name it in Understand and re-trace it in Review, don't let it appear unexplained. Each chapter closes with an "edge cases to surface" note listing the ones for that pattern.
- **Off-by-one:** loop bounds, `<=` vs `<` in binary search, `right - left + 1` for window size.
- **Empty / single-element input:** does your code handle `[]`, `""`, a one-node list/tree?
- **Duplicate results in k-sum:** sorting lines equal values up, so the same triple surfaces twice — dedupe the blunt way first (dump triples in a set), then optimize by skipping repeated anchors and repeated pointer values so you never generate a copy.
- **Forgot the visited set:** every graph traversal needs one — or you loop forever.
- **Mutating while recording:** snapshot with `path[:]` in backtracking; don't append the live list.
- **Returning the wrong end:** linked-list reversals return the *new* head (old tail); use a dummy for head changes.
- **Min-heap when you wanted max:** Python's `heapq` is a min-heap; negate for max.
- **Integer overflow (Java/C++):** use `low + (high - low) // 2` for midpoints; mention it even in Python.
- **Binary search infinite loop:** always move *past* mid (`low = mid + 1`, `high = mid - 1`) for exact match.
- **Re-summing the window:** slide (add entering, drop leaving) instead of recomputing.
- **Confusing subarray (contiguous) with subsequence (gaps allowed):** window vs DP.
- **Not stating complexity:** always close with time and space, and the tradeoff you chose.

---

## F. The five-second decision flow

When the problem lands and your mind is blank, run this:

1. **What's the brute force?** State it. Get its Big-O.
2. **What's the repeated/wasted work?** Name it precisely.
3. **Which pattern deletes that waste?** (Table B / C above.)
4. **What does the constraint `n` allow?** (Table A — confirms the target complexity.)
5. **Plan in words, then code.** (UMPIRE, Chapter 15.)

> *A pattern is just the thing that deletes the specific waste in your brute force. Find the waste, and the pattern names itself.*
