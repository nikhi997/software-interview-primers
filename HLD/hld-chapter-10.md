# Chapter 10: The vocabulary of tradeoffs

*[← Chapter 9](hld-chapter-9.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

You've spent nine chapters *making* tradeoffs. Replication traded freshness for read capacity. Caching traded freshness for speed. Queues traded immediacy for resilience. CAP forced you to trade consistency for availability. Now we step back and put crisp names on these, because in an interview the *words* are how you show you understand. This chapter is the glossary you've earned — every term here, you've already felt.

The big idea to carry through: **there are no right answers in HLD, only tradeoffs you can name and defend.** A candidate who says "I'll use eventual consistency here because a stale like-count is harmless and it lets reads scale" beats one who just draws boxes, every time.

---

## Latency vs throughput

The two ways to measure "performance," constantly confused.

- **Latency:** how long *one* request takes. "This read takes 5 ms." Measured in time.
- **Throughput:** how *many* requests you handle per unit time. "We serve 50,000 requests/sec." Measured in rate.

They're independent, and you can trade one for the other. **Batching** is the classic example: instead of writing 100 records one at a time, write them in one batch. Each individual record now waits a bit longer to be grouped (worse *latency*), but you push far more records per second (better *throughput*). A queue (Ch 6) does the same — a job waits in line (latency up) but the system absorbs way more total work (throughput up).

> 💡 **Concept notes — optimize for the one that matters**
> A trading system lives or dies on **latency** (a millisecond is money). A nightly analytics pipeline only cares about **throughput** (crunch billions of rows by morning; nobody's waiting on any single row). Ask which one the problem actually cares about — optimizing the wrong one is wasted effort. Most user-facing systems care about *tail* latency especially (below).

> 💡 **Concept notes — tail latency (p50, p95, p99)**
> Averages lie. What matters is the **distribution**: **p50** (median — half of requests are faster), **p95**, **p99** (99% are faster than this; the slowest 1%). The "tail" (p99) is what users actually notice and complain about — a 10 ms average means nothing if p99 is 3 seconds and every page loads dozens of resources (so *some* request hits the tail almost every page). Interviewers love "what's your p99?" Targeting tail latency, not average, is a senior instinct.

---

## Consistency models (the spectrum)

Not a binary — a range from strict to loose. You met the endpoints in Ch 3 and Ch 7.

- **Strong consistency:** every read reflects the most recent write. Simplest to reason about; costs latency and availability (recall CP in CAP). *For:* balances, inventory, anything where being wrong is dangerous.
- **Eventual consistency:** replicas converge *eventually* (usually milliseconds); reads may be briefly stale. Cheaper, more available, scales better. *For:* feeds, counts, views, most read-heavy content.
- **Read-your-own-writes:** a middle guarantee — *you* always see your own changes immediately, even if others see them slightly later (Ch 3's fix for the profile-edit problem). A very common practical sweet spot.
- **Causal consistency:** if event B depends on event A, everyone sees A before B (a reply never appears before the message it replies to), but unrelated events can be seen in any order.

> 💡 **Concept notes — pick consistency per piece of data, not per system**
> The recurring lesson of this whole book: *don't* declare "this system is strongly/eventually consistent." Declare it **per feature.** Same app: strong for the wallet balance, eventual for the activity feed, read-your-own-writes for the user's own profile. Naming the model for *each* piece of data is the mark of someone who actually gets it.

---

## CAP and PACELC (the one-paragraph recap)

You learned these in Ch 7; here they are as glossary entries.

- **CAP:** under a network **P**artition, choose **C**onsistency (refuse to answer rather than be wrong → CP) or **A**vailability (answer with possibly-stale data → AP). You can't have both during a partition.
- **PACELC:** even with no partition (**E**lse), you still trade **L**atency vs **C**onsistency. The tradeoff never fully goes away.

The interview phrasing that lands: *"During a partition would I rather return a stale answer or no answer? For this feature, ___, because ___."*

---

## Scaling vocabulary (recap as terms)

- **Vertical scaling (scale up):** bigger box. Simple, hard ceiling, single point of failure.
- **Horizontal scaling (scale out):** more boxes. No real ceiling, survives failures, *requires statelessness* (Ch 2).
- **Replication:** full copies → scales **reads**, survives failure, costs lag (Ch 3).
- **Sharding / partitioning:** distinct slices → scales **size and writes**, costs cross-shard pain (Ch 4).
- **Stateless service:** holds no unique local state, so any instance serves any request — the precondition for scaling out (Ch 2).

---

## Reliability vocabulary

Words to describe "does it stay up and keep the data."

- **Availability:** the fraction of time the system is up and answering, often stated in **nines**:

| "Nines" | Uptime | Downtime per year |
|---|---|---|
| 99% (two nines) | | ~3.65 days |
| 99.9% (three nines) | | ~8.76 hours |
| 99.99% (four nines) | | ~52 minutes |
| 99.999% (five nines) | | ~5 minutes |

Each extra nine is dramatically harder and more expensive. You don't always want five nines — you want the level the product *needs.*

- **Single point of failure (SPOF):** any component whose death takes down the system. The reflex from Ch 2: find each one and ask "what if this dies?" Eliminate via redundancy.
- **Redundancy:** running extra copies (N+1) so losing one doesn't drop you below capacity (Ch 2).
- **Failover:** automatically promoting a standby when the primary dies (Ch 3's replica promotion).
- **Durability:** committed data survives crashes (Ch 7) — distinct from availability (being *up*). You can be down but durable (data safe, service offline).
- **Fault tolerance:** the system keeps working *correctly* despite component failures.

> 💡 **Concept notes — availability ≠ durability**
> A subtle but loved distinction. **Availability** = "can I reach the service right now?" **Durability** = "is my committed data safe?" A system can be unavailable (down for maintenance) yet perfectly durable (no data lost). It can also be highly available yet lose data (answers fast, but a crash drops recent writes). They're different guarantees with different costs — don't conflate them.

---

## Coupling and idempotency (recap)

- **Decoupling:** components don't depend on each other's internals or uptime — a queue decouples producer from consumer (Ch 6). Loosely coupled systems fail in isolation rather than together.
- **Idempotency:** doing an operation twice = doing it once (Ch 6). The defense against the at-least-once redelivery and retries that distributed systems guarantee. *"Make the handler idempotent, dedupe on a unique ID."*

---

## Bounded contexts: where to split the system

At some point the interviewer stops asking "how do you scale this box?" and starts asking "how do you *break this up*?" A single service has grown to own users, orders, payments, inventory, and shipping, and now every team trips over every other team. Where do the boundary lines go?

The tempting answer is "split by technical layer" — a database service, an API service, a business-logic service. That fails, because a single feature change (add a discount field) then touches all three. The boundaries should follow the *domain*, not the plumbing. This is the system-scale version of the decoupling you just named, and the idea has a name: a **bounded context** — a section of the system that owns one part of the domain, with its own data and its own internally-consistent vocabulary.

Here's the tell that you've found a real boundary: **the same word means different things to different teams.** "User" to the Identity context is a login and a password hash; to Billing it's an account with a payment method; to Shipping it's a name and an address. Forcing all three into one shared `User` table creates a monster that every team must coordinate on and nobody can change safely. The fix is to let each context keep its *own* model of the user, sharing only a stable ID across the boundary.

> 💡 **Concept notes — bounded contexts and the ubiquitous language at system scale**
> A **bounded context** draws a line around a part of the domain inside which one **ubiquitous language** holds — every term means exactly one thing, and the code, the database, and the team's conversation all use that one meaning. (The LLD track builds this naming discipline inside a single codebase; here it decides *service boundaries*.) Two signals that you're crossing a context boundary: (1) a word's meaning shifts ("order" means a shopping cart in one place and a fulfillment job in another), or (2) two areas change for entirely different reasons and at different rates. Split there. Each context becomes a candidate service that owns its data and exposes a narrow contract; contexts talk through explicit APIs or events, never by reaching into each other's tables. The payoff is the decoupling above, made organizational: teams ship independently because the boundaries match how the business actually thinks.

> 💡 **Concept notes — don't over-split (the cost side)**
> Bounded contexts are not a license to draw twenty microservices on the whiteboard. Each split you make trades local team autonomy for *distributed-systems tax* — network calls, partial failure, eventual consistency, and cross-context transactions that no longer fit in one database. The three-sentence habit applies: *why* split (two teams blocking each other, a word meaning two things), *gain* (independent deploys, clearer models), *cost* (a network and a consistency boundary where there used to be a function call). Start with a well-organized monolith whose modules follow context lines, and peel off a service only when a real number — team friction, divergent scaling needs — forces it.

---

## The meta-skill: every choice has a cost — say it

If you take one thing from Part 3, take this. For *every* component and decision, you should be able to finish three sentences:

1. **"I'm adding this because ___"** (the specific pain/number — never "best practice").
2. **"This gains us ___"** (the benefit).
3. **"And it costs us ___"** (the price — there is *always* one).

Examples you can already fill in:
- Cache → gains read speed → costs staleness + invalidation complexity.
- Replication → gains read scale + failover → costs replication lag.
- Sharding → gains size + write scale → costs cross-shard queries/joins/transactions.
- Queue → gains responsiveness + spike absorption → costs eventual consistency + idempotency burden.
- Strong consistency → gains correctness → costs latency + availability.

An interviewer who hears all three sentences for each box is hearing someone who *designs*, not someone who *memorized a diagram.* That's the entire game, restated one final way.

---

## What we have now

You can now *name* every tradeoff you've been making for nine chapters: latency vs throughput, the consistency spectrum, CAP/PACELC, the scaling and reliability vocabularies, coupling and idempotency, and where to draw bounded-context boundaries when a system gets too big for one team. More importantly, you have the three-sentence habit — *why, gain, cost* — for every decision.

Words are half of the interview. The other half is the picture. Chapter 11: how to *draw* a system so it's clear, and how to structure the API and data model that the drawing implies.

---

## Try it

1. Define latency and throughput, then give a concrete example of improving one while *worsening* the other.
2. Your service averages 20 ms but p99 is 1.5 s, and a typical page loads 40 resources. Roughly what fraction of page loads hit at least one slow (p99) request? Why does this make p99, not the average, the number to chase?
3. For a food-delivery app, assign a consistency model to each and justify: the restaurant menu, your live order status, the driver's GPS location, your saved payment methods.
4. A service is "highly available" but users report losing data after a crash. Explain how that's possible using availability vs durability.
5. Pick any three components from earlier chapters and write the three sentences (why / gain / cost) for each from memory.
6. Your monolith bundles Identity, Billing, and Shipping, and all three share one `User` table. Give the bounded-context boundary you'd draw, what each context's *own* model of "user" contains, and the one cost you take on by splitting them into separate services.

*Write your answers in [hld-chapter-10-tryit.md](code/hld-chapter-10-tryit.md).*

---

## The bumper sticker

> *There are no right answers in system design, only tradeoffs you can name. For every box: why you added it, what it gains, and what it costs — say all three.*

Next: turn the words into a picture. How to draw the system, define the API, and design the data model — the three artifacts every HLD interview asks you to produce.

---

<div align="right">

[Chapter 11 →](hld-chapter-11.md)

</div>
