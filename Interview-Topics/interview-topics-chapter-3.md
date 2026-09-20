# Chapter 3: PostgreSQL

*[← Chapter 2](interview-topics-chapter-2.md) · [Contents](interview-topics-README.md)*

- [ ] **Mark as read**

Postgres is the technology people are most likely to *claim* and least likely to be ready to *defend*. You've written `SELECT`s and `JOIN`s for years, so you put "PostgreSQL" on the resume — and then the interviewer asks "why is this query slow?" or "what does an index cost you?" and the answer gets vague. This chapter is the layer that turns a claimed skill into a defensible one.

The concept beneath the brand: Postgres is the **database internals** from [Foundations Ch 3](../Foundations/1-sql-and-databases/sql/ch3-sql.md) made concrete — indexes, query plans, transactions, isolation. The SQL itself is [Foundations Ch 1–2](../Foundations/1-sql-and-databases/sql/ch1-sql.md). This chapter is the interview-recall view of both.

---

## Indexes: the single most-asked database topic

> 💡 **Concept notes — what an index is and what it costs**
> A B-tree index is a sorted side-structure that lets the database **find rows without scanning the whole table** — turning O(n) into O(log n) lookups. The trade-off interviewers want you to volunteer: indexes **speed reads but slow writes** (every insert/update must maintain them) and **cost storage**. So index for your read patterns, don't over-index, and watch write-heavy tables.

> 💡 **Concept notes — the rules that catch people**
> - **Composite index column order matters** — an index on `(a, b)` follows the **leftmost-prefix** rule: it helps queries on `a` or `a AND b`, **not** `b` alone. (Classic trap question.)
> - **Sargability** — the planner can't use an index if a function wraps the column (`WHERE lower(email) = …` won't use an index on `email`).
> - A **covering index** can satisfy a query entirely from the index, skipping the table.
> - Poor **selectivity** (the filter matches most rows) makes the planner skip the index and scan anyway.

> 💡 **Concept notes — beyond the B-tree**
> The default is B-tree, but interviewers like "when wouldn't a B-tree help?": **GIN** for `JSONB`/array/full-text containment, **partial** indexes (`WHERE active = true`) to index only the rows you query, **expression** indexes to make `lower(email)` sargable. Two writes is one index decision: more indexes = faster reads, slower writes.

---

## VACUUM, MVCC, and connection pooling: the ops every probe hits

> 💡 **Concept notes — why dead rows and pooling matter**
> - **MVCC keeps old row versions** so readers don't block writers; updates/deletes leave **dead tuples**. **VACUUM** (autovacuum) reclaims them — skip it and the table **bloats**, slowing scans. That's why high-churn tables need attention.
> - **Connections are expensive** — each is a backend process. Apps must use a **pool** (HikariCP, PgBouncer); spawning a connection per request exhausts Postgres fast. "Why a pool?" is a near-guaranteed follow-up.
> - **`JOIN`s, window functions, CTEs** — know inner vs left join, `ROW_NUMBER()/RANK()` for "top-N per group", and `WITH` for readable multi-step queries. These are the SQL questions a data-heavy role asks.

---

## Query plans: how you debug "it's slow"

> 💡 **Concept notes — read the plan, don't guess**
> `EXPLAIN ANALYZE` shows the **actual** execution plan. Look for: **sequential scans on big tables** (often a missing index), **bad row estimates** (stale statistics), and **expensive sorts/joins**. The debugging loop: read the plan → add/fix an index or rewrite the query to be sargable → re-check the plan. "I'd run `EXPLAIN ANALYZE` first" is the answer that signals you've actually tuned a query.

---

## Transactions, ACID, and isolation

> 💡 **Concept notes — isolation levels, by what they prevent**
> - **Read committed** (Postgres default) — prevents dirty reads; allows non-repeatable and phantom reads.
> - **Repeatable read** — also prevents non-repeatable reads.
> - **Serializable** — prevents all three (dirty, non-repeatable, phantom) at the cost of more conflicts/retries.
> Pick by the invariant: a balance check that must not race may need serializable or explicit locking (`SELECT … FOR UPDATE`). **MVCC** is how Postgres lets readers not block writers — each transaction sees a consistent snapshot. (Deeper: [Foundations Ch 3](../Foundations/1-sql-and-databases/sql/ch3-sql.md).)

---

## Schema: relational, and when not to be

> 💡 **Concept notes — normalize, then denormalize on purpose**
> **Normalize** for integrity (no duplicated, drift-prone data); **denormalize** deliberately for read speed when joins become the bottleneck. Know **relational vs document** trade-offs — Postgres also has `JSONB` if you need document-style flexibility inside a relational store. (Deeper: [Foundations Ch 4](../Foundations/1-sql-and-databases/sql/ch4-sql.md).) Run [Foundations/code/sql_demo.py](../Foundations/code/sql_demo.py) to see joins, `GROUP BY`, and a query plan live.

---

## Try it

Answer aloud:

1. Why does adding an index speed up reads but slow down writes? When would you *not* add one?
2. You have a composite index on `(customer_id, created_at)`. Does a query filtering only on `created_at` use it? Why or why not?
3. A query is slow. Walk me through exactly how you'd debug it.
4. Name the isolation levels and what each one prevents. When would you reach for serializable?
5. What's the difference between normalizing and denormalizing, and when would you denormalize on purpose?
6. What is VACUUM for, and why does a high-update table get slow without it?
7. Why does an app need a connection pool, and when would you pick a GIN or partial index over a B-tree?

*Write your answers in [interview-topics-chapter-3-tryit.md](code/interview-topics-chapter-3-tryit.md).*

## The bumper sticker

> *"PostgreSQL" on a resume invites one question: do you understand the engine, or just the syntax? Be ready to volunteer the index write-cost, read a plan from `EXPLAIN ANALYZE`, and name what each isolation level prevents. That's the difference between a claimed skill and a defended one.*

Next: the technology most likely to be your *gap* — **Kafka** — and the honest-pivot template that turns any gap into a strong answer.

---

<div align="right">

[Chapter 4 →](interview-topics-chapter-4.md)

</div>
