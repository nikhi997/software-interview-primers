# HLD Visual Deepdive — Chapters 1–16 in one flow

*[← Chapter 16](hld-chapter-16.md) · [Contents](hld-README.md)*

This is a visual retelling of the whole HLD primer in one continuous arc. Nothing here is new — every number, move, and cost comes from a chapter you've already read. What's new is the *shape*: a system that starts as a single box and grows into a sharded, cached, queued, replicated thing you could defend on a whiteboard, with each step visible.

Read it top to bottom in one or two sittings. Then use it the way the [study contract](hld-README.md) intends: close the file, redraw the diagrams from memory, and diff. Each section links its source chapter for when you want the depth back.

> *Architecture is the set of moves you make so the system bends instead of breaks when the traffic lands.*

In Part 1 the architecture genuinely grows: each section makes one architectural move on the system the previous section left behind, always in response to a number you could name. From Part 2 on, the diagrams alternate — some add a component to that skeleton, others zoom in on a mechanism (how a write-ahead log works, what a token bucket does), and Part 4 composes the finished vocabulary into specific systems. If you can say why every move happened and what it cost, you know this book.

---

## Part 1 — Foundation

Four chapters, four boxes. This part builds the skeleton every large system shares. Nothing exotic: one machine, then more machines, then copies of the data, then splits of the data.

### 1.1 Everything on one server — [Chapter 1](hld-chapter-1.md)

**The problem:** none, yet. That's the point. The instinct on day one is to draw a load balancer and a cache and three services. Resist it.

**Diagram 1 — one box does everything:**

```
client ──▶ ┌──────────────────────────┐
           │  ONE SERVER              │
           │  web + app + database    │
           │  + files on local disk   │
           └──────────────────────────┘
```

Before you touch this, do the arithmetic. **Back-of-the-envelope estimation** is not a ritual — it's what gives you *permission to stay simple*. For a URL shortener at 1 million new URLs/day, with ~100 reads per write:

```
1,000,000 writes/day ÷ 100,000 sec/day  =  10 writes/sec
10 writes/sec × 100                     =  1,000 reads/sec
500 MB/day × 365                        ≈  180 GB/year  (under 1 TB in 5 years)
```

Ten writes a second. A thousand reads a second. Under a terabyte for years. **One box is fine.** "One million a day" *sounds* enormous and turns out to be nothing — that gap is exactly what the estimate exists to expose.

> 💡 **The seconds-in-a-day trick:** a day is ≈ 100,000 seconds (10⁵). Any daily total divided by 100,000 gives you the per-second rate. This one number powers every estimate in the book.

**The first real crack** isn't traffic — it's that the app and the database compete for the same CPU and RAM on the same box, and you can't scale one without the other.

**The move:** split them.

**Diagram 2 — app and database on separate boxes:**

```
client ──▶ ┌──────────────┐  ──▶  ┌──────────────┐
           │  app server  │       │   database   │
           └──────────────┘  ◀──  └──────────────┘
                          network hop
```

**The cost:** what used to be an in-process call is now a network round-trip — microseconds become ~0.5 ms inside a datacenter. You bought independent scaling and paid a millisecond.

**The next pain:** two boxes, two single points of failure. Either dies and you're down.

### 1.2 Many app servers — [Chapter 2](hld-chapter-2.md)

**The problem:** one app server is both a SPOF and a ceiling. Traffic climbs toward 50,000 reads/sec; one box handles ~1,000 requests/sec.

**The move:** run many identical app servers behind a **load balancer**. This only works if the servers are **stateless** — holding no unique data, so any request can go to any server.

**Diagram 3 — the stateless app tier:**

```
              ┌──────────────┐
client ──────▶│     load     │──▶ app server A ──┐
client ──────▶│   balancer   │──▶ app server B ──┼──▶ database
client ──────▶│ (redundant)  │──▶ app server C ──┘
              └──────────────┘
```

The arithmetic is now a division: 50,000 reads/sec ÷ 1,000 RPS per server = 50 servers, **plus one** — you always provision **N+1** so losing a box doesn't push the survivors past their limit and cascade.

**The cost:** the app can no longer hold anything in local memory that matters — sessions, uploaded files, in-process caches all have to move somewhere shared. Session data goes to Redis or a signed token the client carries; uploaded files go to shared storage (which becomes Ch 9). Statelessness isn't free; it's a constraint you accept in exchange for being able to add boxes without thinking.

And notice the load balancer became the new SPOF, so it's redundant too. **Every box you add to kill a single point of failure, check that it isn't a new one.**

**The next pain:** fifty app servers, one database. We moved the problem one tier right.

### 1.3 Replication — [Chapter 3](hld-chapter-3.md)

**The problem:** the database is both the bottleneck and the SPOF. And you *can't* fix it the way you fixed the app tier — app servers were multipliable precisely *because* they gave up state. A database exists to hold state. Run three and round-robin, and a write lands on box 1 while the read hits box 2, which has never heard of it.

There are two genuinely different moves, and confusing them is the classic mistake:

- **Replication** — full copies of the same data on many boxes. Fixes read capacity and survival.
- **Sharding** — the data split into pieces, each box holding a different piece. Fixes size and write capacity.

Read-heavy systems reach for replication first.

**Diagram 4 — primary and replicas:**

