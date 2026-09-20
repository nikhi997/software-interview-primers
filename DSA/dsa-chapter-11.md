# Chapter 11: Everything is a graph — BFS and DFS

*[← Chapter 10](dsa-chapter-10.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

A linked list is a graph where each node has one neighbor. A tree is a graph with no cycles and a single root. Drop those restrictions — let nodes connect to *any* other nodes, in cycles, with multiple paths — and you have the **graph**, the most general structure in this book. Maps, social networks, dependencies, the web, game states, mazes: all graphs.

The good news: two traversals — **BFS** and **DFS** — solve a startling fraction of graph problems. You already met both (BFS on trees in Chapter 8, DFS as recursion throughout). Graphs add one new worry — **cycles** — and one new habit: **mark what you've visited.**

---

## Representing a graph

> 💡 **Concept notes — graph vocabulary and representation**
> A **graph** is nodes (**vertices**) connected by **edges**. Edges can be **directed** (one-way, like Twitter follows) or **undirected** (mutual, like Facebook friends), and **weighted** (each edge has a cost) or unweighted. The standard in-memory form is an **adjacency list**: a map from each node to its list of neighbors — `O(V + E)` space, efficient for the sparse graphs common in interviews. (An adjacency *matrix*, a `V×V` grid, costs `O(V²)` and only pays off for dense graphs.) Grids — mazes, islands — are graphs too: each cell is a node, neighbors are the up/down/left/right cells.

```python
from collections import defaultdict

def build_graph(edges):                       # edges = [(node, neighbor), ...] undirected
    graph = defaultdict(list)
    for node, neighbor in edges:
        graph[node].append(neighbor)
        graph[neighbor].append(node)          # drop this line for a directed graph
    return graph
```

---

## BFS: explore in rings, find shortest paths

Breadth-first search visits all neighbors at distance 1, then distance 2, and so on — expanding in rings. Because it reaches nearer nodes first, **BFS finds the shortest path in an unweighted graph.**

Why not just brute-force it — enumerate every path from `start` to `target` and keep the shortest? Because a graph with cycles has *infinitely* many walks, and even without cycles the number of simple paths grows exponentially; worse, all those paths re-walk the same early edges over and over. That re-walking is the waste. BFS deletes it by visiting each node **once**, in distance order, so the first arrival is already the shortest — no path enumeration needed.

One bookkeeping question: when we pop a node, how do we know its distance? We could keep a separate `node → distance` map, but the tidiest trick is to store `(node, distance)` pairs in the queue itself — each node carries its own distance, so popping it tells us how far it is for free.

```python
from collections import deque

def bfs_shortest(graph, start, target):
    visited = {start}
    queue = deque([(start, 0)])               # (node, distance from start)
    while queue:
        node, distance = queue.popleft()
        if node == target:
            return distance                   # first time we reach it = shortest
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)         # mark BEFORE enqueue (avoid dupes)
                queue.append((neighbor, distance + 1))
    return -1                                 # unreachable
```

`O(V + E)` — each node and edge is examined once. The critical detail: **mark a node visited when you enqueue it**, not when you dequeue it, or the same node gets added many times.

> 💡 **Concept notes — why BFS gives shortest paths (unweighted)**
> BFS processes nodes in strict order of distance from the start: all distance-1 nodes, then all distance-2 nodes, never skipping ahead. So the *first* time it reaches the target, it has used the fewest possible edges — that's the shortest path. This only holds when every edge counts the same (unweighted). The moment edges have *different* weights, BFS breaks and you need Dijkstra (Chapter 12).

Trace `bfs_shortest` on this little graph, searching for `A → D`:

```
A ── B
|    |
C ── D
```

| Pop `(node, dist)` | Newly visited & enqueued | Queue after |
| --- | --- | --- |
| `(A, 0)` | B, C at dist 1 | `[(B,1), (C,1)]` |
| `(B, 1)` | D at dist 2 | `[(C,1), (D,2)]` |
| `(C, 1)` | — (A, D already visited) | `[(D,2)]` |
| `(D, 2)` | target! return **2** | — |

We pop in distance order, so the *first* time `D` comes off the queue its distance is already the shortest — and `C`'s attempt to re-visit `D` is silently dropped by the `visited` set, which is the waste the brute force never avoided.

---

## DFS: go deep, great for connectivity

Depth-first search plunges down one path as far as it can, then backtracks. It's the natural tool for "is everything connected?", "how many separate components?", "does a path exist?", and exploring all of something (like flood-fill).

```python
def dfs(graph, start):
    visited = set()
    def explore(node):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:       # the cycle guard
                explore(neighbor)
    explore(start)
    return visited                            # everything reachable from start
```

Same `O(V + E)`. The `if neighbor not in visited` check is what stops a cycle from looping forever — the one thing trees never needed.

> 💡 **Concept notes — the visited set is non-negotiable**
> Unlike trees, graphs have **cycles** and **multiple paths** to the same node. Without a `visited` set, DFS/BFS will revisit nodes endlessly (infinite loop) or redo exponential work. *Every* graph traversal needs it. For grid problems you can either keep a `visited` set of coordinates or mark cells in place (e.g., flip `'1'`→`'0'`). Forgetting the visited check is the #1 graph bug.

---

## The grid template (islands, flood fill, mazes)

A 2D grid is a graph in disguise; this template — DFS from each unvisited "land" cell, sinking the whole island — solves a big family of problems:

```python
def num_islands(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])

    def sink(row, col):
        if row < 0 or row >= rows or col < 0 or col >= cols or grid[row][col] != "1":
            return                            # off-grid or water -> stop
        grid[row][col] = "0"                  # mark visited by sinking it
        sink(row + 1, col); sink(row - 1, col)    # explore 4 neighbors
        sink(row, col + 1); sink(row, col - 1)

    count = 0
    for row in range(rows):
        for col in range(cols):
            if grid[row][col] == "1":         # new unvisited island
                count += 1
                sink(row, col)                # drown all of it
    return count
```

That five-part guard in `sink` — `row < 0 or row >= rows or col < 0 or col >= cols or grid[row][col] != "1"` — is the Understand step written as code: it's how you handle running **off the grid** and hitting **water**. Say the grid's boundaries out loud first — an **empty grid** (`if not grid`), a **single cell**, an **all-water grid** (zero islands), an **all-land grid** (one island) — so the guard is a deliberate decision, not a line you copied.

Each cell is visited once: `O(rows × cols)`. Recognize the shape — *"count/measure connected regions in a grid"* — and this template is your answer.

---

## Choosing BFS or DFS

> 💡 **Concept notes — the decision**
> - **Shortest path / fewest steps** in an unweighted graph → **BFS** (rings reach the target by the shortest route first).
> - **Connectivity, components, "does a path exist," explore-everything, flood fill** → **DFS** (simpler to write recursively) — though BFS works too.
> - **Level-by-level** processing → BFS.
> - **Very deep** graphs where recursion might overflow the stack → BFS, or DFS with an explicit stack (Chapter 6).
> When in doubt for "explore everything," reach for DFS (less code); for "shortest/fewest," reach for BFS.

---

## Recognizing a graph problem

- Explicit graphs: **networks, dependencies, connections, maps.**
- Disguised graphs: **grids/mazes** (cells = nodes), **word ladders** (words = nodes, one-letter changes = edges), **state machines** (states = nodes, moves = edges).
- Keywords: **"shortest path," "connected," "reachable," "number of islands/regions," "clone a graph," "can you get from A to B."**

> 💡 **Concept notes — edge cases to surface**
> The load-bearing graph edge case is the **`visited` set itself** — omit it and cycles loop forever (the chapter's #1 bug). Beyond that, surface: a **disconnected graph** (some nodes unreachable from the start), a **single node** or empty graph, and for grids the **out-of-bounds** neighbours the guard above rejects. In Review, run one input with a cycle to prove the visited check actually stops it.

---

## Try it

1. *Number of Islands:* you have the template — what marks a cell visited, and why does that avoid a separate visited set?
2. *Clone Graph:* deep-copy a graph. (Hint: BFS/DFS while keeping a map from original node → copy, to handle cycles.)
3. *Word Ladder:* fewest one-letter transformations from one word to another, each step a valid word. Why is this BFS, and what are the nodes and edges?
4. *Rotting Oranges:* minutes until all oranges rot, spreading to neighbors each minute. Why is *multi-source* BFS the right tool? (Start with all rotten oranges in the queue.)
5. Explain precisely why BFS finds shortest paths on unweighted graphs but fails when edges have different weights.

*Write your answers in [dsa-chapter-11-tryit.md](code/dsa-chapter-11-tryit.md).*

---

## The bumper sticker

> *Almost everything is a graph. BFS expands in rings (shortest paths, fewest steps); DFS plunges deep (connectivity, components, flood fill). Both are `O(V + E)` — and both die in an infinite loop without a visited set.*

Next: graphs with *weighted* edges and *ordering* constraints — Dijkstra for shortest paths with costs, topological sort for dependencies, and union-find for connectivity.

---

<div align="right">

[Chapter 12 →](dsa-chapter-12.md)

</div>
