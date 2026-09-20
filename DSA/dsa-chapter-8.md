# Chapter 8: When pointers branch — trees and traversal

*[← Chapter 7](dsa-chapter-7.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

A linked list node points to one next node. A **tree** node points to *several* children. That one change — branching instead of chaining — unlocks hierarchy: file systems, org charts, the DOM, decision trees, parse trees. And it makes a new question central: *in what order do you visit the nodes?*

Most tree problems are one of two things: **a traversal with a small twist**, or **recursion where each node asks its children a question.** This chapter gives you both reflexes.

---

## The structure

> 💡 **Concept notes — binary tree vocabulary**
> A **binary tree** node has a value and up to two children, `left` and `right`. The top is the **root**; nodes with no children are **leaves**. **Depth** of a node = edges from the root to it; **height** of the tree = the longest root-to-leaf path. A tree with `n` nodes that's **balanced** has height `~log n`; a degenerate one (every node has a single child) has height `n` — it's basically a linked list. Many tree operations are `O(height)`, so balance is what keeps them fast.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

---

## The three depth-first orders

Depth-first traversal goes as deep as possible before backing up. The *only* difference between the three orders is **when you visit the current node** relative to its children:

```python
def preorder(node, result):   # NODE, then left, then right
    if not node: return
    result.append(node.val)   # visit BEFORE children
    preorder(node.left, result)
    preorder(node.right, result)

def inorder(node, result):    # left, NODE, right
    if not node: return
    inorder(node.left, result)
    result.append(node.val)   # visit BETWEEN children
    inorder(node.right, result)

def postorder(node, result):  # left, right, NODE
    if not node: return
    postorder(node.left, result)
    postorder(node.right, result)
    result.append(node.val)   # visit AFTER children
```

> 💡 **Concept notes — which order, and why it matters**
> - **Preorder** (node first): copy/serialize a tree, or process a parent before its children (e.g., building paths from the root down).
> - **Inorder** (node in the middle): on a **binary search tree** (Chapter 9) this visits values in **sorted order** — a fact interviewers love to test.
> - **Postorder** (node last): when a node's answer *depends on its children's answers* — computing height, deleting a tree, evaluating an expression tree. "Ask the children first, then combine" = postorder.
> All three are `O(n)` time and `O(height)` space (the recursion stack).

---

## The recursion reflex: each node asks its children

The deepest pattern in tree problems: **a node computes its answer from its children's answers.** This is postorder thinking, and it solves a huge fraction of tree questions with four or five lines.

Take *maximum depth of a tree*. The brute force spells out the definition: find every root-to-leaf path, measure each, return the longest — which means building and storing all those paths (`O(n)` extra space) and re-walking the shared upper ancestors once per leaf. That repeated walk of the shared part is the waste. Postorder recursion deletes it: each node asks its two children for *their* depth and adds one, so every node is touched exactly once, `O(n)` time and `O(height)` stack space.

```python
def max_depth(root):
    if not root:
        return 0                                  # empty tree has depth 0
    return 1 + max(max_depth(root.left),          # ask both children their depth
                   max_depth(root.right))         # take the bigger, add yourself
```

Read it as a sentence: *"my depth is 1 plus the deeper of my two children's depths."* You don't track global state or manage a stack — you trust the recursion to answer for the subtrees and you just combine. This *trust the recursion* mindset is the single most important tree skill.

Now *is this tree height-balanced?* — every node's two subtrees differ in height by at most 1. The definition hands you a naive solution directly: at each node, measure the left height, measure the right height, confirm they differ by ≤ 1, and recurse into both children.

```python
def is_balanced_brute(root):
    def height(node):
        if not node:
            return 0
        return 1 + max(height(node.left), height(node.right))

    if not root:
        return True
    if abs(height(root.left) - height(root.right)) > 1:
        return False
    return is_balanced_brute(root.left) and is_balanced_brute(root.right)
```

Correct — but feel the waste. `height` walks an entire subtree, and then `is_balanced_brute` recurses *into* that same subtree and calls `height` all over again. Every node's height gets recomputed once for each ancestor above it: that's `O(n²)` on a skewed tree — the same "re-walking the shared upper part" waste we just deleted from `max_depth`.

The fix: compute the height and check balance in the *same* pass. Let the height helper return a sentinel `-1` the moment it finds an imbalance below, so one postorder walk does both jobs.

```python
def is_balanced(root):
    def height(node):
        if not node:
            return 0
        left_height = height(node.left)
        right_height = height(node.right)
        if left_height == -1 or right_height == -1 or abs(left_height - right_height) > 1:
            return -1                  # -1 signals "unbalanced somewhere below"
        return 1 + max(left_height, right_height)
    return height(root) != -1
```

The trick that bought back the time: the helper returns *both* a height *and* (via the `-1` sentinel) a validity flag, so the whole check is one `O(n)` postorder pass instead of recomputing heights from every ancestor.

> 💡 **Concept notes — the "define what the recursion returns" habit**
> Before writing a tree recursion, finish this sentence: *"`solve(node)` returns ____ for the subtree rooted at node."* Once that contract is crisp — "returns the height," "returns whether it's a valid BST and its min/max," "returns the sum" — the body almost writes itself: handle the empty case, recurse on children, combine. Most tree-recursion bugs come from a fuzzy or shifting contract.

---

## The other half: level-order (breadth-first)

Sometimes you need the tree **level by level** — "right side view," "level averages," "minimum depth," "zigzag order." That's **breadth-first search** using a queue: process a node, enqueue its children, and nodes come out in the order they went in (FIFO) — all of depth `d` before depth `d+1`.

A plain `list` *can* act as a queue — `append` to enqueue, `pop(0)` to dequeue the front — but `pop(0)` is a trap: removing the first element shifts every remaining one down a slot, so it costs `O(n)`. Do that once per node and an `O(n)` traversal quietly degrades to `O(n²)`. `collections.deque` (a double-ended queue) exists for exactly this: its `popleft()` is `O(1)`.

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    levels, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):      # snapshot THIS level's size
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        levels.append(level)             # one list per level
    return levels