```
                          ┌──▶ replica 1 ─┐
LB ─▶ app servers ─writes─▶ PRIMARY        │ reads spread
                  └─reads──┼──▶ replica 2 ─┤ across replicas
                          └──▶ replica 3 ─┘
```

One **primary** takes all writes and streams every change to the **replicas**, which serve reads only. For our 100:1 read:write ratio this fits perfectly — the 1% that are writes barely tickle the primary, and the 99% that are reads spread across as many replicas as you want. If the primary dies, one of the replicas is promoted in its place.

**The cost: replication lag.** A write is on the primary but not yet on replica 2 — usually milliseconds, never zero. That gap produces the read-your-own-writes bug: a user edits their profile, the read hits a stale replica, and their change appears to have vanished.

**The fix:** route that user's reads to the primary for a short window after their write. Everyone else keeps reading replicas.

**Failover is not automatic magic either.** When the primary dies, the remaining replicas run a **leader election** to agree on which of them is promoted — and during that window, writes are refused. It's also possible for the old primary to come back believing it's still in charge, so the mechanism has to fence it off. You don't implement this in an interview; you name it, and you name the cost: **a short write outage during promotion.**

**The next pain:** still **one** primary for all writes, and **every** box holds the **full** dataset. When write volume or data size outgrows a single box, copying can't save you.

### 1.4 Sharding — [Chapter 4](hld-chapter-4.md)

**The problem:** the data won't fit one disk, or the write rate exceeds one primary. Copying doesn't help. You have to split.

The hard question is *which shard holds this row?* The obvious answer — `hash(key) mod N` — is a trap. Change N from 4 shards to 5 and almost every key's `mod` result changes, so **almost all your data has to move.** That's the resharding catastrophe.

**The move: consistent hashing.** Map both keys and shards onto a ring, and a key belongs to the first shard clockwise from it.

**Diagram 5a — the ring:**

```
        0/360°
          ┌───── Shard A
    Shard │
     C    ●         ● key "alice"  ──clockwise──▶ Shard B
          │
          ●  Shard B
```

Add a shard and it drops onto one spot; only the keys in the arc just before it move. **Adding a shard relocates ~1/N of the keys, not nearly all of them.** (Real systems hash each physical shard onto many ring positions — **virtual nodes** — so the arcs stay even.)

**Diagram 5b — the full scalable skeleton:**

```
                   ┌─ shard 1 (primary + replicas)
LB ─▶ app servers ─┼─ shard 2 (primary + replicas)   ← consistent hashing
                   └─ shard 3 (primary + replicas)      picks the shard
```

**The cost is real and worth naming out loud:** cross-shard queries, joins, and transactions all become hard, because the rows you want now live on different machines. Pick the **shard key** to match your dominant query so most reads touch one shard.

Getting that key wrong produces the failure everyone dreads: a **hot shard.** Shard a social app by `country` and one shard holds a third of your users while another sits idle — you bought machines and got no capacity. Shard by something high-cardinality and evenly distributed that also matches how you read, and the load spreads on its own. This is why the chat system later shards by `conversation_id`: it's even, *and* it makes "load this chat" a single-shard read.

> 💡 **Concept note — replication and sharding are answers to different questions.** Reads too heavy or need failover? Replicate. Data too big or writes too heavy? Shard. Large systems do both — shard for size, replicate each shard for reads and survival. Never offer one as a fix for the other's problem.

**Part 1 checkpoint:** cover the page. Can you redraw Diagram 5b from memory and say, for each box, why it exists and what it cost you?

> *Replication copies, sharding splits. Choose based on whether you're fixing reads or writes — never both with one move.*

---

## Part 2 — Components through bottlenecks

Part 1 solved *capacity*. This part is about *speed, decoupling, durability, and behaving well under abuse.* Every component below enters because of a specific number.

### 2.1 Caching — [Chapter 5](hld-chapter-5.md)

**The problem:** the same popular link is fetched a million times, and every single fetch walks the full path to a disk. Memory is roughly **100,000× faster than disk.** Doing the slow thing repeatedly for an answer that never changes is pure waste.

**The move: cache-aside.** Check memory first; on a miss, read the database and remember the answer.

**Diagram 6 — hit path vs miss path:**

```
HIT  (≈99% of reads)
  client ──▶ app ──▶ cache ──▶ value  (sub-millisecond)

MISS (the rest)
  client ──▶ app ──▶ cache  ✗
                      └────▶ database ──▶ value
                                 └──▶ write it into the cache on the way back
```

```
read(key):
    value = cache.get(key)
    if value is not None:        # CACHE HIT
        return value
    value = database.get(key)    # CACHE MISS
    cache.set(key, value)        # remember it for next time
    return value
```

Caches work because access is **skewed** — a small hot minority accounts for most reads. Hold that minority in memory and you absorb the overwhelming majority of traffic before it reaches a disk.

**The cost: the copy can be wrong.** Now you own **invalidation** — when the underlying data changes, something has to evict or refresh the cached copy. The lever is **TTL** (let entries expire; simple, accepts a window of staleness) versus **explicit invalidation** (delete on write; fresher, but every write path must remember to do it).

The cache is also small on purpose — that's what makes it fast — so it needs an **eviction policy** (LRU is the default) to decide what to drop when full.

