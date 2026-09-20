# Chapter 3 (MongoDB companion): What the database is actually doing

*[← Chapter 2 (companion)](ch2-mongo.md) · [SQL twin: Chapter 3](../sql/ch3-sql.md) · [Contents](../../foundations-README.md)*

- [ ] **Mark as read**

[Chapter 3](../sql/ch3-sql.md) goes under the abstraction: why one query is instant and another times out, and what keeps data correct when two writers collide. This is the companion's most important entry, because the mechanisms here — indexes, query plans, transactions — are *nearly identical* across SQL and MongoDB, and the two places they genuinely differ (multi-document transactions and consistency knobs) are exactly where a MongoDB-native engineer gets the most pointed interview questions. Know these and "why is my query slow?" and "is my data safe?" stop being mysteries in either database.

The principle is at its sharpest here: **feel the mechanism.** An index is a B-tree whether Postgres or MongoDB owns it. ACID is a promise you can hold *any* database against.

---

## Full scan vs index — same mechanism, different names

A collection of 10 million orders and the query `{ customer_id: 42 }`. With no help, MongoDB reads *every document* and checks each — a **collection scan** (`COLLSCAN`), the O(n) crawl. An **index** is the fix, and it's the same fix as in SQL.

> 💡 **Concept notes — the index is a B-tree here too**
> A MongoDB index is a separate, sorted **B-tree** — the identical structure from Chapter 3, so the same one-liner works: "a balanced sorted tree, so point lookups and ranges are logarithmic." Create one with `db.orders.createIndex({ customer_id: 1 })` (`1` ascending, `-1` descending). It turns the `COLLSCAN` into an **index scan** (`IXSCAN`) — milliseconds on billions of documents. Range queries (`{ created_at: { $gt: ISODate("2026-01-01") } }`) walk a contiguous slice of sorted leaves, and an index can supply documents already ordered for a `.sort()`, exactly as in SQL. The `_id` field is indexed automatically, just like a primary key.

---

## Indexes still aren't free

Same tradeoff, no exceptions: an index speeds **reads** and slows **writes**, because every insert and update must also maintain each index, and indexes eat disk (or RAM — MongoDB really wants its indexes in memory). So the interview answer is unchanged: **index the fields you filter, sort, or `$lookup` on; don't over-index a write-heavy collection.**

> 💡 **Concept notes — compound indexes and the ESR rule**
> MongoDB's version of SQL's "leftmost prefix" is the same idea with a memorable refinement. A **compound index** `{ customer_id: 1, created_at: 1 }` helps queries on `customer_id`, or `customer_id` *and* `created_at` — but **not** `created_at` alone, because the tree is sorted by `customer_id` first. That's leftmost prefix, identical to SQL. The refinement worth quoting is the **ESR rule** for ordering the fields of a compound index: put **E**quality-matched fields first, then the **S**ort field, then **R**ange-matched fields. So a query filtering `status = "open"`, sorting by `created_at`, and ranging on `total` wants an index `{ status: 1, created_at: 1, total: 1 }`. "Equality, Sort, Range" is a crisp thing to say when an interviewer probes on index design — it's more specific than most candidates can offer.

---

## Reading the plan: `explain` vs `EXPLAIN`

How do you *know* whether a query used an index or scanned? You ask the database. SQL has `EXPLAIN`; MongoDB has `.explain()`.

```sql
-- SQL
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42;
-- hunt for: "Seq Scan" (bad on a big table) vs "Index Scan" (good)
```

```js
// MongoDB
db.orders.find({ customer_id: 42 }).explain("executionStats");
// hunt for winningPlan.stage: "COLLSCAN" (bad on a big collection) vs "IXSCAN" (good)
```

> 💡 **Concept notes — what to look for in the plan**
> The job is identical to SQL: find a full scan on a big data set and fix it with the right index. In MongoDB's `explain("executionStats")` output you read the **`winningPlan`** — a `COLLSCAN` stage is the red flag, an `IXSCAN` means an index is doing the work. The tell-tale number is comparing **`totalDocsExamined`** to **`nReturned`**: if the query examined 10 million documents to return 12, it scanned. A healthy indexed query examines about as many documents as it returns. "When a query is slow I'd `explain` it, look for a `COLLSCAN` with `docsExamined` far above `nReturned`, and add an index matching the filter and sort" is exactly the debugging story interviewers want — the same story as Chapter 3, in Mongo's vocabulary.

---

## Transactions and ACID — where the databases actually differ