```

`O(n)` time, `O(width)` space. The key idea: capture `len(queue)` *before* the inner loop so you process exactly one level per outer iteration, then enqueue the next level's nodes. This BFS-on-a-tree is the warm-up for graph BFS in Chapter 11.

> 💡 **Concept notes — DFS vs BFS on trees, the choice**
> Use **DFS (recursion)** when the answer is about *paths* or *subtree properties* — depth, sums, "does a root-to-leaf path exist," validity. Use **BFS (queue)** when the answer is about *levels* — shortest depth, per-level aggregates, anything "row by row." DFS naturally uses the call stack; BFS needs an explicit queue. Asking "is this about depth/paths or about levels?" picks the tool instantly.

---

## Recognizing tree problems

- **"Depth," "height," "diameter," "path sum," "is it balanced/symmetric"** → DFS recursion, combine children's answers (postorder).
- **"Level order," "right side view," "minimum depth," "zigzag"** → BFS with a queue.
- **"In sorted order," "kth smallest"** on a BST → inorder traversal (Chapter 9).
- **"Serialize / copy the tree"** → preorder.

> 💡 **Concept notes — edge cases to surface**
> Every tree recursion's base case *is* an edge case in disguise: `if not node: return` handles the **empty tree** and, at the bottom of the recursion, every **missing child**. Say it out loud anyway — plus the **single node** and a **completely skewed tree** (a straight chain, where `O(height)` stack space becomes `O(n)` and deep recursion can overflow). In Review, an empty root and a one-node tree are the two traces that catch most base-case bugs.

---

## Try it

1. *Invert a Binary Tree:* swap every node's left and right child. One line of recursion plus a base case — write it.
2. *Diameter of a Binary Tree:* the longest path between any two nodes. (Hint: at each node, the path *through* it is `leftHeight + rightHeight`; track a global max while returning height.)
3. *Binary Tree Right Side View:* the values visible from the right. BFS, and take the last node of each level — why the last?
4. *Validate a BST:* return whether a tree is a valid binary search tree. What contract should your recursion return so you can verify it in one pass?
5. State, in one sentence each, what `solve(node)` returns for: max depth, is-balanced, and diameter.

*Write your answers in [dsa-chapter-8-tryit.md](code/dsa-chapter-8-tryit.md).*

---

## The bumper sticker

> *Trees branch, so the question becomes "in what order?" DFS recursion lets each node combine its children's answers; BFS with a queue walks level by level. Define what your recursion returns, and the body writes itself.*

Next: a tree with a *rule* — the binary search tree, where ordering turns lookup into binary search, plus its string-loving cousin, the trie.

---

<div align="right">

[Chapter 9 →](dsa-chapter-9.md)

</div>