Two failure modes are worth knowing by name, because they're standard follow-up questions. A **cache stampede** (thundering herd) happens when a hot key expires and a thousand concurrent requests all miss simultaneously and all hit the database at once — the very spike the cache existed to prevent. The fix is to let only one request rebuild the entry while the others wait, or to refresh hot keys slightly before they expire. **Cache penetration** is repeated lookups for keys that don't exist anywhere — a scanner trying random short codes — so every one is a guaranteed miss that reaches the database; the fix is to cache the "not found" answer too, or to put a **Bloom filter** in front.

> 💡 **Concept note — why a Bloom filter is the right gate.** It answers one question in tiny space: *have I definitely never seen this key?* False positives are possible; **false negatives are not.** So a "no" is always safe to trust, and a scanner's invented code is rejected before it ever touches the database. It stores no values, only bits — which is exactly why it's cheap enough to sit in front of everything.

### 2.2 Queues and async work — [Chapter 6](hld-chapter-6.md)

**The problem:** work that the user doesn't need finished is making the user wait anyway.

```
user clicks "Sign up"
  → create the account in the database        (50 ms)
  → send a welcome email                       (800 ms)
  → generate their profile thumbnail           (1,200 ms)
  → add them to the analytics pipeline         (300 ms)
  → finally... return "Welcome!"               total: ~2.4 seconds
```

The account existed after 50 ms. The other 2.35 seconds were spent on things the user doesn't care about.

**The move:** hand the slow work to a **message queue** and answer now.

**Diagram 7 — sync path vs async path:**

```
BEFORE:  app ──▶ email ──▶ thumbnail ──▶ analytics ──▶ respond   (2.4 s)

AFTER:
                          ┌─────────────┐      ┌──────────┐
app server ──"send email"─▶│    QUEUE    │─────▶│ worker 1 │
app server ──"make thumb"─▶│ (messages   │─────▶│ worker 2 │
app server ──"log signup"─▶│  waiting)   │─────▶│ worker 3 │
                          └─────────────┘      └──────────┘
   returns "Welcome!" in 50 ms                 (slow work, later)
```

Beyond speed you get two things worth naming: **spike absorption** (a traffic surge grows the queue instead of melting the workers) and **failure isolation** (the email provider being down no longer breaks signup).

**The cost:** you traded *"done"* for *"will be done."* Queues typically deliver **at least once**, which means a message can arrive twice, which means your handlers must be **idempotent** — processing the same message twice must have the same effect as once. And the user's thumbnail is now eventually consistent.

**The decision rule:** if the user needs it to get their answer, do it synchronously. If not, queue it.

Two flavors are worth distinguishing. A **task queue** (RabbitMQ, SQS) hands each message to one worker and deletes it when done — right for "do this job." A **log** (Kafka) keeps an ordered, replayable record that many independent consumers read at their own pace — right for "this event happened, and several systems care." Reach for the log when more than one consumer needs the same stream, or when you want to replay history.

### 2.3 Durability and CAP — [Chapter 7](hld-chapter-7.md)

**The problem:** we keep saying a write is "saved." Saved *where*, exactly, and what survives?

**Durability** is a dial, and every step up costs latency:

1. Acknowledge after it's in one box's **memory** — fastest, lost if the box dies.
2. Acknowledge after it's on one box's **disk** — survives a crash, lost if the disk dies.
3. Acknowledge after it's on **multiple boxes** — survives any single box, and is slowest.

Match the level to the cost of losing the data. A like counter sits at 1. A bank transfer sits at 3.

That third level is a choice you make explicitly at the replication layer. **Asynchronous replication** acknowledges as soon as the primary has the write — fast, but if the primary dies before replicating, that write is gone. **Synchronous replication** waits until at least one replica also has it — survives the primary dying, at the cost of a network hop in the user's path. Most real systems land in the middle with a **quorum**: with N copies, require each write to land on W of them and each read to consult R of them, chosen so that **W + R > N**. The read set and write set must then overlap, so any read is guaranteed to *reach* at least one copy holding the latest write — the reader then compares versions across the R responses and returns the newest. N=3, W=2, R=2 is the classic setting: it tolerates one box being down and still lets a read find the current value.

Level 2 is only affordable because of one trick:

**Diagram 8 — the write-ahead log:**

```
write ──▶ append to LOG (sequential, one file, fsync)  ──▶ "durable, ack the user"
                │
                └──(later, in background)──▶ fold into the main data files

crash? ──▶ on restart, REPLAY the log
```

Appending to the end of one file is about the fastest thing a disk can do. Notice this log looks exactly like the replication stream from Ch 3 — it *is* the same ordered stream of changes, which is why a replica can simply follow it.

Underneath, storage engines are **B-trees** (sorted, updated in place — good for reads and range scans) or **LSM-trees** (buffer in memory, flush sorted files, merge in background — turns random writes into sequential ones). Rule of thumb: **B-tree for read-heavy, LSM-tree for write-heavy ingest.**

Then the big one. The moment data lives on multiple boxes over a network, that network **will** partition.

**Diagram 9 — CAP during a partition:**

```
   user writes X=2                        user reads X
        │                                      │
        ▼                                      ▼
   ┌───────────┐        ✗ link down       ┌───────────┐
   │   DC 1    │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─▶ │   DC 2    │  (still has X=1)
   └───────────┘                          └───────────┘

   CP: DC 2 answers "I can't guarantee I'm current"  → error, no wrong answers
   AP: DC 2 answers "X=1"                            → always answers, may be stale
```

Partition tolerance isn't optional, so the real question is binary: **during a partition, do you give up consistency or availability?** Money → CP (no answer beats a wrong answer). Social feed → AP (a stale answer beats an error).

