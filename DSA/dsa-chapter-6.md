# Chapter 6: The structure that remembers the last thing

*[← Chapter 5](dsa-chapter-5.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

Part 1 was about *patterns* over arrays. Part 2 is about *structures* — and each structure earns its place by making one specific operation cheap. The stack's specialty: **"what was the most recent thing I haven't dealt with yet?"** Last in, first out.

That sounds trivial until you meet the **monotonic stack**, a variant that solves a whole class of "next greater / nearest smaller" problems in `O(n)` that look hopelessly `O(n²)` at first.

---

## The brute force and its waste

*For each element, find the **next greater element** to its right (or -1 if none).*

Brute force: for each element, scan rightward until you find something bigger.

```python
def next_greater_brute(nums):
    result = [-1] * len(nums)
    for current in range(len(nums)):
        for ahead in range(current + 1, len(nums)):
            if nums[ahead] > nums[current]:
                result[current] = nums[ahead]
                break
    return result
```

`O(n²)`. The waste is subtle. Consider `[2, 1, 5]`. For `2` we scan past `1` (not bigger) to `5`. For `1` we *also* scan to `5`. We rescanned `1`→`5`. Worse, elements we've already "passed over" because they were small get re-examined again and again. We keep re-walking the same descending runs.

---

## The move: a stack of "still waiting for a bigger number"

Keep a stack of elements that **haven't yet found their next-greater element.** Walk left to right. For each new element, it might be the answer for everyone on the stack smaller than it — so pop them and record it.

```python
def next_greater(nums):
    result = [-1] * len(nums)
    stack = []                              # holds INDICES still waiting
    for index in range(len(nums)):
        while stack and nums[index] > nums[stack[-1]]:
            waiting = stack.pop()           # nums[index] is this index's next greater
            result[waiting] = nums[index]
        stack.append(index)
    return result                           # anything left on the stack -> -1
```

Each index is pushed once and popped at most once, so it's **`O(n)`** total — even with the inner `while`. The stack "remembers" exactly the elements still searching for a bigger neighbor, in decreasing order, so a new big element resolves all of them at once.

> 💡 **Concept notes — what makes a stack "monotonic"**
> A **monotonic stack** keeps its elements in sorted order (here, decreasing). When a new element would break the order, you *pop* until order is restored — and each pop is a problem getting solved (here, "found j's next greater"). The magic is amortized `O(n)`: every element is pushed and popped exactly once, so the total pop work across the whole run is `n`, no matter how the `while` loops nest. This is the same amortized-counting trick as the sliding window in Chapter 4.

> 💡 **Concept notes — stack basics (the ADT)**
> A **stack** supports `push` (add to top), `pop` (remove from top), and `peek` (look at top) — all `O(1)`. It's **LIFO**: last in, first out, like a stack of plates. In Python a plain `list` is a stack: `append` to push, `pop()` to pop, `[-1]` to peek. Use a stack whenever the thing you need next is always the *most recent* unresolved item — matching brackets, undo history, call frames, backtracking.

---

## The bread-and-butter stack problem: matching brackets

*Is a string of brackets `()[]{}` valid?* Every closing bracket must match the **most recent** unmatched opening one — pure LIFO.

The primitive attempt: an adjacent matched pair like `()` is always safe to delete, so keep collapsing pairs until the string stops shrinking. If nothing's left, it was valid.

```python
def is_valid_naive(brackets):
    while "()" in brackets or "[]" in brackets or "{}" in brackets:
        brackets = brackets.replace("()", "").replace("[]", "").replace("{}", "")
    return brackets == ""                       # nothing left over => balanced
```

It works, but feel the waste: every `replace` re-scans the whole string, and we loop until nothing changes — `O(n²)` or worse, re-reading characters we already resolved. All we really need is to remember the *most recent* unclosed opener and match each closer against it in one pass. "Most recent unresolved thing" is precisely a stack.

```python
def is_valid(brackets):
    closer_to_opener = {")": "(", "]": "[", "}": "{"}
    stack = []
    for bracket in brackets:
        if bracket in closer_to_opener.values():    # an opening bracket
            stack.append(bracket)
        elif bracket in closer_to_opener:           # a closing bracket
            if not stack or stack.pop() != closer_to_opener[bracket]:
                return False                # nothing to match, or wrong match
    return not stack                        # valid only if nothing left over
```

`O(n)`. The stack naturally enforces "close the most recently opened bracket first" — try doing this *without* a stack and you'll reinvent one.

Two edge cases hide in that one condition. `not stack` catches a **closing bracket that arrives with nothing open** (`)(` — without the check, `stack.pop()` crashes on an empty list), and the final `return not stack` catches the opposite: **openers left unclosed** (`(((`). Add the **empty string** (trivially valid) and you have the three inputs to say out loud in Understand.

---

## When recursion is secretly a stack

Every recursive function uses the **call stack** — the runtime pushes a frame for each call and pops it on return. So any recursion can be rewritten with an explicit stack, which matters when deep recursion would overflow. Here we make that hidden call stack *visible*.

Start with the case that mirrors the call stack most directly: **preorder** (visit the node, then its left subtree, then its right). Pop a node, visit it right away, then push its children so the left one comes off next:

```python
def preorder_iterative(root):               # visit node, then left subtree, then right
    if root is None:
        return []
    result = []
    stack = [root]
    while stack:
        node = stack.pop()
        result.append(node.val)             # visit the moment we pop — no waiting
        if node.right:                      # push right first so left pops first
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return result
```

That's the whole idea: the stack *is* the pile of "calls" still waiting. **Inorder** (left, node, right) is trickier, because now you must visit the left subtree *before* the node — so you can't visit on pop. Instead you dive left pushing every node as you go, then visit on the way back up:

```python
def inorder_iterative(root):                # tree traversal without recursion
    result = []
    stack = []
    node = root
    while stack or node:
        while node:                         # go left as far as possible
            stack.append(node)
            node = node.left
        node = stack.pop()                  # backtrack to most recent unvisited
        result.append(node.val)
        node = node.right                   # then go right
    return result
```

We'll lean on this in Chapter 8 (tree traversals) and Chapter 11 (DFS). The takeaway: **DFS, backtracking, and recursion are all "stack" in disguise.**

---

## Recognizing a stack problem

- You need the **most recently seen** unresolved item → plain stack.
- **Matching / nesting / balancing** (brackets, tags, expressions).
- **"Next greater," "next smaller," "nearest larger to the left,"** "largest rectangle," "daily temperatures," "stock span" → **monotonic stack.**
- You're **undoing** or **backtracking** to the last decision point.

> 💡 **Concept notes — monotonic stack direction & order**
> Two choices define a monotonic-stack solution: (1) **traversal direction** — left-to-right finds "next" relationships, right-to-left finds "previous" ones; (2) **stack order** — a decreasing stack finds *greater* neighbors, an increasing stack finds *smaller* neighbors. Pick by what the problem asks. "Next greater to the right" → left-to-right, decreasing stack (as above). Practicing two or three of these until the direction/order choice is automatic covers a surprising slice of medium interview questions.

> 💡 **Concept notes — edge cases to surface**
> For stack problems, name what happens at the boundaries: an **empty input** (usually a trivial yes/valid), a **pop from an empty stack** (an unmatched closer — guard it or you crash), and **items left on the stack at the end** (unclosed openers, an unfinished job). In Review, trace one input that under-flows (`)`) and one that over-fills (`(((`) — the two ways balance can fail.

---

## Try it

1. *Daily Temperatures:* for each day, how many days until a warmer temperature? (Monotonic stack of indices — what order?)
2. *Min Stack:* design a stack that also returns its minimum in `O(1)`. (Hint: a second stack tracking the running min.)
3. *Largest Rectangle in Histogram:* the hard but classic monotonic-stack problem — find the largest rectangle. What does each pop compute?
4. Explain, with amortized counting, why the monotonic-stack `next_greater` is `O(n)` despite the nested `while`.
5. Rewrite a simple recursive factorial using an explicit stack. What does each stack frame hold?

*Write your answers in [dsa-chapter-6-tryit.md](code/dsa-chapter-6-tryit.md).*

---

## The bumper sticker

> *A stack remembers the most recent unresolved thing. Make it monotonic and each new element resolves everyone it dominates — turning `O(n²)` "next greater/smaller" scans into `O(n)`, because every element is pushed and popped just once.*

Next: a structure with no indices at all, where the only way forward is to follow a pointer — the linked list, and the slow/fast trick that tames it.

---

<div align="right">

[Chapter 7 →](dsa-chapter-7.md)

</div>
