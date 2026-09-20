# Chapter 12: Weighted edges and ordering — Dijkstra, topo sort, union-find

*[← Chapter 11](dsa-chapter-11.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

Plain BFS assumes every edge costs the same. Real graphs rarely do — roads have lengths, networks have latencies, tasks have durations. And some graphs carry *constraints*: "you must do A before B." This chapter adds three specialist tools for these cases. You won't use them as often as BFS/DFS, but when a problem fits, nothing else works, and naming the right one is a strong signal.

---

## Dijkstra: shortest path with weights

When edges have different (non-negative) weights, BFS's "first arrival = shortest" guarantee breaks — a path with more edges might be *cheaper*. The brute force would enumerate every path from the start and total each one's weights, keeping the cheapest — but the number of paths is exponential and they redundantly re-sum shared prefixes. **Dijkstra's algorithm** deletes that waste with one repeated move: always finalize the **cheapest-so-far** node next, then relax its neighbours.

Start with the plainest version that captures that idea. Keep a `distances` map and a `finalized` set; each round, *scan every unfinalized node* to find the cheapest one, finalize it, and relax its edges:

```python
def dijkstra_scanning(graph, start):           # graph[node] = [(neighbor, weight), ...]
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    finalized = set()
    while len(finalized) < len(graph):
        cheapest = None                        # the unfinalized node with the smallest distance
        for node in graph:
            if node not in finalized:
                if cheapest is None or distances[node] < distances[cheapest]:
                    cheapest = node
        if distances[cheapest] == float("inf"):
            break                              # everything left is unreachable
        finalized.add(cheapest)
        for neighbor, weight in graph[cheapest]:
            new_cost = distances[cheapest] + weight
            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost # found a cheaper route to neighbor
    return distances                           # shortest cost from start to each node
```

This is correct and easy to read, but look at the cost: finding the cheapest node re-scans every node, and we do that once per node — `O(V²)`. The scan *is* the waste. We're asking "what's the smallest thing left?" over and over — which is exactly what a **min-heap** (Chapter 10) answers in `O(log V)`. So replace the linear scan with a priority queue:

```python
import heapq

def dijkstra(graph, start):                    # graph[node] = [(neighbor, weight), ...]
    distances = {start: 0}
    heap = [(0, start)]                        # (cost so far, node)
    while heap:
        cost, node = heapq.heappop(heap)       # cheapest unfinalized node
        if cost > distances.get(node, float("inf")):
            continue                           # stale entry, skip
        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if new_cost < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_cost # found a cheaper route to neighbor
                heapq.heappush(heap, (new_cost, neighbor))
    return distances                           # shortest cost from start to each node
```

`O((V + E) log V)` with a binary heap — the heap buys back the `O(V²)` scan. It's BFS's smarter cousin: instead of a plain queue (FIFO), it uses a **priority queue** so the next node explored is always the one with the smallest total cost. (On dense graphs where `E ≈ V²`, the plain scanning version is actually competitive — worth saying out loud.)

The `if cost > distances.get(node, float("inf")): continue` line is a genuine edge case, not noise: the same node can sit in the heap several times with different costs, and this skips the **stale, already-beaten copies**. Two more to surface up front — **unreachable nodes** (they never leave `float('inf')`, so decide how you report them) and, for the topological sort below, a **cycle** (Kahn's algorithm returns a short list, which is how you answer "is this even possible?").

> 💡 **Concept notes — when Dijkstra, and its one rule**
> Use Dijkstra for **shortest path with non-negative weights.** The core insight: once you pop a node from the priority queue, its shortest distance is *final* — because any other route to it would go through a node that's already more expensive. The one hard rule: **no negative edge weights** (they break the "popped = finalized" guarantee; use Bellman-Ford for those, rarely needed in interviews). If all weights are equal, Dijkstra degenerates to BFS — so reach for plain BFS when edges are unweighted, Dijkstra when they're not.

---

## Topological sort: ordering with dependencies

Some problems give a **directed acyclic graph (DAG)** of dependencies — "course B requires course A," "task X before task Y" — and ask for a valid order. That's a **topological sort**: a linear ordering where every edge points forward (every prerequisite comes before what needs it).

The cleanest method is **Kahn's algorithm** (BFS on in-degrees): repeatedly take a node with no remaining prerequisites.

```python
from collections import deque, defaultdict

def topo_sort(num_nodes, edges):               # edge (before, after) means before must come first
    graph = defaultdict(list)
    indegree = [0] * num_nodes
    for before, after in edges:
        graph[before].append(after)
        indegree[after] += 1                   # `after` has one more prerequisite

    queue = deque()
    for node in range(num_nodes):
        if indegree[node] == 0:                # no prerequisites -> ready to start now
            queue.append(node)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1            # one prerequisite satisfied
            if indegree[neighbor] == 0:
                queue.append(neighbor)         # now free to take
    return order if len(order) == num_nodes else []   # [] => a cycle exists
```

`O(V + E)`. A beautiful side effect: if you *can't* order all nodes (some never reach in-degree 0), the graph has a **cycle** — which is exactly how you detect "is this schedule even possible?"

> 💡 **Concept notes — topological sort signals**
> Reach for topo sort when you see **"order," "schedule," "prerequisites," "dependencies," "build order," "compile order,"** on a **directed** graph. Two things fall out of one algorithm: a valid ordering *and* cycle detection (if the output is shorter than the node count, a cycle made it impossible). "Course Schedule" and "Alien Dictionary" are the canonical interview problems.

---

## Union-Find: are these two connected?

Some problems repeatedly ask "**are A and B in the same group?**" and "**merge these two groups**" — connectivity that *changes* as you add edges. Running BFS/DFS for each query is wasteful. **Union-Find** (disjoint set union) answers both in nearly `O(1)`.

The idea: give every node a **parent** pointer. Each group is a tree, and the group's identity is its **root** (a node that is its own parent). "Same group?" walks both nodes up to their roots and compares them; "merge" points one root at the other. Here's the primitive version:

```python
class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))        # each node starts as its own root

    def find(self, node):
        while self.parent[node] != node:       # walk up to the root
            node = self.parent[node]
        return node

    def union(self, node_a, node_b):
        root_a, root_b = self.find(node_a), self.find(node_b)
        if root_a != root_b:
            self.parent[root_b] = root_a       # hang one tree under the other
```

Correct, but it has a pain: nothing controls the *shape* of the trees. Merge in an unlucky order and you build a long chain `0 → 1 → 2 → … → n`, so `find` walks the whole thing — back to `O(n)` per query, the exact cost we wanted to kill.

Two small moves fix it. **Union by rank:** always hang the shorter tree under the taller one, keeping trees shallow. **Path compression:** while `find` walks up, re-point nodes closer to the root, flattening the tree for next time. Together they make every operation effectively `O(1)`.

```python
class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))        # each node starts as its own group
        self.rank = [0] * size                 # tree height, for union-by-rank

    def find(self, node):
        while self.parent[node] != node:
            self.parent[node] = self.parent[self.parent[node]]   # path compression
            node = self.parent[node]
        return node                            # the group's representative (root)

    def union(self, node_a, node_b):
        root_a, root_b = self.find(node_a), self.find(node_b)
        if root_a == root_b:
            return False                       # already connected
        if self.rank[root_a] < self.rank[root_b]:   # attach smaller tree under bigger
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1
        return True                            # merged two distinct groups
```

With path compression and union-by-rank, each operation is **effectively `O(1)`** (technically inverse-Ackermann, which is < 5 for any realistic input). It's the perfect tool for "number of connected components," "redundant connection," "accounts merge," and Kruskal's minimum-spanning-tree algorithm.

> 💡 **Concept notes — union-find vs DFS for connectivity**
> Both can find connected components. Choose union-find when connections **arrive incrementally** and you must answer "connected?" queries *as you go* (a dynamic, growing graph), or when you just need to **count groups** after merging many edges — it's simpler than rebuilding a graph and re-running DFS. Choose DFS/BFS when the graph is **fixed** and you also need the actual paths or traversal order. "Group things as edges stream in" → union-find.

---

## Recognizing these three

- **"Shortest/cheapest path" with weights** → Dijkstra (priority queue).
- **"Order," "schedule," "prerequisites," "dependencies," "can it be done"** on a directed graph → topological sort (and cycle detection for free).
- **"Same group?", "connected components," "merge sets," "redundant edge," "minimum spanning tree"** → union-find.

> 💡 **Concept notes — edge cases to surface**
> Weighted-graph algorithms hinge on inputs you must name: **negative edge weights** (Dijkstra silently gives wrong answers — say "assuming non-negative weights" out loud), **unreachable nodes** (infinite distance), a **cycle** in what's meant to be a DAG (topological sort detects it — output shorter than the node count), and **single-node or empty** graphs. In Review, a two-node graph with one edge is the smallest trace that exercises a relaxation.

---

## Try it

1. *Network Delay Time:* time for a signal to reach all nodes from a source, with weighted edges. Why Dijkstra and not BFS?
2. *Course Schedule II:* return a valid order to take all courses given prerequisites, or empty if impossible. How does the algorithm reveal a cycle?
3. *Number of Connected Components in an Undirected Graph:* count components using union-find. What does `find` return, and when does `union` actually merge?
4. *Cheapest Flights Within K Stops:* shortest path with at most K stops — why does plain Dijkstra need a tweak here?
5. Explain why Dijkstra requires non-negative edge weights, using the "popped node is finalized" guarantee.

*Write your answers in [dsa-chapter-12-tryit.md](code/dsa-chapter-12-tryit.md).*

---

## The bumper sticker

> *Weighted shortest path → Dijkstra (BFS with a priority queue). Dependencies and ordering → topological sort (which also detects cycles). Dynamic "are these connected?" → union-find (near `O(1)` per query). Match the constraint to the specialist.*

Next: leaving graphs for the art of trying *every* possibility cleanly — recursion and backtracking.

---

<div align="right">

[Chapter 13 →](dsa-chapter-13.md)

</div>