The interview-grade version is never *"this system is CP."* It's *"the balance check is CP because a stale balance is dangerous; the like count is AP because a stale like count is harmless."* **Same system, chosen per feature.**

**PACELC** adds the part CAP omits: *if Partition, choose A or C; Else, choose Latency or Consistency.* Even with a perfectly healthy network, keeping copies in lockstep costs latency. The tradeoff is always there, not just during failures.

### 2.4 Rate limiting and backpressure — [Chapter 8](hld-chapter-8.md)

**The problem:** two different overloads. A single client hammering you (abuse, a runaway script), and the system as a whole receiving more than it can serve.

**The move for the first: a rate limit per client key.** Know **token bucket** cold.

**Diagram 10 — token bucket:**

```
bucket capacity B = 10 tokens, refill R = 1 token/sec

  [●●●●●●●●●●]  full          10 requests at once → all allowed  (burst absorbed)
  [          ]  empty         11th immediately     → 429 "slow down"
  [●●●●●     ]  5 sec later   5 refilled           → 5 more allowed
```

Bucket capacity is how big a **burst** you tolerate; refill rate is the **sustained** rate you allow. Limit by API key, user ID, or IP — pick the key that identifies the abuser. Know the alternatives by name: **fixed window** (simplest, but lets a double-rate burst through at the window edge), **sliding window** (fixes that edge case, costs more bookkeeping), and **leaky bucket** (drains at a constant rate, smoothing output rather than allowing bursts).

**The move for the second: backpressure.** And the subtle point most people miss — backpressure is mostly *implicit*, falling out of resources already in the request path rather than arriving as a notification you subscribe to. A **bounded queue** that's full stops accepting; an exhausted **connection pool** stops handing out connections; a saturated receiver shrinks the TCP window. Each layer slows down simply because its call into the layer below stops making progress, and the slowdown propagates upstream with no listener code anywhere.

Which is why the real work is choosing what "stops making progress" *means* at each point. Blocking forever is its own outage — held request threads pile up until the service is wedged. So you **bound the queues, size the pools, and set timeouts**, and decide deliberately whether a full queue blocks briefly, rejects immediately, or sheds. A rejection is a healthy backpressure signal; an unbounded wait is a disguised failure.

What *is* explicit is priority — the system can't infer which work matters. That's your **graceful degradation** kit: **load shedding** (drop analytics before checkout), **circuit breakers** (stop calling a failing dependency, fail fast, retest after a cooldown), degraded responses (stale data, "recommendations unavailable" while the page still loads), and **bounded queues** — an unbounded queue under overload grows until it exhausts memory, turning a slowdown into an outage.

**The cost:** rejected requests. Some users see 429s or a reduced experience — you're deliberately choosing who to disappoint instead of letting the system choose randomly by falling over.

> 💡 **Concept note — the retry storm.** Naive retries make overload worse: errors trigger immediate retries, retries multiply load, the service drowns. Say **"retry with exponential backoff and jitter,"** plus a retry cap. Interviewers listen for that exact phrase.

### 2.5 Blob storage and CDN — [Chapter 9](hld-chapter-9.md)

**The problem:** two instincts that break at scale. Storing files *in* the database bloats it, wrecks its cache, and makes backups miserable. Serving files *from* your app servers burns app-server bandwidth on bytes that need no logic — and a user in Tokyo pays a **cross-continent round trip** to Virginia for every image, the slowest rung on the [latency ladder](hld-appendix.md).

**The move:** big bytes go in **blob storage** (S3 and friends), the database keeps only a pointer, and a **CDN** caches copies at edges near users.

**Diagram 11 — where the bytes actually live:**

```
database row:
  user_id: 123
  avatar_url: "https://cdn/avatars/123.jpg"   ← just a string. Bytes live in S3.

UPLOAD (app never touches the bytes):
  client → app: "uploading avatar"
  app    → client: PRE-SIGNED URL
  client → blob storage: PUT the bytes  (direct)
  blob storage → app: "upload complete"  (event, or the client tells it)
  app    → database: save the pointer

SERVE:
  Tokyo user ─ 5 ms ─▶ Tokyo edge cache ─(only on miss)─▶ Virginia origin
  Osaka user ─ 8 ms ─▶ Tokyo edge cache  (already warm)
```

The **pre-signed URL** is the elegant part: a short-lived permission to write one specific object, so the client uploads straight to blob storage and your app servers never see the file. Note the completion step — the app can't record the pointer until it *knows* the bytes landed, so it waits for an object-store event or the client's confirmation.

**The cost:** eventual consistency at the edges. Change a file and edges keep serving the old one until their TTL expires — which is why production systems version filenames rather than overwrite them.

**Diagram 12 — the complete component vocabulary:**

```
                         ┌── CDN (static files, near users)
client ──▶ load balancer ─┤
                         └─▶ app servers (stateless)
                               ├─▶ cache (hot reads)
                               ├─▶ database (sharded + replicated metadata)
                               ├─▶ blob storage (big files)
                               └─▶ queue ─▶ workers (async work)
            + rate limiting / backpressure protecting it all
```

