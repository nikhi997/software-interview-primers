# DSA Mixed Cold Drills: timed retrieval workbook

*[← Chapter 15](dsa-chapter-15.md) · [Contents](dsa-README.md)*

This workbook is for cold retrieval, not reading. The chapters teach, the appendix looks up, the waste map diagnoses, and these drills make you perform the whole move under a clock. None of the problems below announces its target pattern in the prompt. Your job is to earn the pattern from the brute force.

Start these after Chapter 5. Use them heavily after Chapter 15. They do **not** replace problem reps from the appendix; they train the decision muscle between reps.

---

## Rules for every packet

Each packet has three problems and should take **30–35 minutes total**:

- 2 minutes: skim all three and choose an order.
- 9–10 minutes per problem: run the full ritual and code.
- 3 minutes: postmortem the packet.

For **each problem**, submit these fields in your notes or editor:

1. Clarification questions and assumptions.
2. Brute force.
3. Brute-force Big-O.
4. The exact waste.
5. Candidate approaches you considered, including why you rejected at least one.
6. The invariant your chosen approach maintains.
7. Code.
8. A hand trace on the given trace target.
9. Final time and space complexity.
10. Postmortem: recognition error / implementation error / missed edge case / next review date.

Do not open the hints until the checkpoint time. The hints are nudges, not solutions; if you need a full editorial, mark the problem for outside practice and re-solve it tomorrow.

---

## Packet 1 — Same words, different shape

**Timebox:** 32 minutes. Open first hints only after minute 12; second hints only after minute 22.

### 1A. Quiet sensor stretch

A sensor stream is a list of integers. Return the length of the longest **contiguous** stretch where no value appears more than twice. Values can be negative. Empty stream returns `0`.

- Constraints: `n` up to 100,000.
- Trace target: `[5, 1, 5, 2, 5, 1, 1, 3]`.
- Watch for: the third copy of a value, and whether removing one left value is always enough.

<details>
<summary>Hint after minute 12</summary>

Your state should describe only the current stretch, not the whole prefix.

</details>

<details>
<summary>Hint after minute 22</summary>

When a value count becomes illegal, move the left boundary until the state is legal again. Your invariant is about every count inside the current stretch.

</details>

### 1B. Signal subsequence cleanup

Given a list of signal strengths, return the length of the longest sequence you can keep in original order, not necessarily adjacent, where every kept value is strictly larger than the previous kept value.

- Constraints: `n` up to 2,000 for the first pass.
- Trace target: `[4, 2, 3, 1, 5]`.
- Watch for: confusing "kept in order" with "kept next to each other."

<details>
<summary>Hint after minute 12</summary>

A moving boundary over a contiguous stretch cannot skip the `4` and keep `2, 3, 5`.

</details>

<details>
<summary>Hint after minute 22</summary>

Define a state like "best answer ending at this position" and build it from earlier compatible positions.

</details>

### 1C. Exact-size energy block

You have hourly energy deltas and an integer `k`. Return the maximum total over exactly `k` consecutive hours. If there are fewer than `k` hours, return `None`.

- Constraints: `n` up to 100,000.
- Trace target: `[3, -2, 4, -1, 2]`, `k = 3`.
- Watch for: all-negative input and `k == len(values)`.

<details>
<summary>Hint after minute 12</summary>

Two neighboring candidates share almost everything.

</details>

<details>
<summary>Hint after minute 22</summary>

After the first block, each move has one entering value and one leaving value. State the equality your running total must maintain.

</details>

---

## Packet 2 — Pairs, positions, and sortedness

**Timebox:** 33 minutes. This packet is a contrast pair plus a curveball: do not reuse an approach unless the requirements still justify it.

### 2A. Catalog prices, shelf already sorted

A sorted list of product prices is printed on a shelf label. Return `True` if two different prices add to a target. You do not need indices.

- Constraints: `n` up to 1,000,000; extra memory should be constant.
- Trace target: prices `[2, 4, 7, 11, 15]`, target `18`.
- Watch for: duplicate prices and using the same element twice.

<details>
<summary>Hint after minute 12</summary>

The sorted order lets one comparison rule out many pairs, not just the current pair.

</details>

<details>
<summary>Hint after minute 22</summary>

When the sum is too small, explain why moving the larger side cannot help. When too large, explain the opposite.

</details>

### 2B. Receipt lines, original positions required

An unsorted list of receipt line amounts is given. Return the two original indices whose values add to the target, or `[]` if none exists.

