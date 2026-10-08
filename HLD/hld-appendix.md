# Appendix: Quick reference

*[← Chapter 16](hld-chapter-16.md) · [Contents](hld-README.md)*

Five short references for after you've finished the book. Not study material — lookup material.

Looking to *re-read* rather than look something up? See the [visual deepdive](hld-visual-deepdive.md) — all sixteen chapters retold as one continuous diagram-led story. Ready to make and defend production choices? Use the [multi-region and event-driven design drills](hld-multi-region-event-driven-drills.md); they are a companion, not Chapter 17.

## A. Component catalog

Each component, one line: what it is, and the *pain* that justifies it.

**Load balancer** — spreads requests across many app servers, routes around dead ones. *For:* removing the app-tier single point of failure and scaling out. (Ch 2)

**Stateless app server** — holds no unique local state, so any instance serves any request. *For:* horizontal scaling — the precondition for adding boxes freely. (Ch 2)

**Replication (primary-replica)** — full copies of the data on many boxes; one writer, many readers. *For:* scaling reads + surviving a DB box dying. *Costs:* replication lag / stale reads. (Ch 3)

**Leader election / consensus (Raft, Paxos)** — surviving boxes agree on exactly one new primary by majority vote when the old one dies. *For:* automatic failover without split-brain (two primaries taking conflicting writes). *Costs:* wants an odd voter count + a brief election window; usually delegated to the DB or a coordinator (ZooKeeper/etcd). (Ch 3)

**Sharding (partitioning)** — split data into slices across boxes, routed by a shard key. *For:* data too big or writes too many for one box. *Costs:* cross-shard queries/joins/transactions get hard. (Ch 4)

**Consistent hashing** — map keys and nodes onto a ring so adding/removing a node moves only ~1/N of keys. *For:* growing a sharded/cached cluster without reshuffling everything. (Ch 4)

**Cache (Redis/Memcached)** — fast in-memory copy of hot data. *For:* absorbing repeated reads (the hot minority). *Costs:* staleness + invalidation complexity. (Ch 5)

**Bloom filter** — a tiny probabilistic set (bit array + *k* hashes) that answers "definitely not present" or "maybe present." *For:* cheaply rejecting lookups for keys that don't exist (cache penetration) before they touch the DB. *Costs:* false positives are possible (false negatives never), and the classic version can't delete. (Ch 5)

**Message queue (SQS/RabbitMQ/Kafka)** — holds work to be done asynchronously by workers. *For:* fast responses, spike absorption (load leveling), failure isolation. *Costs:* eventual consistency + idempotency burden. (Ch 6)

**Blob/object storage (S3)** — cheap, durable storage for large files by key. *For:* big files (images, video) — keep bytes out of the database. (Ch 9)
**CDN** — caches static files at edge locations near users. *For:* serving large/static content fast worldwide + offloading origin bandwidth. (Ch 9)

**Rate limiter** — caps requests per client at the edge. *For:* stopping abuse/runaway clients from taking everyone down. (Ch 8)

**Backpressure** — the system's reaction to real-time overload: reject or slow down work it can't handle so load is shed deliberately instead of cascading into an outage. Mostly *implicit* — a full bounded queue, an exhausted connection pool, or a shrinking TCP window makes the upstream call *block*, and that blocking is the signal (no notification-handler code). *Explicit parts:* priority/load-shedding rules (what to sacrifice), circuit breakers, and retry-with-backoff. (Ch 8)

**WebSocket gateway** — holds persistent bidirectional connections so the server can push. *For:* real-time delivery (chat, live tracking). *Costs:* introduces connection state. (Ch 15)

**Geospatial index (geohash/quadtree/H3)** — index entities by location for "what's nearby?" queries. *For:* matching by physical location. (Ch 16)

**Write-ahead log (WAL)** — append every change to a sequential log and fsync it *before* updating the main data files. *For:* making on-disk durability cheap (sequential append) and crash recovery possible (replay the log on restart); it's also the stream replicas follow. (Ch 7)

**Storage engine (B-tree vs LSM-tree)** — how a single database lays data on disk. B-tree updates in place (read-heavy, range scans); LSM-tree buffers writes and flushes sorted files merged in the background (write-heavy ingest). *For:* matching the engine to the workload's read/write profile. (Ch 7)

**Bounded context** — a domain-shaped boundary that owns one part of the system with its own data and its own consistent vocabulary; the unit you split services along. *For:* breaking a system up when teams block each other or a word ("user", "order") means different things in different places. *Costs:* a network + consistency boundary where there was a function call. (Ch 10)

