# Chapter 19: Worked problem — LRU Cache

*[← Chapter 18](lld-chapter-18.md) · [Contents](lld-README.md)*

- [ ] **Mark as read**

A worked problem, same ritual as the others. This one is different in one way: the patterns are nearly absent, and the *data structure* is the whole design. It's where your DSA reps meet your LLD reps, which is exactly why interviewers love it — it's almost guaranteed somewhere in a loop.

The problem: *"Design an LRU cache. `get(key)` returns the value or a miss. `put(key, value)` inserts or updates. The cache has a fixed capacity; when it's full and a new key arrives, evict the least recently used entry. Both operations must be O(1)."*

## Step 1: Clarify

- Capacity fixed at construction? **Yes, a positive integer.**
- What does `get` return on a miss? **`None` for now (could be a sentinel or an exception).**
- Does `get` count as a use? **Yes. Both `get` and `put` mark a key as most recently used.**
- What gets evicted? **The least recently used key, and only when a *new* key would exceed capacity.**
- Hard requirement on speed? **Yes — `get` and `put` both O(1) average. This is the crux, not a nice-to-have.**
- Thread-safe? **Single-threaded core; I'll cover locking in tradeoffs.**

Scope locked. Note the O(1) requirement — it's what makes this a real problem.

## Step 2: Entities

Short list. That's a hint the difficulty isn't in the modeling.

- **Node** — one cache entry: `key`, `value`, and two neighbor links (`prev`, `next`).
- **LRUCache** — holds the capacity, a hash map from key to its node, and an ordering of nodes from most- to least-recently-used.

## Step 3: Class diagram, and why it has to be this shape

This is the step that matters, so let's earn it instead of asserting it. Feel the brute force first.

**Attempt — just a dict.** `{key: value}` gives O(1) `get` and `put`. But a dict has no notion of "least recently used." When you're full, finding the LRU key means scanning every entry to see which was touched longest ago — O(n). Fails the requirement.

**Attempt — a list ordered by recency.** Keep keys in a list, most-recent at the end. Eviction is cheap (pop the front). But every `get` has to move the touched key to the end: find it (O(n)), remove it (O(n)), append. Fails again.

The two requirements pull apart:

- *"Find the entry for this key, fast"* wants a **hash map**.
- *"Reorder by recency, fast"* wants a structure where you can yank a known item out of the middle and move it, in O(1).

A **doubly linked list** does that second job — *if you already hold the node*, you can splice it out (`node.prev.next = node.next`, and the mirror) and re-insert at the front in constant time. The only missing piece is getting from a key to its node without searching. That's exactly what the hash map gives you.

So the move is: **combine them.** The hash map maps `key → Node`. The nodes live in a doubly linked list ordered by recency. Neither alone is enough; together they're O(1) for both operations. That combination *is* the design.

```
LRUCache
  capacity: int
  map: { key -> Node }            # O(1) lookup
  doubly linked list:             # O(1) reorder
      head <-> ... <-> tail
      (head side = most recent, tail side = least recent)

Node
  key, value
  prev, next
```

> 💡 **Concept note — why two sentinels**
> I give the list a dummy `head` and dummy `tail` node that never hold real data. Without them, inserting into an empty list or removing the last real node forces "is this the end?" special-cases in every splice. With sentinels, every real node always has a real neighbor on both sides, so insert and remove are the same three lines every time. A tiny bit of setup buys a lot of missing `if`s.

## Step 4: Code skeleton

```python
class Node:
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.map = {}                      # key -> Node

        # sentinels: head side is most-recently-used, tail side is least
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.map:
            return None
        node = self.map[key]
        self._remove(node)          # it was somewhere in the list
        self._add_to_front(node)    # now it's most recent
        return node.value

    def put(self, key, value):
        if key in self.map:
            node = self.map[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
            return

        if len(self.map) >= self.capacity:
            lru = self.tail.prev    # the node just before the tail sentinel
            self._remove(lru)
            del self.map[lru.key]   # this is why the Node stores its key

        node = Node(key, value)
        self.map[key] = node
        self._add_to_front(node)
```

Two helpers, `_remove` and `_add_to_front`, do all the pointer work; `get` and `put` read like sentences. Notice the node stores its own `key` — on eviction we have the node (the tail's neighbor) but need the key to delete it from the map. Without the back-reference, that lookup would be O(n) and we'd have lost the whole game.

## Step 5: Walk a flow

*Capacity 2. Two puts, a get that changes recency, then an insert that forces eviction.*

```python
cache = LRUCache(2)
cache.put(1, "a")      # [1]
cache.put(2, "b")      # [2, 1]  (most recent first)
cache.get(1)           # "a"  -> [1, 2]   touching 1 makes it most recent
cache.put(3, "c")      # full: evict least recent (2) -> [3, 1]
cache.get(2)           # None  (2 was evicted)
cache.get(3)           # "c"
```

The key beat is `get(1)`: because the get promoted 1 to most-recent, the later `put(3, ...)` evicts **2**, not 1. If `get` *didn't* count as a use, 1 would have been the victim. That's the whole behavior of the cache, and it falls out of two O(1) splices.

## Step 6: Tradeoffs

- **"Make it thread-safe."** → Wrap `get` and `put` in a `threading.Lock` (appendix C). Both mutate the shared list and map, so both are critical sections — even `get`, because it reorders. Read-heavy workloads can use a read-write lock, but note that *every* `get` here is a writer to the ordering.

- **"What if the policy needs to change to LFU or FIFO?"** → Make eviction a **Strategy** (Ch3). The cache holds an eviction policy object; LRU, LFU, and FIFO each implement "pick the victim" and "record a use." The linked-list machinery stays; only the choice of victim swaps.

- **"Entries should expire after N seconds."** → Store an expiry timestamp on each `Node`; treat an expired entry as a miss on `get` and lazily evict it. Combine TTL with LRU by checking expiry first.

- **"Couldn't you just use `OrderedDict`?"** → Yes. `collections.OrderedDict` has `move_to_end` and `popitem(last=False)`; the whole cache becomes about ten lines. Say so in an interview — but then offer the doubly-linked-list version, because the question is testing whether you *understand the mechanism* the library is hiding. (That's the Foundations principle: feel the mechanism before you trust the abstraction.)

- **"Capacity by memory, not count."** → Track the byte size of values; evict from the LRU end until you're back under the limit. The eviction loop replaces the single-victim check.

## Pattern audit

Used:
- **Plain classes** — `Node` and `LRUCache`.
- **A hash map + a doubly linked list** — the actual design. No Gang-of-Four pattern in sight.

Could be added (and only if asked):
- **Strategy** — swappable eviction policy (LRU / LFU / FIFO).
- **Decorator** — a thread-safe wrapper around a plain cache, or a logging/metrics layer (Ch8, Ch18).
- **Observer** — fire a callback on eviction, so an owner can flush a dirty entry.

The lesson worth carrying out of this chapter: not every LLD problem wants a pattern. Sometimes the strong answer is the right data structure, named plainly, with the patterns held in reserve for the follow-ups. Reaching for a pattern here would be the shoehorning the appendix warns about.

---

<div align="right">

[Chapter 20 →](lld-chapter-20.md)

</div>