- Constraints: `n` up to 100,000; values may repeat.
- Trace target: `[8, 3, 4, 3]`, target `6`.
- Watch for: the answer uses two equal values at different positions.

<details>
<summary>Hint after minute 12</summary>

Sorting would disturb the thing the output asks you to return unless you carry extra bookkeeping.

</details>

<details>
<summary>Hint after minute 22</summary>

While scanning once, ask what value would complete the current value, and what you need to remember about previous values.

</details>

### 2C. Badge pairs within a gap

A hallway log records badge IDs in order of entry. Return `True` if the same badge appears twice with at most `gap` entries between them.

- Constraints: `n` up to 100,000.
- Trace target: badges `[9, 1, 2, 9, 3, 1]`, `gap = 2` and then `gap = 3`.
- Watch for: whether old sightings should still count.

<details>
<summary>Hint after minute 12</summary>

Remembering every old badge is safe for duplicate detection, but it may be too permissive for the distance rule.

</details>

<details>
<summary>Hint after minute 22</summary>

Either remember the latest index for each badge, or maintain only the last `gap` badges as the active set.

</details>

---

## Packet 3 — Fewest steps is not always cheapest

**Timebox:** 35 minutes. Say out loud whether every move costs the same before you choose a traversal.

### 3A. Office maze steps

A floor plan grid contains `S`, `T`, `.`, and `#`. From `S`, move four directions through `.` cells to reach `T`. Return the fewest number of moves, or `-1`.

- Constraints: up to 300 by 300.
- Trace target:
  - row 0: `S..#`
  - row 1: `.##.`
  - row 2: `...T`
- Watch for: marking a cell too late and enqueuing it many times.

<details>
<summary>Hint after minute 12</summary>

The first time you remove a cell at distance `d`, every route with fewer than `d` moves has already had its chance.

</details>

<details>
<summary>Hint after minute 22</summary>

Store the distance with the cell, or process the queue level by level. Mark visited before adding to the queue.

</details>

### 3B. Delivery grid with tolls

A grid contains non-negative tolls for entering each cell. From the top-left cell, reach the bottom-right cell with minimum total toll. You may move four directions.

- Constraints: up to 200 by 200.
- Trace target: `[[1, 9, 1], [1, 9, 1], [1, 1, 1]]`.
- Watch for: the route with more steps can be cheaper.

<details>
<summary>Hint after minute 12</summary>

A plain first-arrival rule only works when each edge has the same cost.

</details>

<details>
<summary>Hint after minute 22</summary>

Always expand the not-yet-final cell with the cheapest known total. Non-negative costs are the rule that makes finalization safe.

</details>

### 3C. Regions behind fences

A grid contains land `1` and water `0`. Return the size of the largest connected land region using four-direction adjacency. You may mutate the grid.

- Constraints: up to 500 by 500.
- Trace target:
  - row 0: `11000`
  - row 1: `01011`
  - row 2: `00011`
- Watch for: counting the same land twice from two starting cells.

<details>
<summary>Hint after minute 12</summary>

The key is not distance; it is making sure each land cell joins exactly one counted region.

</details>

<details>
<summary>Hint after minute 22</summary>

When you start from fresh land, consume the whole connected region and return its size. Mutating land to water is one way to record visited.

</details>

---

## Packet 4 — The largest few, now or later

**Timebox:** 32 minutes. Watch the output timing: once at the end is different from after every update.

### 4A. Batch leaderboard cut

Given final scores and `k`, return any `k` highest scores. The returned `k` scores do not need to be sorted.

- Constraints: `n` up to 5,000,000; `k` up to 50.
- Trace target: scores `[10, 4, 8, 20, 2, 15]`, `k = 3`.
- Watch for: accidentally sorting millions of discarded scores.

<details>
<summary>Hint after minute 12</summary>

The structure should never need to hold more than the answer size.

</details>

<details>
<summary>Hint after minute 22</summary>

Keep the current winners, and make the easiest-to-evict winner sit at the top.

</details>

### 4B. Live median board

Numbers arrive one at a time. After each insertion, return the median of all numbers seen so far.

- Constraints: up to 100,000 insertions.
- Trace target: insert `5, 2, 10, 4` and report after each insert.
- Watch for: a single top-k structure cannot see both sides of the middle.

<details>
<summary>Hint after minute 12</summary>

You need fast access to the largest value on the low side and the smallest value on the high side.

</details>

<details>
<summary>Hint after minute 22</summary>

Maintain two balanced halves. State both invariants: size balance and ordering between halves.

</details>

### 4C. Frequent error codes

Given a finished log of error codes, return the `k` most frequent codes. Ties may be returned in any order.