**Managed cloud service** — rent a building block (database, cache, queue, blob store, load balancer) that the provider provisions, patches, and fails over for you. *For:* skipping undifferentiated ops work — reach for "a managed queue (SQS)" over "my own Kafka" unless you can justify the operational cost. *Terms:* IaaS (raw machines) → PaaS (managed service) → serverless (per-request execution, scales to zero); spread replicas across **availability zones** within a **region** so one datacenter failure can't take you down; **autoscaling** adds/removes instances as load moves. (Ch 9)

**CI/CD pipeline** — on every push, automatically build, test, and ship the change through one un-skippable path. *For:* making releases small, frequent, and boring instead of rare and scary — so a bad deploy is easy to find and undo. (Ch 12)

**Container (Docker)** — bundle the app *plus its whole environment* into one immutable image. *For:* killing "works on my machine" and making rollback = redeploy the previous image. *Costs:* an image build/registry step. (Ch 12)

**Orchestrator (Kubernetes)** — you *declare* desired state ("10 healthy replicas"); it reconciles reality to match — restarting, rescheduling, rolling out, scaling. *For:* running many containers across many machines without hand-babysitting. (Ch 12)

**Observability (metrics / logs / traces)** — the system reports how it feels: numbers over time, event records, and per-request paths across services. *For:* debugging a live system instead of guessing. *Watch the golden signals:* latency, traffic, errors, saturation. (Ch 12)

**SLI / SLO / error budget** — measure reliability (indicator), set a target (objective), and treat the allowed-failure remainder as a spendable budget. *For:* defining "reliable enough" as a number — under budget, ship fast; over budget, freeze and harden. (Ch 12)

**Release strategy (rolling / blue-green / canary)** — expose a new version gradually rather than to 100% at once. *For:* shrinking the blast radius of a bad deploy and making rollback fast. *Canary* pairs with observability: ship to 1%, watch metrics, ramp or roll back. (Ch 12)

**Infrastructure as Code (Terraform)** — describe the infrastructure in a version-controlled file; a tool makes the cloud match it. *For:* reproducible, reviewable, self-documenting environments instead of un-repeatable console clicks. (Ch 12)

---

## B. Numbers every engineer should know

Memorize these orders of magnitude. They power every estimate.

**Latency ladder (the most important table in the book):**

| Operation | Time | Mental model |
|---|---|---|
| L1 cache reference | ~1 ns | instant |
| Main memory (RAM) read | ~100 ns | very fast |
| Read 1 MB from RAM | ~10 µs | |
| SSD random read | ~100 µs | |
| Network round-trip (same datacenter) | ~0.5 ms | |
| Read 1 MB from SSD | ~1 ms | |
| Disk (HDD) seek | ~10 ms | slow |
| Read 1 MB from disk | ~20 ms | |
| Network round-trip (cross-continent) | ~150 ms | very slow |

The one takeaway: **memory is ~100,000× faster than disk, and crossing a continent costs ~150 ms.** This is *why* caches exist (Ch 5) and *why* CDNs exist (Ch 9).

**Estimation toolkit:**
- Seconds in a day ≈ **100,000** (10⁵). Daily total ÷ 100,000 ≈ per-second rate.
- Thousand 10³ · Million 10⁶ · Billion 10⁹ · Trillion 10¹².
- 1 char ≈ 1 byte; a typical DB row ≈ hundreds of bytes; an image ≈ MBs; a video ≈ GBs.