The other half of "what the database is doing" is correctness under concurrency and failure: what if the power dies mid-transfer, or two people book the last seat at once? SQL's answer is **transactions governed by ACID**, and this is the one topic where the MongoDB story is genuinely different — so it's worth getting exactly right rather than hand-waving "NoSQL isn't ACID," which is both outdated and a red flag in an interview.

> 💡 **Concept notes — ACID, and what MongoDB actually guarantees**
> The four guarantees are the same targets (Chapter 3 has the full definitions): **A**tomicity (all-or-nothing), **C**onsistency (valid state to valid state), **I**solation (concurrent transactions don't corrupt each other), **D**urability (committed data survives crashes). The nuance that trips people up:
> - **A single-document write in MongoDB is always atomic** — updating one document, however many fields or nested arrays it touches, is all-or-nothing on its own. This is why the *embed* modeling instinct pays off twice: when related data lives in one document, an operation that would need a multi-row SQL transaction is just one atomic document update.
> - **Multi-document transactions exist** (since 4.0 on replica sets, 4.2 on sharded clusters) and are fully ACID — `session.startTransaction()` ... `commitTransaction()`, the direct analogue of `BEGIN; ... COMMIT;`. But they carry more overhead than in a relational database, so the design guidance is to *reach for the data model that makes them unnecessary* (embed the aggregate) and use explicit transactions for the genuine cross-document cases like a funds transfer between two accounts.
> The mature interview answer: **"single-document operations are always atomic in MongoDB, and multi-document ACID transactions are available since 4.0 — but the idiomatic move is to model so that a business operation lives in one document and doesn't need a multi-document transaction at all."** That shows you know both the capability and the philosophy.

---

## Isolation levels vs read/write concern

SQL tunes how much concurrent transactions see through **isolation levels** (Read Uncommitted → Read Committed → Repeatable Read → Serializable), trading strictness for speed. MongoDB exposes the same *kind* of dial, but split across two knobs shaped by its replicated architecture.

> 💡 **Concept notes — the two knobs: write concern and read concern**
> Because MongoDB replicates data across several nodes, "is it safe?" splits into "how many copies confirmed the write?" and "how fresh is the read?"
> - **Write concern** — how many replicas must acknowledge a write before it's considered done. `w: 1` (the primary only) is fast but a crash before replication can lose it; `w: "majority"` waits for a majority of nodes, the practical **durability** dial. This is the knob a "did we actually save it?" question is really about.
> - **Read concern** — how *committed* the data you read must be. `"local"` may return not-yet-replicated data; `"majority"` returns only data acknowledged by a majority (so it can't be rolled back) — MongoDB's answer to the **dirty read**; `"snapshot"` gives a consistent point-in-time view inside a transaction, the analogue of a serializable snapshot.
> The mapping to say out loud: **"SQL isolation levels bundle durability and read-freshness into one setting; MongoDB splits them into write concern (how many replicas confirmed the write — durability) and read concern (how committed the data I read must be — the isolation/anomaly dial). `majority`/`majority` is the safe default."** The anomalies from Chapter 3 — dirty, non-repeatable, phantom reads — are the same phenomena these knobs guard against.

---

## Try it

1. A query `{ email: "..." }` on a 5-million-document users collection takes 4 seconds. What's almost certainly missing, and which command confirms it before you change anything — and what field in its output gives it away?
2. Explain why you wouldn't put an index on every field of a write-heavy collection.
3. You have a compound index `{ country: 1, city: 1 }`. Which queries can use it: `country` only? `city` only? both? Then restate the ESR rule and give the ideal index for a query that equality-matches `status`, sorts by `created_at`, and ranges on `total`.
4. An interviewer says "NoSQL isn't ACID, right?" Give the accurate, up-to-date correction in two sentences.
5. Two users try to buy the last concert ticket at the same instant. Describe how you'd model and write this in MongoDB so exactly one succeeds — and say whether you'd even need a multi-document transaction.
6. What's the difference between write concern and read concern, and which one is MongoDB's answer to a dirty read?

*Write your answers in [ch3-mongo-tryit.md](../../code/ch3-mongo-tryit.md).*

---

## The bumper sticker

> *Under the hood MongoDB and SQL are twins: an index is a B-tree turning `COLLSCAN` into `IXSCAN`, and `explain` is your `EXPLAIN`. They part ways on correctness — single-document writes are always atomic, multi-document ACID transactions exist since 4.0, and isolation is split into write concern (how many replicas confirmed) and read concern (how committed your read is). Model so the transaction isn't needed, and reach for `majority` when it is.*

Next: zoom out from single operations to the whole schema — normalizing vs embedding, modeling relationships, and the honest "SQL vs document" answer from the document side.

---

<div align="right">

[Chapter 4 (MongoDB companion) →](ch4-mongo.md)

</div>