> 💡 **Concept note — you rent most of these boxes.** Notice how many of them named a product: S3, Redis, CloudFront. You rarely *build* a load balancer or an object store; you rent a **managed service**, because provisioning, patching, failover, and capacity planning are undifferentiated work that has nothing to do with your product. Worth being able to place: **IaaS** (rent raw machines), **PaaS** (rent a managed database or queue), **serverless** (rent per-request execution, scaling to zero). And two that are load-bearing for every failover claim in this document — a **region** is a geographic location, an **availability zone** is an isolated datacenter *within* a region, and you spread replicas **across AZs** so losing one datacenter doesn't take you down. That's Ch 2's "remove the single point of failure," at datacenter granularity. None of this changes the method: the cloud changes *who operates the box*, never *why it exists*.

**Part 2 checkpoint:** take a new problem — a photo-sharing app at scale. Which 3–4 of these components does it need, and what *specific number* justifies each?

> *Cache the hot minority, queue the async work, rate-limit the surge, CDN the files. Each solves a specific bottleneck, and each has a specific cost.*

---

## Part 3 — Naming what you know

You've been making tradeoffs for nine chapters. This part gives them names, teaches you to draw them, and covers what happens after the design ships.

### 3.1 The vocabulary of tradeoffs — [Chapter 10](hld-chapter-10.md)

**Latency vs throughput are not opposites** — a common muddle. Latency is how long *one* request takes; throughput is how many you handle per second. Batching raises throughput and raises latency. Adding servers primarily raises throughput; what it does to latency depends on load and architecture — under saturation it can *reduce* latency by draining queues, while extra routing or coordination layers can add some back. Say which one you're optimizing, and under what conditions.

**The consistency spectrum**, strongest to weakest: strong (every read sees the latest write) → read-your-own-writes (you see your own changes, others may lag) → eventual (all copies converge, given time). Most systems pick different points for different features.

**Diagram 13 — the why/gain/cost frame:**

```
For EVERY box on your diagram, finish three sentences:

  ┌───────────────────────────────────────────────────────────────┐
  │  I'm adding this because ___   (a number or a failure, never  │
  │                                 "best practice")              │
  │  This gains us ___             (the benefit)                  │
  │  And it costs us ___           (there is ALWAYS one)          │
  └───────────────────────────────────────────────────────────────┘
```

The ones you can already fill in:

| Component | Why | Gain | Cost |
|---|---|---|---|
| Cache | reads repeat on a hot minority | read speed | staleness + invalidation |
| Replication | reads exceed one box; box can die | read scale + failover | replication lag |
| Sharding | data or writes exceed one box | size + write scale | cross-shard queries, joins, transactions |
| Queue | work doesn't block the answer | responsiveness + spike absorption | eventual consistency + idempotency |
| Strong consistency | a wrong answer is dangerous | correctness | latency + availability |
| CDN | users are far from the origin | edge latency | edge staleness |

An interviewer who hears all three sentences per box is hearing someone who *designs*. One who hears only box names is hearing someone who memorized a picture.

Two more pieces of vocabulary you'll need in Part 4. **Availability in nines** is how reliability gets quantified — 99% is ~3.65 days of downtime a year, 99.9% is ~8.76 hours, 99.99% is ~52 minutes, 99.999% is ~5 minutes. Each additional nine is dramatically harder and more expensive than the last, which is why nobody sane targets 100%. And **idempotency** — an operation you can safely repeat with the same result — is what makes retries and at-least-once queues survivable. Any time you say "we'll retry" or "the queue delivers at least once," the interviewer's next question is *how do you avoid double-charging that customer*, and "idempotency key on the request" is the answer.

**And one question this part answers that isn't about scale at all:** eventually the interviewer stops asking "how do you scale this box?" and asks "how would you *break this up*?" The tempting split is by technical layer — an API service, a logic service, a data service — and it fails immediately, because one feature change touches all three. Split by **domain** instead. The name for a domain-shaped boundary is a **bounded context**, and the tell that you've found a real one is that **the same word means different things on either side of it**: "user" is a login and a password hash to Identity, an account with a payment method to Billing, a name and an address to Shipping. Force those into one shared table and every team has to coordinate on it forever.

The cost side matters just as much, and it's where most candidates overreach. Every split trades team autonomy for **distributed-systems tax** — network calls, partial failure, eventual consistency, and transactions that no longer fit in one database. Start with a well-organized monolith whose modules follow context lines, and peel off a service only when a real number forces it. Drawing twenty microservices unprompted reads as inexperience, not ambition.

### 3.2 Drawing the system — [Chapter 11](hld-chapter-11.md)

Three artifacts win an HLD interview, and the diagram is only one of them.

**Diagram 14 — the canonical skeleton (and the anatomy of a system diagram):**

```
            ┌─────────────┐
  clients   │     CDN     │ (static files)
    │       └─────────────┘
    ▼
┌─────────────────┐
│  load balancer  │
└────────┬────────┘
         ▼
┌─────────────────┐      ┌──────────┐
│  app servers    │─────▶│  cache   │  (hot reads)
│  (stateless)    │      └──────────┘
└───┬─────────┬───┘
    │         │          ┌──────────────────────┐
    │         └─────────▶│  database            │
    │                    │  (sharded+replicated)│
    │                    └──────────────────────┘
    │                    ┌──────────┐
    └───────────────────▶│  queue   │──▶ workers ──▶ blob storage,
                         └──────────┘                 email, etc.
```

