# Chapter 3: What the database is actually doing

*[← Chapter 2](ch2-sql.md) · [Contents](../../foundations-README.md)*

- [ ] **Mark as read**

You can write correct SQL and still have no idea *why* one query returns instantly and another times out, or what actually happens when two users update the same row at once. This chapter goes under the abstraction — the heart of this track's principle. It answers the two questions interviewers reach for most: **"how does an index work?"** and **"what does ACID mean?"** Get these and "why is my query slow?" and "is my data safe under concurrent writes?" stop being mysteries.

---

## How a query finds rows: the full scan vs the index

Imagine a table of 10 million orders and the query `WHERE customer_id = 42`. Without help, the database does the only thing it can: read *every row* and check each one. That's a **full table scan** — O(n), and it's why big-table queries crawl.

An **index** is the fix, and it's the single most important database performance concept.

> 💡 **Concept notes — what an index is**
> An **index** is a separate, sorted data structure that lets the database find rows by a column's value *without* scanning the whole table. The analogy is exact: it's the index at the back of a book. To find every mention of "mitochondria," you don't read all 800 pages — you flip to the index, which is alphabetized, find the term, and jump to the listed pages. A database index does the same for a column: keep the values sorted (with pointers to the rows), and lookups go from O(n) scanning to roughly O(log n) — milliseconds even on billions of rows.