- Constraints: `n` up to 1,000,000; number of distinct codes may be much smaller than `n`.
- Trace target: `['A', 'B', 'A', 'C', 'B', 'A']`, `k = 2`.
- Watch for: heaping raw events instead of summarized counts.

<details>
<summary>Hint after minute 12</summary>

First compress repeated events into the information you actually rank.

</details>

<details>
<summary>Hint after minute 22</summary>

There are two phases: count, then keep only the best `k` count records.

</details>

---

## Packet 5 — Waiting things and changing readiness

**Timebox:** 34 minutes. Two of these involve unresolved items; only one is about the most recent unresolved item.

### 5A. Warranty after a higher price

For each day's price, return how many days until a higher price appears. If none appears, return `0`.

- Constraints: `n` up to 100,000.
- Trace target: `[7, 3, 4, 2, 8]`.
- Watch for: the day with price `8` resolving several earlier days at once.

<details>
<summary>Hint after minute 12</summary>

Keep only days that are still waiting for an answer.

</details>

<details>
<summary>Hint after minute 22</summary>

When a new price arrives, it resolves the most recent lower waiting prices first. Count pushes and pops, not nested loops.

</details>

### 5B. Assembly prerequisites

There are `n` modules and dependency pairs `(before, after)`. Return one build order, or `[]` if no order exists.

- Constraints: `n` up to 100,000; dependencies up to 300,000.
- Trace target: `n = 4`, pairs `(0, 2), (1, 2), (2, 3)`.
- Watch for: a cycle that leaves no module ready.

<details>
<summary>Hint after minute 12</summary>

A module's readiness changes only when one of its prerequisites is completed.

</details>

<details>
<summary>Hint after minute 22</summary>

Track the remaining prerequisite count for each module and queue modules whose count becomes zero.

</details>

### 5C. Browser tag checker

Given a stream of opening and closing tags like `<a>`, `<b>`, `</b>`, return whether every closer matches the most recent unmatched opener.

- Constraints: up to 100,000 tags.
- Trace target: `<a> <b> </b> <c> </a> </c>`.
- Watch for: a closer that matches some opener, but not the most recent one.

<details>
<summary>Hint after minute 12</summary>

The word "most recent" is doing real work.

</details>

<details>
<summary>Hint after minute 22</summary>

Push openers; on a closer, the only legal match is the top unresolved opener.

</details>

---

## Packet 6 — Connectivity is not always a path

**Timebox:** 35 minutes. Decide whether the output asks for a route, a count, or only sameness of group.

### 6A. Merging customer profiles

You receive pairs of profile IDs believed to be the same person. After processing all pairs, return how many distinct people remain.

- Constraints: profiles numbered `0..n-1`, pairs up to 500,000.
- Trace target: `n = 6`, pairs `(0,1), (2,3), (1,2), (4,5)`.
- Watch for: merging two profiles already in the same group.

<details>
<summary>Hint after minute 12</summary>

You do not need the path between profiles; you need a representative for each group.

</details>

<details>
<summary>Hint after minute 22</summary>

Each successful merge reduces the group count by one. Make repeated representative lookups cheap.

</details>

### 6B. Route with actual handoff list

Given an undirected graph of teams and handoff links, return one actual path from team `start` to team `target`, or `[]`.

- Constraints: up to 100,000 nodes and 300,000 edges.
- Trace target: edges `(A,B), (A,C), (C,D), (B,D)`, path `A` to `D`.
- Watch for: a group-membership answer is not enough.

<details>
<summary>Hint after minute 12</summary>

A yes/no connected answer loses the predecessor information needed to reconstruct the route.

</details>

<details>
<summary>Hint after minute 22</summary>

Traverse once, record how each node was first reached, then walk predecessors backward from target.

</details>

### 6C. Conflicting dependency claims

A directed graph of claims says `A` must happen before `B`. Return `True` if all claims can be satisfied; return `False` if they contradict each other.

- Constraints: up to 100,000 nodes.
- Trace target: `(0,1), (1,2), (2,0)`.
- Watch for: treating directed dependencies like undirected groups.

<details>
<summary>Hint after minute 12</summary>

The problem is not whether nodes are connected. Direction is the whole meaning.

</details>

<details>
<summary>Hint after minute 22</summary>

If you repeatedly remove nodes with no remaining blockers and cannot remove them all, what structure must be left?

</details>

---

## Packet 7 — Try choices or remember states?

**Timebox:** 35 minutes. The word "ways" is not enough; ask whether you must list them or count/optimize them.