Boxes are components, arrows are data flow, labels say what flows. Client on the left, stores on the right. **But do not draw this whole thing at once.** Start with three boxes — client, app, database — and add each component *as you narrate the pain that demands it*. A diagram that grows from need is far more convincing than one produced whole, because the interviewer is scoring the reasoning, not the picture.

**Artifact 2, the API**, pins the scope before you design anything: the endpoints, what goes in, what comes back. **Artifact 3, the data model**, is justified by the *access pattern* — "we look up by key, no joins, enormous scale, so a key-value/wide-column store" is a justification; "I'd use Postgres" is a preference.

Then trace one request end-to-end with your finger. If you can do that, the diagram is doing its job.

### 3.3 Keeping it running — [Chapter 12](hld-chapter-12.md)

The design is drawn. Now it has to *survive contact with production*, and each piece of "DevOps" exists because of one specific 2am pain.

| The pain | The move |
|---|---|
| "I shipped a bug because I skipped the tests" | **CI/CD** — automated build, test, deploy |
| "It worked in test, prod has a different Python" | **Containers** — the environment ships inside the artifact |
| "I'm restarting crashed containers by hand all night" | **Orchestration** — declare N healthy copies, let it self-heal |
| "It's live and I have no idea if it's healthy" | **Observability** — metrics, logs, traces |
| "Is it reliable *enough*?" | **SLI / SLO / error budget** — make it a number |
| "I shipped to everyone and broke everyone" | **Release strategies** — small blast radius |
| "I built prod by clicking and can't reproduce it" | **IaC** — the environment as code |

**Diagram 15 — the pipeline, ending in a canary:**

```
commit ─▶ CI: build + test ─▶ container image ─▶ registry
                                                    │
                                                    ▼
                                      orchestrator (declare N replicas)
                                                    │
                       ┌────────────────────────────┴──────────────┐
                       ▼                                           ▼
                 1% of traffic ──▶ NEW version            99% ──▶ OLD version
                                        │
                            watch metrics/logs/traces
                                        │
                    healthy? ─▶ ramp to 100%    unhealthy? ─▶ roll back
```

The three observability pillars divide cleanly: **metrics** tell you *something is wrong and roughly where*, **logs** tell you *exactly what happened*, **traces** tell you *which hop in the chain was slow*. Instrument the **golden signals** — latency, traffic, errors, saturation — on every service.

**SLI** is the measurement ("% of requests under 200 ms"). **SLO** is the target you choose ("99.9% succeed monthly"). **SLA** is that promise written into a contract. And the **error budget** is the flip side: 99.9% allowed means 0.1% — about 43 minutes a month — is yours to *spend*. Under budget, ship fast. Blown budget, stop shipping features and harden. It turns reliability from a virtue into a currency, and it settles the product-vs-ops argument with a number instead of an opinion.

Rolling updates, blue-green, and canary all buy the same thing — **a small blast radius**. Canary is the interview favorite because it pairs with observability: ship to 1%, watch, auto-roll-back on a spike, otherwise ramp.

> 💡 **Concept note — it's the same move three times.** CI/CD, orchestration, and IaC are all *declare the desired state, let an automated system reconcile reality to it*, instead of a human running one-off commands. Observability checks that reality matches intent; SLOs define how close it must match; release strategies make changing the intent safe.

**Part 3 checkpoint:** for a system you just designed, can you name its SLI, propose an SLO, say what the error budget buys you, and pick a rollout strategy with a reason?

> *Say why / gain / cost for every box. That's the whole game.*

---

## Part 4 — Interview-shaped

Same six steps, four problems. The ritual never changes; only the signature difficulty does.

```
1. Clarify   → what are we actually building, and what's out of scope
2. Estimate  → reads/sec, writes/sec, storage — the numbers ARE the design
3. API + data model → pin the scope, justify the store by access pattern
4. Architecture → grow the diagram, narrating each addition
5. Deep dive → zoom into whichever box they poke
6. Bottlenecks & tradeoffs → close by naming what you gave up
```

### 4.1 The ritual, on a URL shortener — [Chapter 13](hld-chapter-13.md)

**Clarify before anything else.** "Design a URL shortener" is deliberately underspecified, and the questions you ask are themselves scored. Do custom codes need to be supported? Do links expire? Do we need click analytics — real-time, or is a delay fine? How many users, and is it read-heavy? Each answer either adds a component or lets you cut one, and "analytics can lag by a few minutes" is what buys you the queue later.

**Estimate next**, because everything downstream falls out of it: 100M new URLs/day → **1K writes/sec**, at 100:1 → **100K reads/sec**, at ~500 bytes/row → **~18 TB/year**. Those numbers do the designing. 100K reads/sec screams cache plus replicas. 18 TB/year says sharding, eventually. Base62 keyspace math says **7 characters**.

**The data model justifies the store by access pattern**, not preference: lookups are by `short_code`, a single key, with no joins and no complex queries — but at enormous scale. That's the textbook case for a key-value or wide-column store that shards by key natively. At smaller scale SQL would be perfectly fine, and saying so shows you're choosing rather than reciting.

The one genuinely interesting decision is **how to generate the code.** Hashing collides and needs a check-and-retry read on every write. Random codes degrade as the keyspace fills. The clean answer is a **counter encoded in base62** — every integer is unique, so collisions are impossible and no read-before-write is needed. The catch is that a single global counter is a bottleneck and a SPOF, and the fix is elegant: **hand out ID ranges**, so each server owns a block of 1,000 and only coordinates once per 1,000 URLs. Name the SPOF and its fix in the same breath.

