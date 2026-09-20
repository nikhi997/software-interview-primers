# Chapter 10: Keeping only the most extreme thing on top

*[← Chapter 9](dsa-chapter-9.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

A BST keeps *everything* sorted, which is more than you often need. Many problems only ask for *the* most extreme element — the smallest, the largest, the top-k — over and over, while new elements keep arriving. Fully sorting is overkill. The **heap** does exactly the needed amount: it keeps the single most extreme element instantly available, and nothing more.

This is the structure behind "top k," "k closest," "merge k lists," "median of a stream," and any time the word **priority** shows up.

---

## The brute force and its waste

*Find the `k` largest elements in a list.*

Brute force: sort the whole thing, take the last `k`.

```python
def k_largest_sort(nums, k):
    return sorted(nums)[-k:]          # O(n log n) to sort everything
```

`O(n log n)`. The waste: we sorted *all* `n` elements to keep only `k`. If `k` is small (top 10 out of a million), we did a million-element sort to answer a ten-element question. We need the relative order of the top `k`, not of everything.

---

## The move: a heap of size k

A **heap** gives you the minimum (or maximum) in `O(1)` and lets you add/remove in `O(log n)`. Keep a **min-heap of size `k`**: it holds the `k` largest seen so far, with the *smallest of those k* on top. Each new element only has to beat that smallest-of-the-top.

```python
import heapq

def k_largest(nums, k):
    heap = []                              # min-heap, size capped at k
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)            # evict the smallest -> keep top k
    return heap                            # the k largest (unordered)
```

`O(n log k)` time, `O(k)` space. When `k ≪ n`, `log k` is tiny compared to `log n`, and we never stored more than `k` elements. We did the *minimum* sorting work: just enough to know the top `k`.

That `if len(heap) > k` line is the whole mechanism, so surface what `k` can be before you code: **`k` larger than the array** (you simply return everything), **`k == 0`** (an empty answer), and **ties** among values (does "k largest of `[5, 5, 5]`" return three fives?). Naming `k`'s range in Understand is what stops an off-by-one in the eviction.

> 💡 **Concept notes — what a heap actually is**
> A **heap** (binary heap) is a complete binary tree kept in an array, obeying the **heap property**: in a **min-heap**, every parent ≤ its children, so the global minimum sits at the root (index 0). It does *not* fully sort — siblings have no order — it just guarantees the top is the extreme. Operations: **peek** the min in `O(1)`, **push** and **pop-min** in `O(log n)` (the element "bubbles" up or down one level at a time). Building a heap from `n` items is `O(n)`. A **priority queue** is the abstract idea ("always serve the highest priority next"); a heap is its standard implementation.

> 💡 **Concept notes — Python's heapq is a min-heap**
> Python's `heapq` is always a **min-heap** (smallest on top). For a **max-heap**, negate the values on the way in and out (`heapq.heappush(h, -x)`), or store tuples `(-priority, item)`. For "k largest," counterintuitively you use a **min**-heap of size k (evict the smallest); for "k smallest," a **max**-heap of size k. The rule: to keep the k *largest*, the heap's removable element must be the *smallest of the kept set* — so it's a min-heap.

---

## The other classic: merging k sorted lists

*Merge `k` sorted lists into one sorted list.* The blunt first move ignores the sortedness entirely: pour every element into one pile and sort it.

```python
def merge_k_sorted_bruteforce(lists):
    merged = []
    for sorted_list in lists:
        merged.extend(sorted_list)     # dump everything together
    merged.sort()                      # then sort the whole pile
    return merged
```

`O(N log N)` for `N` total elements — correct, and honestly fine in a pinch. But it throws away a gift: each input list is *already sorted*, yet we re-sort as if the elements arrived in random order. Re-earning order we were handed for free is the waste.

A heap keeps that order instead. Hold one "frontier" element from each list, always pull the smallest, then advance only the list it came from:

```python
import heapq

def merge_k_sorted(lists):
    heap = []
    for list_index, sorted_list in enumerate(lists):
        if sorted_list:
            heapq.heappush(heap, (sorted_list[0], list_index, 0))   # (value, which list, index)
    result = []
    while heap:
        value, list_index, element_index = heapq.heappop(heap)      # smallest frontier element
        result.append(value)
        next_index = element_index + 1
        if next_index < len(lists[list_index]):                     # push that list's next element
            heapq.heappush(heap, (lists[list_index][next_index], list_index, next_index))
    return result
```

`O(N log k)` where `N` is the total element count — the heap never holds more than `k` items (one frontier per list). Against the brute force's `O(N log N)`, that's the win whenever `k` is much smaller than `N` (many short lists), because `log k < log N`. The tuple trick `(value, list_index, element_index)` lets the heap compare by value while remembering where each element came from.

> 💡 **Concept notes — how Python compares tuples**
> A heap orders items with `<`, and Python compares tuples **lexicographically**: it looks at the first element, and only consults the second if the firsts tie (then the third, and so on). So `(value, list_index, element_index)` sorts by `value` first — exactly what we want — while `list_index` and `element_index` ride along as pure bookkeeping that only ever breaks ties. That's why the thing you want to order by goes *first* in the tuple. One gotcha: if two values can tie and the next tuple slot isn't comparable (say, custom objects), insert a unique increasing counter as the tiebreaker so the comparison never reaches the object.

> 💡 **Concept notes — the "two heaps" trick for streaming medians**
> A famous heap pattern: **find the median of a stream** of numbers as they arrive. Keep *two* heaps — a max-heap for the smaller half and a min-heap for the larger half — balanced in size. The median is then the top of one heap (or the average of both tops), available in `O(1)`, with each insert `O(log n)`. Whenever you need a running median or to repeatedly query "the middle," reach for two balanced heaps.

---

## Recognizing a heap problem

- **"Top k," "k largest/smallest," "k closest," "k most frequent"** → heap of size `k`.
- **"Merge k sorted ..."** → heap holding one frontier per list.
- **"Median of a data stream," "running median"** → two heaps.
- **"Schedule by priority," "process the most urgent next," "Dijkstra"** (Chapter 12) → priority queue (a heap).
- Any time you repeatedly need *the* extreme element from a **changing** set — a heap beats re-sorting.

> 💡 **Concept notes — heap vs sorting vs BST, the decision**
> - Need the **whole thing sorted once**? Just **sort** — `O(n log n)`, simplest.
> - Need **the extreme element repeatedly** while the set changes (inserts/removes)? **Heap** — `O(log n)` per op, `O(1)` peek.
> - Need **arbitrary ordered queries** (range, predecessor, kth at any time, in-order)? **Balanced BST** (Chapter 9).
> "Top k of a static list" can go either way, but the heap's `O(n log k)` beats sorting's `O(n log n)` when `k` is much smaller than `n`.
> 💡 **Concept notes — edge cases to surface**
> Beyond `k`'s range (above), name the empties in Understand: an **empty input**, **`k` equal to `n`** (the heap ends up holding everything), and tied keys when you heap on a computed value. In Review, trace `k = 1` (the plain min/max) and `k = n` (no eviction ever happens) — the two extremes the size-`k` heap must both handle.
---

## Try it

1. *Kth Largest Element in an Array:* return the kth largest. Min-heap of size k — why size exactly k, and why min not max?
2. *Top K Frequent Elements:* the k most frequent values. (Hint: count with a hash map from Chapter 2, then heap the counts.)
3. *K Closest Points to Origin:* the k points nearest `(0,0)`. What's the key you heap on, and is it a min- or max-heap of size k?
4. *Find Median from Data Stream:* implement `addNum` and `findMedian` with two heaps. How do you keep them balanced?
5. Explain why "k largest" uses a *min*-heap of size k rather than a max-heap.

*Write your answers in [dsa-chapter-10-tryit.md](code/dsa-chapter-10-tryit.md).*

---

## The bumper sticker

> *A heap keeps only the single most extreme element ready — `O(1)` to peek, `O(log n)` to update. For top-k, merge-k, or a streaming median, it does just enough ordering instead of sorting everything: `O(n log k)` beats `O(n log n)`.*

That closes Part 2 — the core structures. You now know which structure makes which operation cheap. Part 3 steps up to the hardest and highest-value territory: graphs, recursion and backtracking, dynamic programming, and the interview ritual that ties it all together.

---

<div align="right">

[Chapter 11 →](dsa-chapter-11.md)

</div>