### 7A. Door codes to list

Given digits `2` through `9`, return all possible letter strings using the phone-key mapping. Output every string.

- Constraints: at most 8 digits.
- Trace target: digits `23`.
- Watch for: mutating one partial string/list and accidentally recording the same final object repeatedly.

<details>
<summary>Hint after minute 12</summary>

The output itself may be exponential, so exponential exploration is expected.

</details>

<details>
<summary>Hint after minute 22</summary>

Build one partial candidate, choose a letter, explore the next digit, then undo or create a fresh candidate safely.

</details>

### 7B. Cheapest non-adjacent donations

A row of donation boxes has values. Pick boxes with maximum total value, but you cannot pick adjacent boxes.

- Constraints: up to 100,000 boxes.
- Trace target: `[2, 7, 9, 3, 1]`.
- Watch for: a recursion that re-solves the best answer from the same index many times.

<details>
<summary>Hint after minute 12</summary>

At each position, the two choices lead to suffixes you will see again from different paths.

</details>

<details>
<summary>Hint after minute 22</summary>

Define a state for the best total using boxes up to, or starting at, a position. Then see whether only the previous two states are needed.

</details>

### 7C. Word walk in a board

Given a board of letters and a word, return whether the word can be formed by moving four directions without reusing a cell in the same attempt.

- Constraints: board up to 12 by 12; word length up to 20.
- Trace target: board rows `ABCE`, `SFCS`, `ADEE`, word `ABCCED`.
- Watch for: forgetting to unmark a cell before trying a different path.

<details>
<summary>Hint after minute 12</summary>

The visited state is local to the current attempted word path, not global for the whole board.

</details>

<details>
<summary>Hint after minute 22</summary>

The shape is choose a neighbor, explore the next character, and un-choose the cell so another branch can use it.

</details>

---

## Packet 8 — Boundary, extreme, or repeated subproblem?

**Timebox:** 34 minutes. This packet is deliberately mixed; the constraints should veto at least one tempting idea per problem.

### 8A. Smallest truck limit

Packages must be shipped in order over `days` days. A truck with limit `capacity` can carry consecutive packages until the next one would exceed the limit, then a new day starts. Return the smallest capacity that finishes on time.

- Constraints: package count up to 50,000; weights positive.
- Trace target: weights `[3, 2, 2, 4, 1, 4]`, days `3`.
- Watch for: testing every capacity from 1 upward.

<details>
<summary>Hint after minute 12</summary>

For a proposed capacity, checking whether it works is much easier than directly constructing the smallest one.

</details>

<details>
<summary>Hint after minute 22</summary>

If a capacity works, every larger capacity works too. Search for the boundary, and be careful to keep a working midpoint as a candidate.

</details>

### 8B. Repeated prefix penalty

A string has lowercase letters. Return the minimum deletions needed so no two letters have the same frequency.

- Constraints: length up to 100,000.
- Trace target: `aaabbbcc`.
- Watch for: repeatedly scanning the whole frequency table after each deletion.

<details>
<summary>Hint after minute 12</summary>

First compress the string into counts; the letters themselves no longer matter.

</details>

<details>
<summary>Hint after minute 22</summary>

As you adjust a count downward, you need fast membership for frequencies already claimed. State why counts never need to increase.

</details>

### 8C. Cheapest edit script length

Given two short strings, return the minimum number of insertions, deletions, and replacements needed to turn the first into the second.

- Constraints: lengths up to 500.
- Trace target: `horse` to `ros`.
- Watch for: a recursive solution branching three ways on the same `(i, j)` pairs repeatedly.

<details>
<summary>Hint after minute 12</summary>

A subproblem is determined by how much of each string remains, not by the path you took to get there.

</details>

<details>
<summary>Hint after minute 22</summary>

Define a two-dimensional state over prefixes or suffixes. Matching characters move diagonally for free; otherwise consider the three edit moves.

</details>

---

## Postmortem log template

Use this after every packet. Keep the entries short enough that you will actually reread them.

| Problem | Recognition error | Implementation error | Missed edge case | Next review date |
|---|---|---|---|---|
| 1A |  |  |  |  |
| 1B |  |  |  |  |
| 1C |  |  |  |  |

A good postmortem names the specific confusion: "treated subsequence as contiguous," "used a weighted grid with a plain queue," "sorted and lost original indices," or "used one heap for a streaming median." That sentence is the thing you review before the next timed set.

---

<div align="right">

[Waste map →](dsa-waste-map.md) · [Appendix →](dsa-appendix.md)

</div>