**Diagram 16 — the final architecture:**

```
            ┌──────────────┐
 users ────▶│ load balancer│
            └──────┬───────┘
                   ▼
         ┌───────────────────┐   429 if abusive (Ch 8)
         │   app servers     │◀──rate limiter
         │   (stateless)     │
         └──┬─────────────┬──┘
   reads    │             │   writes
            ▼             ▼
      ┌──────────┐   ┌──────────────────────┐
      │  cache   │   │ NoSQL store          │
      │ (Redis)  │   │ sharded by short_code│
      │ hot URLs │   │ + replicated         │
      └──────────┘   └──────────────────────┘
                          ▲
                   ID-range allocator (counter → base62)
   click events ──▶ queue ──▶ workers ──▶ analytics store (async, Ch 6)
```

**Trace a redirect** (the 100K/sec hot path): LB → app → cache hit ~99% of the time → 302 in a few milliseconds. On a miss, read a replica and populate the cache. **Trace a create** (1K/sec): LB → rate limiter → app → next ID from its range → base62 → write. **Clicks** don't block the redirect; they go on a queue and are aggregated by workers, eventually consistent — perfectly fine for a click count.

When they ask *"100K reads/sec on the database?"* the answer is no: the cache absorbs ~99% of them, so roughly **1,000 misses/sec** reach the replicas — a load they handle comfortably, and one you scale by adding replicas.

### 4.2 News feed — [Chapter 14](hld-chapter-14.md)

**The signature difficulty: fanout.** When you post, who does the work of assembling timelines — the writer or the reader?

**Diagram 17 — the two fanouts:**

```
FANOUT-ON-READ (pull)                 FANOUT-ON-WRITE (push)
  post → append to my own list          post → prepend into all 500
         (1 write, cheap)                      followers' timelines
                                               (500 writes, expensive)
  read → fetch 500 followees'           read → return my precomputed
         tweets, merge, sort                   timeline (1 read, trivial)
         (brutal, ×30,000/sec)
```

| | Fanout-on-read | Fanout-on-write |
|---|---|---|
| Write cost | one write | one per follower |
| Read cost | query hundreds, merge live | a single list read |
| Fits | write-heavy | **read-heavy — i.e. feeds** |

Feeds are read-heavy, so the default is **fanout-on-write**: pay once at post time so billions of reads are cheap. That's just the caching principle from Ch 5 applied at the feed level — precompute the answer.

**Until a celebrity posts.** 100 million followers means one tweet becomes 100 million writes. That's the **hot key problem**, and pure push cannot survive it.

**The hybrid is the senior answer:** push for normal users, *don't* push for celebrities, and at read time merge your precomputed timeline with a live pull of the few celebrities you follow. Normal posts stay cheap, celebrity posts don't cause a write storm, and the read-time merge is small because you follow few celebrities.

The rest of the design is components you already have: a queue plus fanout workers so the poster doesn't wait for 500 writes, a Redis timeline cache, sharded NoSQL for tweets and the follow graph, blob storage plus CDN for media.

### 4.3 Chat — [Chapter 15](hld-chapter-15.md)

**The signature difficulty flips:** it's not fanout, it's **real-time delivery and connection state.** Polling can't deliver a message in under a second at any sane cost, so the *server* must push — which means **persistent WebSocket connections**, which means **stateful** gateway servers. Everything in Ch 2 said make servers stateless; here the connection *is* the state, and you can't wish it away.

That creates a routing problem: Bob's phone is connected to gateway-42 specifically, and the server handling Alice's message needs to know that.

**Diagram 18 — gateways, registry, and sharding by conversation:**

```
  Alice's phone ══persistent WebSocket══╗
                                        ▼
                              ┌──────────────────┐      ┌─────────────────┐
                              │ gateway servers  │◀────▶│ session registry│
                              │ (hold open conns)│      │ user→gateway    │
                              └────────┬─────────┘      │ (Redis)         │
                                       │                └─────────────────┘
                              route to recipient's gateway
                                       ▼
                              ┌──────────────────┐
                              │ message service  │──▶ queue for offline
                              │ persist + route  │    delivery / fanout
                              └────────┬─────────┘
                                       ▼
                              ┌──────────────────────────┐
                              │ NoSQL: messages, inboxes  │  sharded by
                              │                           │  conversation_id
                              └──────────────────────────┘
   Bob's phone ══persistent WebSocket══╝  (on gateway-42)
```

Two decisions carry this design. **Shard by `conversation_id`** so an entire conversation's history lives on one shard and "load this chat" is a single-shard read. And **always persist before delivering** — if you push first and the phone is dead, the message is gone; persist first and it's waiting when they reconnect. A group message is just fanout again: persist once, then look up each recipient's gateway and push, queueing for those offline.

Sharding keeps a conversation together, but it doesn't by itself make delivery *ordered* or *exactly once*, and both are standard follow-ups. For ordering, assign a **monotonic sequence number per conversation** — clients then sort by it and can detect a gap and re-fetch. Note what's *not* being promised: global ordering across all conversations is meaningless and expensive; order within one conversation is the only thing anyone can perceive. For duplicates, exactly-once delivery is famously near-impossible, so you do the achievable thing instead — **at-least-once plus a unique message ID**, and the client dedupes. This is Ch 6's idempotency, arriving in a new costume.

