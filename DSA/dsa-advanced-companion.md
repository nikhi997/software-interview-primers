# Optional advanced DSA companion: earn the specialist tool

*[← Chapter 15](dsa-chapter-15.md) · [Contents](dsa-README.md)*

This is an **optional companion, not Chapter 16 and not required for most software interviews**.
Finish the 15 chapters, solve the appendix's core list, and become calm with the
[mixed cold drills](dsa-mixed-cold-drills.md) first. Use this file when a target role or company
regularly asks harder algorithmic questions, or when the basic technique leaves a named bottleneck.

The rule does not change: **waste before pattern**. Never reach for a segment tree, SCC algorithm,
or all-pairs shortest path because it looks advanced. State the working baseline, name the exact
repeated work, check the constraints, and earn the specialist tool.

---

## How to use this companion

For each section:

1. Write the brute force and its complexity.
2. Circle the repeated operation.
3. Try the simplest patch first.
4. Check whether updates, ordering, edge weights, or output requirements invalidate that patch.
5. Only then implement the specialist structure or algorithm.
6. State the invariant and trace a small counterexample.

If sorting, a prefix sum, BFS/DFS, Dijkstra, or repeated scanning fits the constraints, use it. A
simple correct solution is better engineering and usually better interviewing.

---

## 1. Sorting and selection

### Waste ladder

**Problem fragment:** return the `k`th smallest item, or the largest `k` items.

- Sort everything: `O(n log n)`. Often completely sufficient and the best first answer.
- Keep a size-`k` heap: `O(n log k)` time, `O(k)` space. Earn it when `k << n`, data streams, or
  you only need the top `k`.
- Quickselect: expected `O(n)`, worst `O(n²)`, usually in-place. Earn it for one unsorted-array
  order statistic when expected performance is acceptable and output need not be sorted.

Quickselect's invariant is the same as quicksort partitioning: after partition, every element left
of the pivot belongs on one side of its final rank and every element right belongs on the other.
Only recurse into the side containing the requested rank.

```python
def kth_smallest(values, k):  # k is zero-based; this mutates values
    left, right = 0, len(values) - 1
    while left <= right:
        pivot = values[right]
        boundary = left
        for index in range(left, right):
            if values[index] <= pivot:
                values[boundary], values[index] = values[index], values[boundary]
                boundary += 1
        values[boundary], values[right] = values[right], values[boundary]
        if boundary == k:
            return values[boundary]
        if boundary < k:
            left = boundary + 1
        else:
            right = boundary - 1
    raise IndexError("k out of range")
```

**Do not use quickselect** when you need stable ordering, all results sorted, deterministic worst-case
behavior, or repeated rank queries over unchanged data (sort once instead).

**Cold prompts:** median without fully sorting; top 100 events from a stream; merge overlapping
records after sorting by start. For each, explain why the other two choices lose.

---

## 2. Intervals, sweep lines, and difference arrays

### Intervals: sorting deletes pairwise comparison

Comparing every interval with every other interval is `O(n²)`. Sort by start once, then the only
interval that can overlap the next one is the current merged tail. That gives `O(n log n)` time.
State the boundary convention first: do `[1, 3]` and `[3, 5]` overlap? Closed and half-open
intervals answer differently.

### Sweep line: process changes, not every point

For maximum simultaneous meetings, expanding every time unit wastes work and fails for continuous
or huge coordinates. Convert each interval into `(start, +1)` and `(end, -1)` events, sort events,
and maintain the active count. Tie-breaking encodes semantics: for half-open `[start, end)`,
process an end before a start at the same coordinate.

```python
def max_overlap(intervals):
    events = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    active = best = 0
    for _, delta in sorted(events, key=lambda event: (event[0], event[1])):
        active += delta
        best = max(best, active)
    return best
```

### Difference array: batch range updates

Applying each of `q` range increments to every element costs `O(nq)`. For an offline, fixed-size
array, write `+delta` at `left` and `-delta` after `right`, then prefix-sum once. Cost:
`O(n + q)` time and `O(n)` space. The invariant is that the running prefix equals the total effect
of all ranges currently open.

