# Chapter 9: Trees with rules — BST and trie

*[← Chapter 8](dsa-chapter-8.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

A plain tree just branches. Add a *rule* about how values are arranged, and the tree becomes a search engine. This chapter covers two such ruled trees: the **binary search tree** (ordering turns lookup into binary search) and the **trie** (sharing prefixes turns word lookup into a walk down characters).

Both exist for the same reason: the rule makes one operation — *finding things* — dramatically faster.

---

## The binary search tree (BST)

> 💡 **Concept notes — the BST rule**
> A **binary search tree** obeys one invariant at *every* node: all values in its **left** subtree are smaller, all values in its **right** subtree are larger. That single rule means searching is just binary search (Chapter 5) walking down the tree — at each node you go left or right, halving the remaining nodes. Lookup, insert, and delete are all **`O(height)`**: `O(log n)` if the tree is balanced, but `O(n)` if it's degenerate (inserting sorted data builds a straight line).

```python
def search_bst(root, target):
    node = root
    while node:
        if target == node.val:
            return node
        node = node.left if target < node.val else node.right   # discard half
    return None
```

That `node.left if target < node.val else node.right` *is* binary search — the BST structure encodes the "throw away half" decision. Compare to scanning an unsorted tree (`O(n)`): the rule buys us `O(log n)`.

```python
def insert_bst(root, value):
    if not root:
        return TreeNode(value)                    # found the empty spot
    if value < root.val:
        root.left = insert_bst(root.left, value)
    else:
        root.right = insert_bst(root.right, value)
    return root
```

> 💡 **Concept notes — inorder on a BST gives sorted order**
> Because left < node < right everywhere, an **inorder** traversal (left, node, right — Chapter 8) of a BST visits values in **ascending sorted order.** This is why "kth smallest element in a BST" is just "stop the inorder traversal after k visits" — `O(height + k)`, no full sort needed. Any "in sorted order" or "kth smallest/largest" question on a BST is an inorder-traversal problem in disguise.

The simplest read of that idea: walk the whole tree inorder, collect every value into a list — which comes out already sorted — and index it.

```python
def kth_smallest_collect(root, k):
    values = []
    def inorder(node):
        if not node:
            return
        inorder(node.left)
        values.append(node.val)        # visits values in ascending order
        inorder(node.right)
    inorder(root)
    return values[k - 1]               # kth smallest sits at index k-1
```

Correct and easy to read — `O(n)` time, `O(n)` space. But notice we build the *entire* sorted list even when `k` is 1: a million-node tree and we want the 3rd smallest, yet we visited all million. Everything past the kth value is wasted work.

Stop early. An *iterative* inorder lets us pull values one at a time and quit the instant we've popped `k` of them:

```python
def kth_smallest(root, k):
    stack, node = [], root
    while stack or node:
        while node:                    # go left as far as possible
            stack.append(node)
            node = node.left
        node = stack.pop()             # smallest unvisited
        k -= 1
        if k == 0:
            return node.val
        node = node.right
    return None
```

Now it's `O(height + k)` time — we touch only the leftmost path plus the first `k` nodes, not the whole tree — and `O(height)` space for the stack. We managed the stack by hand (instead of leaning on recursion and a full list) precisely to buy that early exit.

> 💡 **Concept notes — the balance problem and why we mention it**
> A BST is only `O(log n)` if it stays **balanced.** Insert already-sorted data into a naive BST and you get a height-`n` chain — `O(n)` operations, no better than a list. **Self-balancing** trees (red-black trees, AVL trees) rotate nodes on insert/delete to keep height `~log n`. You rarely implement these in an interview, but you should *name the problem*: "a plain BST degrades to `O(n)` on sorted input; production uses a self-balancing variant like a red-black tree." Python's `dict`/`set` use hashing instead (Chapter 2); ordered structures like C++ `std::map` or Java `TreeMap` use balanced BSTs.

---

## The trie (prefix tree)

Now a different rule: arrange **strings by shared prefix.** A **trie** stores words as paths down a tree of characters, so all words starting with "ca" share the same first two nodes. This makes prefix queries — autocomplete, spell-check, "does any word start with...?" — extremely fast.

> 💡 **Concept notes — what a trie buys you**
> In a **trie**, each node represents one character; a path from the root spells a prefix, and nodes flagged as word-ends mark complete words. Searching for a word of length `L` is **`O(L)`** — independent of how many words are stored. Checking "is `pre` a prefix of any word?" is also `O(L)`. A hash set can answer "is this exact word present?" in `O(L)` too, but it *cannot* efficiently answer **prefix** questions — that's the trie's unique power. Cost: memory, since each character is a node.

```python
class TrieNode:
    def __init__(self):
        self.children = {}              # char -> TrieNode
        self.is_word = False            # does a word end here?

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True             # mark the final node as a word-end

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_word

    def starts_with(self, prefix):
        return self._walk(prefix) is not None   # prefix exists if path exists

    def _walk(self, text):
        node = self.root
        for char in text:
            if char not in node.children:
                return None             # path breaks -> not present
            node = node.children[char]
        return node
```

`insert`, `search`, and `starts_with` are all `O(L)` in the length of the string. The shared-prefix structure is also what makes a trie the backbone of autocomplete and of word-search puzzles (combine a trie with the DFS of Chapter 11).

---

## Recognizing BST and trie problems

- **"Search/insert/delete in a BST," "kth smallest," "validate BST," "in-order successor," "range queries"** → BST operations; remember inorder = sorted.
- **"Sorted input building a tree," "why is my BST slow"** → balance; name self-balancing trees.
- **"Autocomplete," "prefix," "starts with," "search words with wildcards," "word dictionary"** → trie.
- **"Word search on a grid," "longest word built from others"** → trie + DFS/backtracking.

> 💡 **Concept notes — edge cases to surface**
> For BST and trie work, surface the boundaries before coding: an **empty tree** (insert into it returns a fresh node; search returns not-found), a **`k` larger than the node count** in "kth smallest" (the inorder walk runs out — `kth_smallest` returns `None`), searching an **absent key**, and the **empty string** in a trie (is the root itself a word?). In Review, insert into an empty tree and query `k` at both ends of its range.

---

## Try it

1. *Validate Binary Search Tree:* verify the BST rule holds everywhere. (Hint: pass down a valid `(low, high)` range; a node must fall inside it. Why isn't checking only immediate children enough?)
2. *Kth Smallest Element in a BST:* you've seen the iterative inorder above — explain why it stops in `O(height + k)`.
3. *Implement Trie (Insert/Search/StartsWith):* you have the template above — what's the difference between `search` and `starts_with`?
4. *Design Add and Search Words (with `.` wildcard):* support searching where `.` matches any character. Which traversal handles the wildcard branch?
5. Explain why a hash set can answer "exact word present?" but not "any word with this prefix?", and how a trie does both.

*Write your answers in [dsa-chapter-9-tryit.md](code/dsa-chapter-9-tryit.md).*

---

## The bumper sticker

> *Give a tree a rule and it becomes a search engine: BST ordering makes lookup binary search (`O(log n)` when balanced); trie prefixes make word and prefix lookup `O(L)`. Inorder on a BST is sorted order — remember that one.*

Next: a tree-shaped structure that doesn't sort everything, just keeps the single most extreme element on top — the heap.

---

<div align="right">

[Chapter 10 →](dsa-chapter-10.md)

</div>