> 💡 **Concept notes — the B-tree (what's under most indexes)**
> Most database indexes are **B-trees** (balanced trees). You don't need the implementation, just the shape: a tree kept balanced so any value is reachable in a few hops from the root, and the leaves are sorted. This gives O(log n) lookups *and* makes **range queries** fast (`WHERE created_at > '2026-01-01'` walks a contiguous slice of the sorted leaves) and supplies rows already sorted for `ORDER BY`. "It's a balanced sorted tree, so lookups and ranges are logarithmic" is all you need to say.

---

## The catch: indexes aren't free

If indexes make reads fast, why not index every column? Because they have a real cost, and *knowing the tradeoff* is what separates a thoughtful answer from a naive one.

> 💡 **Concept notes — the read/write tradeoff**
> An index speeds up **reads** but slows down **writes.** Every `INSERT`, `UPDATE`, or `DELETE` must now *also* update every index on that table — keeping each sorted structure correct takes work. Indexes also consume disk space. So indexing is a deliberate tradeoff: add them for columns you frequently filter, join, or sort on; *don't* blindly index everything, because a write-heavy table drowning in indexes gets slower. The standard interview answer to "should I add an index?" is: **"it depends on the read/write ratio — index the columns that queries filter or join on most, and accept the slight write penalty; avoid over-indexing write-heavy tables."** Primary keys are indexed automatically; foreign keys usually should be.

> 💡 **Concept notes — composite indexes and "leftmost prefix"**
> An index can cover **multiple columns** — a *composite* index on `(customer_id, created_at)`. The order matters: such an index helps queries filtering on `customer_id`, or on `customer_id AND created_at`, but **not** one filtering on `created_at` alone — because the index is sorted by `customer_id` first. This "leftmost prefix" rule is a common deeper-dive question; the takeaway is that composite-index column order should match your query patterns.

---

## Reading the query plan: EXPLAIN

How do you *know* whether a query uses an index or does a full scan? You ask the database with **`EXPLAIN`** (or `EXPLAIN ANALYZE`).

> 💡 **Concept notes — EXPLAIN / query plan**
> The **query planner** is the part of the database that decides *how* to execute your declarative SQL (Chapter 1) — which indexes to use, what join strategy, in what order. **`EXPLAIN`** shows you that plan without running it (`EXPLAIN ANALYZE` runs it and reports real timings). The thing you're hunting for: a **"sequential scan" / "full table scan"** on a big table usually means a missing index, while an **"index scan"** means it's using one. "When a query is slow, I'd `EXPLAIN` it and look for a full table scan on a large table, then add the right index" is exactly the answer interviewers want for "how do you debug a slow query." The runnable [code/sql_demo.py](../../code/sql_demo.py) shows a plan changing from scan to index lookup when you add an index.

---

## Transactions and ACID: keeping data correct

The other half of "what the database is doing" is about *correctness under concurrency and failure.* What happens if the power dies mid-transfer? If two people book the last seat simultaneously? The answer is **transactions**, governed by **ACID.**

> 💡 **Concept notes — transaction**
> A **transaction** groups several operations into one all-or-nothing unit. The canonical example: a bank transfer is "subtract $100 from A" *and* "add $100 to B" — both must happen or neither. You wrap them: `BEGIN; ...; COMMIT;` (or `ROLLBACK;` to undo). The database guarantees the group behaves as a single indivisible step.

> 💡 **Concept notes — ACID, the four guarantees (know all four)**
> - **Atomicity** — all-or-nothing. Every statement in the transaction succeeds, or the whole thing is rolled back. No half-finished transfers.
> - **Consistency** — the transaction moves the database from one valid state to another, respecting all rules (constraints, foreign keys). It never leaves the data violating its own rules.
> - **Isolation** — concurrent transactions don't step on each other; each behaves as if it ran alone (the *degree* of this is tunable — see isolation levels below).
> - **Durability** — once committed, the data survives crashes, power loss, restarts. It's written to permanent storage, not just memory.
> "A-C-I-D: atomic all-or-nothing, consistent valid states, isolated from each other, durable once committed" is a memorize-it-cold answer. These are *the* reason relational databases are trusted for money and orders.

---

## Isolation levels: how much do concurrent transactions see?

Full isolation is expensive, so databases let you choose *how* isolated transactions are — trading strictness for speed. You rarely tune this, but interviewers ask because it reveals real depth.

> 💡 **Concept notes — isolation levels and their anomalies**
> Weaker isolation is faster but allows certain **anomalies** when transactions overlap:
> - **Dirty read** — reading another transaction's *uncommitted* changes (which might be rolled back). Prevented at "Read Committed" and above.
> - **Non-repeatable read** — reading the same row twice in one transaction and getting different values because another transaction committed a change between. Prevented at "Repeatable Read."
> - **Phantom read** — re-running the same query and getting *new rows* that another transaction inserted. Prevented at "Serializable."
> The four standard levels, weakest to strongest: **Read Uncommitted → Read Committed → Repeatable Read → Serializable.** Each prevents more anomalies but allows less concurrency. Most databases default to Read Committed or Repeatable Read. You don't need to memorize the full grid, but knowing "stronger isolation prevents more anomalies but reduces concurrency, and Serializable is the strictest" shows you understand the tradeoff.

---

## Try it

1. A query `WHERE email = '...'` on a 5-million-row users table takes 4 seconds. What's almost certainly missing, and how would you confirm it before making a change?
2. Explain why you wouldn't just add an index to every column in a table. What's the cost?
3. You have a composite index on `(country, city)`. Which of these queries can use it: filter by `country` only? by `city` only? by both? Why?
4. Define each letter of ACID in one sentence, with the bank-transfer example for Atomicity.
5. Two users try to buy the last concert ticket at the same moment. Which ACID property is most relevant to making sure only one succeeds, and why?
6. What's a dirty read, and which isolation level is the lowest that prevents it?

*Write your answers in [ch3-sql-tryit.md](../../code/ch3-sql-tryit.md).*

---

## The bumper sticker

> *An index is the book's back-index: a sorted structure that turns full-table scans into logarithmic lookups — fast reads at the cost of slightly slower writes. And ACID is the database's promise that transactions are atomic, consistent, isolated, and durable, which is exactly why we trust databases with money.*

Next: zoom out from single queries to the whole schema — how to structure tables with normalization, when to deliberately break the rules, and the relational-vs-document choice.

---

<div align="right">

[Chapter 4 →](ch4-sql.md)

</div>
