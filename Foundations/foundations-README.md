# Foundations & CS Fundamentals — SQL · Databases · OS · Networking · Python · Concurrency · Git · Distributed Systems

A 15-chapter primer on the pop-quiz layer of software engineering interviews: the questions that test whether you understand what's happening *one level below* the API, the query, or the framework. Written in the same conversational style as the LLD, HLD, DSA, Behavioural, and AI/ML primers in this collection.

Core principle: **feel the mechanism before trusting the abstraction.**

---

## Why this track exists

Most interview rounds have a design question or a coding question as their headline. But at any point — during HLD, during LLD, during the "let's chat about your experience" part — an interviewer can drop a pop quiz: "how does a database index actually work?", "what's the difference between a process and a thread?", "walk me through what happens when you type a URL and hit enter." These aren't obscure. They're the things every working engineer is *assumed* to know, and the ones that expose gaps most clearly when you don't.

This track plugs those gaps. It is not a deep dive into any single subject — it's a **fluency layer** across the mechanisms that come up constantly:

- **SQL** — because data lives in databases and every backend engineer writes queries.
- **Database internals** — because "why is my query slow?" traces straight to indexes, plans, and transactions.
- **Operating systems** — because processes, threads, and memory are the substrate of everything you build.
- **Networking** — because every feature you ship rides the network, and understanding it makes you a sharper system designer too.
- **Concurrency** — because the right tool depends on whether your code is waiting or computing.
- **Python idioms** — because interviews assume you can explain the language mechanisms you reach for.
- **Git** — because every engineer uses the graph, especially when history needs to be combined or undone.
- **Distributed systems** — because the moment work crosses a network, silence becomes ambiguous and retries, copies, ordering, and recovery become correctness concerns.

## The one idea

Every pop-quiz question has the same shape underneath: *"do you understand the mechanism, or are you just pattern-matching the syntax?"*

You can write `SELECT * FROM orders JOIN customers ON ...` without understanding *why* the clauses run in a non-obvious order or what the query planner actually does. You can use `async/await` without understanding what the event loop is doing. You can call a REST API without understanding what TCP is doing underneath. The interview question always finds the edge of your understanding and asks you to go one level deeper. This track puts you one level deeper in each area, so you're never caught at the edge.

## How this track is different from the others

Unlike DSA (which needs *volume* of practice) or HLD (which needs *design frameworks*), this track is built for **rapid recall under pressure.** You're not solving a new problem — you're articulating something you may understand conceptually but have never had to explain out loud, fast, to someone evaluating you.

So the study method shifts:
- **Session 1 (read):** Read the chapter once. Run any code. Don't take notes — just absorb.
- **Session 2 (recall, next day):** Close the book. Write the core concepts out from memory, *then* check. The gap between what you thought you knew and what you can write cold is exactly your re-read list.
- **Session 3 (say it out loud):** Answer the "Try it" questions *aloud*, as if to an interviewer. Saying it is different from knowing it — speaking finds the words you're missing.

Use the companion pages for the two moments ordinary notes miss: [mechanism maps](foundations-mechanism-maps.md) when you need to see the causal flow, and [60-second recall](foundations-60-second-recall.md) when you need to make the answer interview-ready. Role split: chapters teach, the appendix looks up, mechanism maps show causality, and recall cards train spoken delivery.

