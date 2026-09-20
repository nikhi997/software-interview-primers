# Chapter 7: Following pointers, two at a time

*[← Chapter 6](dsa-chapter-6.md) · [Contents](dsa-README.md)*

- [ ] **Mark as read**

Arrays give you `O(1)` access to any index. Linked lists give that up — to reach the 5th node you must walk through the first four. In exchange they give `O(1)` insertion and deletion *anywhere you already are*, without shifting everything over.

Most linked-list interview questions aren't really about the list — they're about a single elegant trick: **two pointers moving at different speeds.** Master that and the whole category collapses into a few templates.

---

## The structure, briefly

> 💡 **Concept notes — what a linked list is**
> A **linked list** is a chain of nodes; each node holds a value and a pointer (`next`) to the following node. There's no index — you start at the `head` and follow `next` until you hit `None`. Insertion/deletion is `O(1)` *if you have a pointer to the spot* (just rewire `next`), but **access by position is `O(n)`** (you must walk there). Compare arrays: `O(1)` access, but `O(n)` insertion in the middle (shifting). The trade is access-speed for insertion-speed.

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

---

## The first template: reversing a list

*Reverse a singly linked list.* The brute-force temptation is to copy values into an array, reverse, rebuild — `O(n)` space. The waste: we don't need a copy, we just need to **flip each `next` pointer** as we walk.

```python
def reverse_list(head):
    previous = None
    current = head
    while current:
        next_node = current.next    # remember where we were going
        current.next = previous     # flip the pointer backward
        previous = current          # advance previous
        current = next_node         # advance current
    return previous                 # new head is the old tail
```

`O(n)` time, `O(1)` space. The only trick is saving `next_node` *before* you overwrite `current.next`, or you lose the rest of the list. This three-pointer shuffle (`previous`, `current`, `next_node`) is worth burning into muscle memory — it shows up inside dozens of harder problems.

> 💡 **Concept notes — draw the pointers**
> Linked-list bugs are almost always "I overwrote a pointer before saving it" or "I returned the wrong end." The fix isn't cleverness, it's **drawing the nodes and arrows** on paper and stepping through 3–4 nodes by hand. Interviewers *expect* you to draw. Track exactly which node each variable points to after each line.

---

## The big idea: slow and fast pointers

Here's the trick that powers most linked-list problems. Run **two pointers at different speeds.** When `fast` moves twice as fast as `slow`, two beautiful things fall out for free:

**1. Finding the middle.** When `fast` reaches the end, `slow` is exactly halfway.

```python
def middle_node(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next            # 1 step
        fast = fast.next.next       # 2 steps
    return slow                     # the middle when fast falls off the end
```

**2. Detecting a cycle.** How do you even *know* a list loops forever? The obvious way first: walk it, and remember every node you step on. The moment you land on one you've already seen, there's a loop.

```python
def has_cycle_with_set(head):
    seen = set()
    node = head
    while node:
        if node in seen:            # been here before -> there's a loop
            return True
        seen.add(node)
        node = node.next
    return False                    # walked off the end -> no loop
```

Correct and dead simple, `O(n)` time. The cost, said out loud: an `O(n)` `set` holding every node we touch. Now buy that memory back.