**Capacity rules of thumb (rough — for sizing, not precision):**
- One app server: ~1,000 simple requests/sec.
- One database box: ~thousands of reads/sec, fewer writes.
- One cache box: ~100,000+ reads/sec (it's memory).
- Always provision **N+1**: enough to lose one box and still serve peak.

**Availability ("nines"):**

| Nines | Downtime/year |
|---|---|
| 99% | ~3.65 days |
| 99.9% | ~8.76 hours |
| 99.99% | ~52 minutes |
| 99.999% | ~5 minutes |

---

## C. The six-step interview ritual (the core loop)

```
1. Clarify    → functional + non-functional requirements (ask, don't assume)
2. Estimate   → reads/sec, writes/sec, storage/year (daily ÷ 100,000)
3. API + data → endpoints + entities; SQL vs NoSQL by access pattern
4. HLD        → diagram grown from one box; trace read path AND write path
5. Deep dive  → zoom into the 1–2 hardest components on demand
6. Tradeoffs  → name the next bottleneck and what each choice cost
```

The non-functional requirements (step 1) and the numbers (step 2) are what *justify* the architecture. Skipping straight to drawing boxes is the #1 way candidates look junior.

### The three-sentence habit (do this for every component)
1. "I'm adding this because ___" (a specific number/failure — not "best practice").
2. "It gains us ___."
3. "It costs us ___." (There is always a cost.)

---

## D. The signature lessons (one per worked problem)

- **URL shortener (Ch 13):** unique code generation — *counter + base62, hand out ID ranges* to kill collisions and the central bottleneck.
- **News feed (Ch 14):** **fanout** — *push for the masses, pull for celebrities, merge at read time.*
- **Chat (Ch 15):** **real-time delivery** — *persistent WebSocket connections + a user→gateway registry + persist-then-deliver.*
- **Ride-sharing (Ch 16):** **geospatial** — *geohash index for "find nearby" + ephemeral in-memory locations + atomic match.*

These four patterns (unique-ID, fanout, real-time push, geospatial) plus the component catalog cover a huge fraction of HLD interview questions. Most new problems are a recombination of these.

---

## E. Common pitfalls

**Skipping estimation.** Jumping to architecture without numbers. The numbers *are* the justification — without them every component is unmotivated. Always do step 2.

**Over-engineering / pattern-dropping.** Drawing Kafka, sharding, and microservices for a problem that needs one box and a database. The discipline of the whole book: *add a component only when a number or failure forces it.* "This doesn't need sharding, replication is enough" is a senior answer.

**Premature sharding.** Sharding is a tax you pay forever (cross-shard joins/transactions). Don't reach for it until data size or write volume actually exceeds one box. Replication first.

**Ignoring the single point of failure.** Adding a component to remove one SPOF while creating another (a single load balancer, a single primary) and not noticing. For every box, ask "what if this dies?"

**Forgetting statelessness.** Putting session/state on app servers, breaking horizontal scaling. State goes in a shared tier (cache/DB/blob), app servers stay disposable.

**Claiming "CA" or "this system is consistent."** Consistency is chosen *per feature*, not per system, and CA isn't real at scale. Say "CP for the balance, AP for the feed."

**Treating the diagram as a silent deliverable.** Narrate as you draw, grow it from need, invite the interviewer in. It's a conversation, not a painting.

**Forgetting idempotency.** Queues redeliver and clients retry; handlers must be idempotent (dedupe on a unique ID). The phrase interviewers wait for.

**Hand-waving failover.** Saying "a replica just takes over" without saying *how*. Automatic promotion needs **leader election by consensus (majority vote)**; without it, two replicas can both believe they're primary — **split-brain** — and accept conflicting writes. Name the mechanism, and prefer an odd voter count. (Ch 3)

**Splitting on the wrong lines.** When you *do* break up a system, split by **domain (bounded contexts)**, not by technical layer. A "database service + logic service + API service" split makes one feature change touch all three; a split along Identity / Billing / Shipping lets each team ship alone. The tell for a real boundary: a word means different things on each side. (Ch 10)

**Optimizing the wrong metric.** Chasing average latency when the tail (p99) is what users feel; optimizing throughput when the problem cares about latency. Ask which one matters first.

**Hand-waving the deploy and the 2am page.** Drawing a perfect diagram but going blank on "how do you ship it, know it's healthy, and roll it back?" Have the four answers ready: CI/CD + canary for releases, golden-signal metrics/logs/traces for health, an SLO + error budget for "reliable enough," and immutable images for instant rollback. (Ch 12)

## F. The 35-minute interview budget

A typical HLD interview is ~45 minutes. After intros, you have ~35 minutes of design time. Rough budget:

- **5 min** — clarify requirements (functional + non-functional)
- **5 min** — estimate (load, storage, the key numbers)
- **5 min** — API + data model + SQL/NoSQL
- **10 min** — high-level design (draw it, grown from simple, trace the flows)
- **7 min** — deep dive into the hard component(s)
- **3 min** — bottlenecks + tradeoffs (close strong)

Stay roughly within these. If you spend 15 minutes on requirements, you'll have nothing drawn. Move on even when uncertain — state an assumption and proceed: *"I'll assume single-region for now and revisit."* That's a valid, senior move.

---

## G. Final notes

The components in this book are the foundation, not the ceiling. Once you've internalized them, you'll see them everywhere — in the systems you use, in design docs at work, in your own past architectures.

The skill you're really building isn't "knowing components." It's *deriving the architecture from the pains* — adding each box because a number or a failure demanded it, and naming what it cost. That's what an interviewer is actually scoring, and it's what makes you good at the real job, not just the interview.

That comes from reps. Lots of them. Across many problems. Run the six-step ritual until it's muscle memory. The understanding arrives quickly; the automatic recognition takes months. Be patient — and trust it.

> *Architecture is the set of moves you make so the system bends instead of breaks when the traffic lands.*