For quick review, use this order:
1. [Mechanism maps](foundations-mechanism-maps.md) — rehearse the arrows until the failure mode feels inevitable.
2. [60-second recall](foundations-60-second-recall.md) — time the DART answer aloud.
3. [Appendix question bank](foundations-appendix.md#question-bank-by-chapter) — test whether the answer survives a prompt.

≈1.5–2 hours per chapter — shorter than the other tracks, because these chapters are narrower and recall-focused.

## Which chapters to read (triage by role)

Read them all if you have time. If you're triaging:
- **SQL chapters (1–2) first** — they come up in *every* role with a backend component. The highest-value chapters for most engineers.
- **Database internals (3–4)** — essential for backend/data roles; "why is this slow?" is a near-universal question.
- **OS chapters (5–6)** — essential for systems/infra roles, FAANG-style loops, and anywhere concurrency matters.
- **Networking (7–8)** — critical for infra/platform roles; also surfaces inside HLD rounds at many companies.
- **Concurrency patterns (9)** — highest day-to-day practical value, especially if you write async code.
- **Python: data & iteration (10)** — the comprehensions, generators, and `collections` you lean on hardest in a coding/DSA round; skim if you're already Pythonic.
- **Python: objects & idioms (11)** — dataclasses, dunders, context managers, and type hints; study if you reach for plain classes and `self.x = x` by default.
- **Chapter 12 (ritual)** — read before any interview, regardless of which other chapters you covered.
- **Chapter 13 (data teams)** — a bonus, not a pop-quiz chapter; skim it to learn who the data engineers, analysts, and scientists around you are and when to pull them in. Useful for new grads and anyone joining a team with a data org.
- **Chapter 14 (Git)** — a bonus tooling chapter; the version-control model every engineer is assumed to know but few can explain. Read it if merge-vs-rebase or "undo a pushed commit" would catch you out.
- **Chapter 15 (distributed systems)** — essential for backend, platform, and senior roles; it derives partial failure, retry safety, replication, coordination, delivery, and disaster recovery from the first ambiguous timeout.

## Reading order

**Part 1 — SQL and databases**
- Chapter 1: SQL you must be able to write *(SELECT, WHERE, JOIN, GROUP BY — and the execution order that trips people up)*
- Chapter 2: SQL you need to know but rarely write *(window functions, CTEs, subqueries, the N+1 problem)*
- Chapter 3: What the database is actually doing *(indexes, query plans, ACID, transactions, isolation levels)*
- Chapter 4: Designing schemas *(normalization, when to denormalize, relational vs document)*

**Part 2 — Operating systems**
- Chapter 5: Processes, threads, and concurrency *(what each is, context switching, race conditions, locks, deadlocks)*
- Chapter 6: Memory *(stack vs heap, garbage collection, memory leaks — and why it shows up in code you write)*

**Part 3 — Networking**
- Chapter 7: Networking fundamentals *(TCP vs UDP, HTTP/HTTPS, TLS, DNS — what each actually does)*
- Chapter 8: How a request travels *(browser → DNS → load balancer → server → DB and back — the whole journey)*

**Part 4 — Putting it together**
- Chapter 9: Concurrency in your own code *(async/await, event loops, thread pools, I/O-bound vs CPU-bound)*
- Chapter 10: The Python you're assumed to know — data and iteration *(comprehensions, dict/set comprehensions, the 2-D aliasing trap, generators, unpacking, collections)*
- Chapter 11: The Python you're assumed to know — objects and idioms *(dataclasses, dunder methods, context managers, type hints)*
- Chapter 12: The pop-quiz ritual *(how these questions are asked, a 4-step way to answer, and a fast-review grid)*

**Bonus**
- Chapter 13: Working with the data teams *(what data engineers, analysts, scientists, and ML engineers do — and when to pull them in)*
- Chapter 14: Git — the graph beneath the commands *(commits as snapshots, branches as pointers, merge vs rebase, and the safe way to undo)*

**Part 6 — Distributed systems**
- Chapter 15: When one machine becomes many *(partial failure, timeouts, safe retries, replication, consistency, coordination, delivery, degradation, and recovery)*

**Companions:** [Mechanism maps](foundations-mechanism-maps.md), [60-second recall](foundations-60-second-recall.md), and the [Appendix](foundations-appendix.md): SQL cheat sheet, OS vocabulary, networking vocabulary, distributed-systems vocabulary, Git vocabulary, and a full interview question bank by chapter.

## Runnable code

- [code/sql_demo.py](code/sql_demo.py) — Uses Python's built-in `sqlite3` (no install needed) to make Chapters 1–3 concrete: joins, GROUP BY, what an index does, and reading a query plan with `EXPLAIN QUERY PLAN`. Run with `python3 sql_demo.py`.

## Prerequisites

- Can write basic code in any language; comfortable with variables, functions, loops.
- **No prior database, OS, or networking knowledge assumed** — every concept is built from scratch.
- The HLD primer touches some of this at *system scale*; this track goes deeper on the *mechanisms*, not the architecture.

## Checkpoints

- **After Ch 2:** Can you write a query using a window function from scratch, without looking it up?
- **After Ch 4:** Can you explain why adding an index speeds up reads but slows down writes?
- **After Ch 6:** Can you explain, without notes, what happens in memory when one function calls another?
- **After Ch 8:** Can you walk end-to-end through a browser request — every hop — without pausing?
- **After Ch 12:** Can you answer "what's the difference between a process and a thread?" in 60 seconds, clearly, with no filler?
- **After Ch 15:** Given a timed-out side effect, can you explain the ambiguity, design a bounded idempotent retry, name the ordering/coordination boundary, and state RPO/RTO?

If a checkpoint fails, reread the relevant chapter and *say the answer out loud* until it's fluent.

## The bumper sticker

> *Every pop-quiz question asks whether you know what's happening one level below where you normally code. Feel the mechanism — what the database does with your query, what the OS does with your thread, what TCP does with your bytes — and no pop quiz can catch you out.*

---

<div align="right">

[Chapter 1 →](1-sql-and-databases/sql/ch1-sql.md)

</div>