And when a gateway dies, every connection it held drops at once. Clients reconnect to a different gateway, re-register in the session registry, and pull anything they missed from their persisted inbox — which only works *because* you persisted before delivering.

### 4.4 Ride-sharing — [Chapter 16](hld-chapter-16.md)

**The signature difficulty: geography, live.** A normal index sorts one value, but location is two dimensions and "nearby" isn't a range on either alone. Scanning every driver is out of the question.

**The move: map 2D space onto a 1D index** so nearby things stay close in the index.

**Diagram 19 — the geo-index:**

```
     the world as a grid of equal-resolution cells

     ┌────────┬────────┬────────┐
     │   NW   │   N    │   NE   │   find_nearby(pickup):
     ├────────┼────────┼────────┤     cell = geohash(pickup)   # "9q8yy"
     │   W    │ 9q8yy  │   E    │     candidates = cell + its 8 neighbors
     │        │   ★    │        │     filter to available, sort by ETA
     ├────────┼────────┼────────┤     return top few
     │   SW   │   S    │   SE   │
     └────────┴────────┴────────┘   ← a handful of cell lookups,
                                       not a scan of every driver
```

**Geohashing** encodes a location as a string, and locations near each other *usually* share a prefix — longer prefix, smaller cell. "Usually" is doing real work in that sentence: two points a metre apart can still land on opposite sides of a cell boundary and share almost no prefix. That's exactly why the query is never just "look up my cell" but **"my cell plus its eight neighbours"** — searching the ring of neighbours is what covers the boundary case. A **quadtree** instead subdivides recursively, splitting dense areas more finely than empty ones. **S2** and **H3** are the production libraries (H3 uses hexagons; Uber built it for this problem).

You don't implement any of these in an interview — you name one and explain the idea in a sentence: *"index drivers by geohash so 'find nearby' is a cell lookup plus its neighbours, not a full scan."*

**Diagram 20 — the whole system:**

```
                  ┌──────────────┐
 riders/drivers ─▶│ load balancer│
                  └──────┬───────┘
                         ▼
        ┌────────────────────────────────┐
        │          app / API tier        │
        └──┬──────────────┬───────────┬──┘
  location │       match  │           │ live tracking
  updates  ▼              ▼           ▼
  ┌────────────────┐ ┌──────────────┐ ┌──────────────────┐
  │ geo-index      │ │ matching svc │ │ WebSocket gateway│ (Ch 15)
  │ (Redis geohash)│ │ atomic claim │ │ push locations   │
  │ SHARDED BY     │ │ of driver    │ └──────────────────┘
  │ city / region  │ └──────┬───────┘
  └────────────────┘        ▼
   1M+ updates/sec   ┌──────────────────────┐
   in memory         │ DB: trips, users     │ durable, sharded
                     └──────────────────────┘
   trip events ──▶ queue ──▶ workers ──▶ receipts, fare, analytics
```

The location firehose — a million updates a second — goes to **in-memory** ephemeral storage, never the durable database; a driver's position from thirty seconds ago is worthless, so there's nothing to protect. But memory alone doesn't absorb a million writes a second, so the geo-index is **sharded by city or region** — a natural shard key here, because a "find nearby" query is almost always local to one region, and the few that straddle a boundary just consult the neighbouring shard. Dense regions get subdivided further, which is the same hot-shard problem from Ch 4 wearing a map.

**And here's the last lesson, one more time.** The interesting consistency decision is **claiming a driver.** If two riders both see the same driver as available and both grab them, you've double-booked. That step is an **atomic compare-and-set** — set available→reserved *only if* currently available. Whoever wins, wins; the loser moves to the next candidate. Note how *narrow* it is: one field, one operation, guarded tightly, rather than strong consistency smeared across the system.

So: driver locations are happily **AP**, the match is **CP**, the trip record is durable, and the fare and receipt are computed asynchronously off a queue. Same system, consistency chosen per operation, and paid for only where it's needed. That's Ch 7, arriving right where you needed it.

**Part 4 checkpoint:** can you run all six steps on an unfamiliar problem in 35 minutes — clarify, estimate, API and data model, a diagram that grows, one deep dive, and a closing list of tradeoffs?

> *Estimate → API → data model → architecture → discover the break → fix it. Repeat until you've scaled as far as needed.*

---

## How to re-read this

Three passes, spread over days — the same contract as the chapters, compressed to one file.

**Pass 1 (~60 min).** Read top to bottom. Don't take notes. You're rebuilding the arc, not learning it.

**Pass 2 (~45 min).** For each part, close the file and redraw the diagrams from memory — boxes, arrows, and *why each box exists.* Peek only when stuck, then close again. Diff at the end and note the two or three things that slipped.

**Pass 3 (~30 min).** Pick two parts and explain each aloud in four or five sentences: what the system was, what the bottleneck was, what the move was, what it cost, and what new bottleneck the move created. If you can't name the cost, you don't have the move.

For depth on anything here, go back to the source chapter. For lookup — the latency ladder, capacity rules of thumb, the component catalog, the 35-minute interview budget — use the [appendix](hld-appendix.md); it's a reference table, this file is a story.

## The bumper sticker

> *No box in this file arrived because it was best practice. Each one arrived because a number or a failure demanded it, and each one was paid for with a cost you can name out loud. Derive an architecture that way in the interview and you never have to remember a picture.*

---

<div align="right">

[Appendix →](hld-appendix.md)

</div>