**The trick (Floyd's algorithm).** Run slow/fast instead. If the list loops, the fast pointer eventually *laps* the slow one and they collide; if there's no cycle, fast just reaches the end — and we never remember a single node.

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:            # they met -> there's a loop
            return True
    return False                    # fast reached the end -> no loop
```

Same `O(n)` time, but `O(1)` space — we traded the visited-set for a second pointer. Slow/fast detects the cycle with *no extra memory at all*.

> 💡 **Concept notes — why the fast pointer always catches the slow one**
> If there's a cycle, once both pointers are inside the loop, the fast pointer gains *one step* on the slow pointer every iteration. The gap shrinks by 1 each time, so it must eventually hit 0 — they collide. It can't "jump over" because the gap changes by exactly 1 per step. This is why fast moves by *2*, not 3 or more: a step-2 gap of 1 closes cleanly. (A neat extension — Floyd's — even finds *where* the cycle starts by resetting one pointer to the head after they meet.)

---

## The other workhorse: the dummy head

Many list problems break at the boundary — "what if we delete the *head*?" The fix is a **dummy node** placed before the head, so the head is no longer a special case.

Take "remove the `n`th node from the end." You can't count from the end, so the obvious way is to count from the front: walk once to measure the length, then walk again to the node just before position `length - n` and unlink it. A dummy in front means deleting the head needs no special branch.

```python
def remove_nth_from_end_two_pass(head, n):
    dummy = ListNode(0, head)           # sentinel before head
    length = 0
    node = head
    while node:                         # first pass: measure the list
        length += 1
        node = node.next
    before_target = dummy
    for _ in range(length - n):         # second pass: stop just before the target
        before_target = before_target.next
    before_target.next = before_target.next.next
    return dummy.next
```

Two passes, `O(n)` time — clear and correct. But we walk the whole list twice. Can we find the node in a *single* pass, without knowing the length up front?

Yes — launch a `fast` pointer `n` nodes ahead of `slow`, then move both together. When `fast` falls off the end, `slow` sits exactly `n` from the end:

```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)           # sentinel before head
    slow = fast = dummy
    for _ in range(n):                  # open a gap of n between the pointers
        fast = fast.next
    while fast.next:                    # advance both until fast is at the end
        slow = slow.next
        fast = fast.next
    slow.next = slow.next.next          # slow is just before the target; unlink
    return dummy.next                   # head may have changed -> return dummy.next
```

The trick that replaced the length count: a **gap of `n`** between the pointers does the measuring for you, so one pass suffices — you touch each node once instead of twice. The **dummy** carries over unchanged: deleting the head still needs no special branch, and returning `dummy.next` always gives the correct (possibly new) head.

> 💡 **Concept notes — when to reach for a dummy head**
> Use a dummy/sentinel node whenever the head node might be **inserted, deleted, or changed** — merging two lists, removing elements, partitioning. It absorbs the edge case so your main loop has no "is this the head?" branch. Returning `dummy.next` at the end always yields the real head. It's the single highest-leverage trick for clean linked-list code.

---

## Recognizing a linked-list problem (and the tool)

- **"Find the middle," "detect a cycle," "find the cycle start," "is it a palindrome"** → slow/fast pointers.
- **"Reverse," "reverse in groups," "swap pairs"** → the `previous/current/next_node` flip template.
- **"Remove," "merge," "partition,"** anything that might touch the head → **dummy node.**
- **"Nth from the end"** → two pointers with a fixed gap.

> 💡 **Concept notes — edge cases to surface**
> Linked-list bugs almost always live at the ends, so surface them first: an **empty list** (`head is None`), a **single node**, **deleting or changing the head** (the reason the dummy node exists — it absorbs this so the main loop has no special branch), and **`n` equal to the list length** (removing the very first node). In Review, run the code on a one- and two-node list by hand — the cases where slow/fast pointers barely have room to move.

---

## Try it

1. *Linked List Cycle II:* return the node where the cycle begins (not just whether one exists). Look up Floyd's two-phase method and reason through why phase two works.
2. *Merge Two Sorted Lists:* merge two sorted lists into one. Use a dummy head — why does it simplify the code?
3. *Palindrome Linked List:* check if a list reads the same forwards and backwards in `O(1)` space. (Hint: find the middle, reverse the second half, compare.)
4. *Reverse Nodes in k-Group:* reverse every consecutive group of `k` nodes. Which two templates does this combine?
5. Why does the fast pointer move exactly 2 steps for cycle detection, rather than 3? What could go wrong with a larger stride?

*Write your answers in [dsa-chapter-7-tryit.md](code/dsa-chapter-7-tryit.md).*

---

## The bumper sticker

> *Linked lists trade index access for cheap rewiring. Two pointers at different speeds find the middle and detect cycles with `O(1)` space, and a dummy head deletes every "what if it's the head?" edge case.*

Next: pointers that branch in two directions instead of one — trees, and the three traversal orders you'll use forever.

---

<div align="right">

[Chapter 8 →](dsa-chapter-8.md)

</div>
