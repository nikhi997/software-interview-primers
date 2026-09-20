# HLD Primer — Reading order and study contract

A 16-chapter primer on High-Level (System) Design, built around a single principle: *feel the bottleneck before reaching for the component.*

This is the companion to the LLD primer. LLD asks "does your code bend or break when a requirement lands?" HLD asks a different question: *"does your system bend or break when the traffic lands?"*

## The one idea

Every system design book throws the same parts at you on page one: load balancer, cache, message queue, sharded database, CDN. You memorize the diagram. Then in the interview you draw all of it for a problem that needed none of it.

We're not doing that.

We start with **one server doing everything.** It works. Then we ask: *what specific load would actually break this?* When we find it, we add exactly one thing to fix it — and we feel why. A cache because reads repeat. A queue because work can wait. A shard because the data won't fit. Never because "that's the architecture."

By the end, you won't have memorized a diagram. You'll be able to *derive* one, live, from the requirements — which is exactly what the interview tests.

## Reading order

Read in sequence. Each chapter assumes the previous ones.

**Part 1 — Foundation (one box, then why it breaks)**
- Chapter 1: The whole app on one server *(and what actually makes you change it)*
- Chapter 2: When one machine isn't enough *(stateless services, load balancing)*
- Chapter 3: When the database is the bottleneck *(replication, read replicas, leader election)*
- Chapter 4: When one database can't hold it all *(sharding, consistent hashing)*

**Part 2 — Components through bottlenecks**
- Chapter 5: When reads repeat themselves *(caching, eviction, invalidation)*
- Chapter 6: When work can wait *(message queues, async processing)*
- Chapter 7: When you must not lose data *(durability, storage engines, CAP)*
- Chapter 8: When too many requests arrive *(rate limiting, backpressure)*
- Chapter 9: When the files get large *(blob storage, CDN)*

**Part 3 — Naming what you know**
- Chapter 10: The vocabulary of tradeoffs *(CAP, consistency, latency vs throughput)*
- Chapter 11: Drawing the system *(HLD diagrams, data flow, API contracts)*
- Chapter 12: Keeping it running *(CI/CD, containers, orchestration, observability, SLOs, releases, IaC — what "DevOps people" do)*

**Part 4 — Interview-shaped (worked problems)**
- Chapter 13: The interview ritual *(URL shortener at scale — full walkthrough)*
- Chapter 14: Worked problem — Twitter / News Feed
- Chapter 15: Worked problem — Chat system (WhatsApp)
- Chapter 16: Worked problem — Ride-sharing (Uber)

**Appendix:** Component catalog, latency numbers to know, the estimation cheatsheet, common pitfalls, the 35-minute interview budget.

**[Visual deepdive](hld-visual-deepdive.md):** all sixteen chapters retold as one continuous diagram-led story, where every diagram is the previous one plus a single move. Read it *after* the book — it's the companion for Session 2, when you're redrawing architectures from memory.

## Prerequisites

You don't need LLD first, but it helps. You *do* need:
- Comfort with the idea of a client, a server, and a database talking over a network
- Rough comfort with "a request comes in, something happens, a response goes out"
- No distributed-systems theory. We build the vocabulary as we go.

## Study contract — do not skip

Each chapter is designed for **3 mini-sessions, NOT one sitting:**

**Session 1 (45–60 min):**
Read the chapter once. When it does a back-of-envelope estimate, *redo the arithmetic yourself* on paper — don't just nod at the number. Don't take notes. Don't move to Session 2 the same day.

**Session 2 (45–60 min, next day):**
Open a blank page. From memory, redraw the architecture the chapter ended with — boxes, arrows, and *why each box exists.* No peeking. When stuck, peek at the minimum needed, close again, continue. Diff against the chapter. Note 2–3 things that slipped. (Once you've finished the book, the [visual deepdive](hld-visual-deepdive.md) is the fastest place to diff against — every architecture in one file, in order.)

**Session 3 (30 min, day after):**
Do the end-of-chapter exercises. Then explain the chapter to yourself in 4–5 sentences: what was the system, what was the bottleneck, what was the move, what new bottleneck did the move create. Only after this, move to the next chapter.

Total: ~2.5 hours per chapter, over 3 days. 16 chapters → ~48 days of focused work. Don't compress. HLD intuition is built from *deriving* the same handful of moves over and over until they're automatic.

## Checkpoints

Every 4 chapters, stop and assess:

- **After Ch4:** Can you take a brand-new read-heavy app and explain where the first three bottlenecks appear as it grows, and the one move that fixes each?
- **After Ch8:** Given a new problem, can you predict which 3–4 components it needs *and justify each from a specific load*, not from habit?
- **After Ch12:** Can you describe how you'd deploy, observe, and set a reliability target (SLO + error budget) for a system you just designed — and name a safe rollout strategy?
- **After Ch13:** Can you do the full interview ritual on an unfamiliar problem in 35 minutes — estimate, API, data model, architecture, bottleneck, tradeoff?

If a checkpoint fails, **stop and redo the previous chapters.** Don't proceed.

## How HLD interviews are actually scored

Most candidates think the interviewer wants the "right" architecture. They don't. They're checking whether you can:

1. **Drive the problem** — ask the right clarifying questions instead of assuming
2. **Estimate** — turn "millions of users" into reads/sec, writes/sec, storage/year
3. **Justify** — every component you add is in response to a number, not a buzzword
4. **Trade off** — name what you gave up for what you gained (there's always a cost)
5. **Go deep on demand** — when they poke one box, you can zoom in without falling apart

This book builds those five, in that order. The architecture is almost a side effect.

## The bumper sticker

> *Architecture is the set of moves you make so the system bends instead of breaks when the traffic lands.*

Not complexity. Not "best practices." Response to load. That's the whole game.

---

<div align="right">

[Chapter 1 →](hld-chapter-1.md)

</div>