```python
def apply_range_additions(size, updates):
    difference = [0] * (size + 1)
    for left, right, delta in updates:  # inclusive endpoints
        difference[left] += delta
        if right + 1 < size:
            difference[right + 1] -= delta
    values = []
    running = 0
    for index in range(size):
        running += difference[index]
        values.append(running)
    return values
```

**Do not use a difference array** for online interleaved updates and queries; that pain earns the
next section.

---

## 3. Fenwick and segment trees

Start with the alternatives:

- static range-sum queries: prefix sums, `O(n)` build and `O(1)` query;
- frequent point updates with naive range sums: `O(1)` update, `O(n)` query;
- update a prefix table after every change: `O(n)` update, `O(1)` query.

The waste is repeatedly rebuilding or rescanning after **interleaved** updates and queries.

### Fenwick tree (Binary Indexed Tree)

A Fenwick tree stores partial sums whose ranges are determined by the least significant set bit.
Point update and prefix sum are both `O(log n)` with `O(n)` space. Range sum is two prefix sums.
Use it when the operation is invertible enough for prefix subtraction (sum is the classic case).

```python
class Fenwick:
    def __init__(self, size):
        self.tree = [0] * (size + 1)

    def add(self, index, delta):
        index += 1
        while index < len(self.tree):
            self.tree[index] += delta
            index += index & -index

    def prefix_sum(self, end):
        total = 0
        while end > 0:
            total += self.tree[end]
            end -= end & -end
        return total

    def range_sum(self, left, right):
        return self.prefix_sum(right + 1) - self.prefix_sum(left)
```

Invariant: `tree[i]` stores the sum of the block ending at one-based index `i` with length
`i & -i`.

### Segment tree

A segment tree stores an aggregate for each interval in a binary partition. Point update and range
query are `O(log n)`; build and space are `O(n)`. It is more general than Fenwick: minimum, maximum,
GCD, or a custom associative merge. **Lazy propagation** earns its complexity only when range
updates would otherwise touch many leaves; defer an update at a covered segment and push it only
when descending.

Choose:

| Need | Simplest valid tool |
|---|---|
| Static range sum | Prefix sum |
| Offline batch range adds, final values | Difference array |
| Point updates + range sums | Fenwick tree |
| Point updates + range min/max/custom associative aggregate | Segment tree |
| Range updates + range queries | Lazy segment tree (only if required) |

**Cold prompts:** mutable account totals by index; minimum sensor value in a changing interval;
offline capacity additions. Say why the simpler rows fail before choosing.

---

## 4. Advanced graph tools

Chapter 12 covers Dijkstra, topological sort, and Union-Find. The next tools are specialist answers
to specific violations of those assumptions.

### Minimum spanning tree (MST): connect everything cheaply

Shortest path minimizes a route from a source. An MST chooses `V - 1` edges connecting **all**
vertices with minimum total cost. Do not confuse the objectives.

- **Kruskal:** sort edges by weight; add an edge if Union-Find says it does not make a cycle.
  `O(E log E)`. Natural for an edge list or sparse graph.
- **Prim:** grow one connected tree by repeatedly taking the cheapest crossing edge with a heap.
  `O(E log V)`. Natural for adjacency lists.

Kruskal's invariant: chosen edges form an acyclic forest, and the next cheapest edge connecting two
components is safe. Use for "connect all sites/cities with minimum total cable cost," not "cheapest
route from A to B."

### 0-1 BFS: weights are only zero or one

Plain BFS assumes equal weights; Dijkstra handles non-negative weights. When every edge is `0` or
`1`, use a deque: a zero-cost relaxation goes to the front, a one-cost relaxation to the back.
`O(V + E)` instead of heap-based `O((V + E) log V)`.

```python
from collections import deque


def zero_one_bfs(graph, start):
    distance = {node: float("inf") for node in graph}
    distance[start] = 0
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor, weight in graph[node]:
            candidate = distance[node] + weight
            if candidate < distance[neighbor]:
                distance[neighbor] = candidate
                if weight == 0:
                    queue.appendleft(neighbor)
                else:
                    queue.append(neighbor)
    return distance
```

### Strongly connected components (SCC): mutual reachability

Running DFS from every node to test mutual reachability costs `O(V(V + E))`. Tarjan's or
Kosaraju's algorithm partitions a directed graph into maximal groups where every node reaches every
other in `O(V + E)`. Collapse each SCC into one node and the remaining **condensation graph is a
DAG**, enabling topological reasoning. Use for dependency cycles, module groups, and "which nodes
are mutually reachable?" Tarjan tracks discovery index, low-link value, and an active stack;
Kosaraju uses finish order plus a traversal of the reversed graph. In an interview, implement the
one you can explain reliably.

### Bellman-Ford: negative edges and cycle detection

Dijkstra's "popped is final" invariant fails with negative edges. Bellman-Ford relaxes every edge
`V - 1` times: any simple shortest path has at most `V - 1` edges. One more successful relaxation
proves a reachable negative cycle. Cost `O(VE)`, space `O(V)`. Use only when negative edges or
negative-cycle detection require it.

### Floyd-Warshall: all pairs, usually small dense graphs

Running a single-source algorithm from every source can be wasteful when the graph is small/dense
and you need all-pairs distances. Floyd-Warshall tries each vertex as an allowed intermediate:

`dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])`

After phase `k`, the invariant is that `dist[i][j]` is shortest using only vertices `0..k` as
intermediates. Cost `O(V³)` time and `O(V²)` space, so constraints must be small. A negative
`dist[i][i]` reveals a negative cycle.

### Graph decision table

| Signal / requirement | Tool |
|---|---|
| Unweighted shortest path | BFS |
| Non-negative weighted path | Dijkstra |
| Weights only 0 or 1 | 0-1 BFS |
| Negative edges / reachable negative cycle | Bellman-Ford |
| All-pairs, small graph | Floyd-Warshall |
| Connect all vertices at minimum total cost | MST (Kruskal/Prim) |
| Mutual reachability groups in a directed graph | SCC |
| Dependency ordering in a DAG | Topological sort |

---

## 5. Mixed advanced drill packet

Timebox: **45 minutes**. Do not label the pattern until you have written the waste.

1. **Release overlap.** Given half-open deployment windows `[start, end)`, return the maximum number
   active at once. Equal end/start timestamps do not overlap.
2. **Changing ledger.** Support `add(index, delta)` and `sum(left, right)` over 100,000 accounts,
   with 100,000 interleaved operations.
3. **Free or paid lane.** Directed edges cost only 0 or 1; return the cheapest cost from a source to
   every node.
4. **Network contract groups.** In a directed call graph, return groups of services that are all
   mutually reachable.
5. **Cheapest full wiring.** Connect all offices with minimum total cable cost; returning one
   source-to-destination route is insufficient.

For every problem record:

```text
Working baseline:
Baseline complexity:
Exact repeated work:
Simplest patch:
Why the patch fails the constraints:
Earned tool:
Invariant:
Counterexample / edge case:
Final time and space:
```

**Review gate:** if you selected a specialist tool before filling "exact repeated work," redo the
problem from the baseline. Recognition without derivation is the failure this track is designed to
prevent.

---

## Optional practice list

Only after the core appendix list:

- Sorting/selection: Kth Largest Element, Top K Frequent Elements, K Closest Points.
- Intervals/sweep: Merge Intervals, Meeting Rooms II, Car Pooling, Skyline (hard).
- Fenwick/segment tree: Range Sum Query Mutable, Count of Smaller Numbers After Self; implement
  range minimum with point updates.
- MST/0-1 BFS/SCC: Min Cost to Connect All Points, Swim in Rising Water, a 0-1 grid path, Critical
  Connections / SCC condensation exercises.
- Bellman-Ford/Floyd-Warshall: Cheapest Flights Within K Stops, Find the City With the Smallest
  Number of Neighbors; construct and detect a negative cycle.

The goal is not to collect names. It is to recognize the narrow condition that earns each tool.

## The bumper sticker

> *Advanced algorithms are not a second catalog to memorize. They are what remains after the simple
> solution meets a precise constraint: dynamic queries earn a tree, 0/1 weights earn a deque,
> negative edges earn repeated relaxation, mutual reachability earns SCC. Name the waste, fail the
> simple patch honestly, and the specialist tool earns its place.*

---

<div align="right">

[Appendix →](dsa-appendix.md)

</div>
