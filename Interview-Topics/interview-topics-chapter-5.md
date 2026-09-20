# Chapter 5: Redis

*[← Chapter 4](interview-topics-chapter-4.md) · [Contents](interview-topics-README.md)*

- [ ] **Mark as read**

Redis is the other technology that's commonly a gap, and the brand hides an even simpler concept than Kafka: it's a **cache** — the in-memory speed layer from [HLD Ch 5](../HLD/hld-chapter-5.md), as a standalone server. Don't oversell it if you haven't used it; show conceptual command and lean on a small demo. The thing interviewers actually probe isn't "what is Redis" — it's **invalidation**, one of the two genuinely hard problems in computing.

The principle holds: **feel the concept beneath the brand name.** Redis is a fast key-value store. Once you frame it that way, the patterns (cache-aside, TTLs, eviction) are obvious, and the honest-pivot from Chapter 4 covers you if it's a gap.

---

## The mental model

> 💡 **Concept notes — what Redis is**
> An **in-memory key-value store** with a single-threaded command loop (so individual commands are atomic) and microsecond reads. Data types beyond plain strings: **hash**, **list**, **set**, and **sorted set (ZSET)** — plus **TTL/expiry** on any key. The in-memory part is the whole point: it's fast because it's RAM, which is also why durability is a *question* (below), not a given.

---

## Caching patterns: cache-aside is the default answer

> 💡 **Concept notes — cache-aside (lazy loading)**
> - **Read:** check Redis first. **Hit** → return. **Miss** → read the database, write the value into Redis **with a TTL**, return.
> - **Write:** update the database, then **invalidate** (delete) or update the cache key.
> - The TTL bounds staleness; explicit invalidation keeps it fresh on known writes.
> Also know **write-through** (write cache + DB together) and **write-behind** (write cache, flush to DB async). Cache-aside is the one to lead with.

> 💡 **Concept notes — invalidation, the hard part**
> Cache invalidation is famously described as one of computing's hardest problems, in a line [commonly attributed to Phil Karlton](https://martinfowler.com/bliki/TwoHardThings.html). The interview question underneath "do you know Redis?" is really **"what makes your cache wrong, and how do you bound it?"** Answers: TTLs cap staleness; explicit deletes on known writes; and **stampede protection** — when a hot key expires, many requests hit the DB at once, so use a short lock/single-flight (one request rebuilds), slightly **randomized TTLs** (avoid synchronized expiry), or pre-warming.

---

## Eviction, durability, and the non-cache uses

> 💡 **Concept notes — eviction and persistence**
> - **Eviction:** under `maxmemory`, Redis evicts by policy (LRU/LFU/TTL). Forgetting TTLs leads to unbounded memory growth.
> - **Durability:** primarily in-memory, so persistence is *optional* — **RDB** snapshots (periodic; can lose recent writes) or **AOF** (append-only log; more durable, configurable fsync). For a cache, losing data is fine (rebuild from the DB); for a source of truth you'd tune AOF or not rely on Redis alone.

> 💡 **Concept notes — it's not only a cache**
> Knowing the other uses signals depth: **session store**, **rate limiter** (`INCR` a per-window key with an expiry), **leaderboard** (sorted set), **distributed lock** (`SET key val NX PX` — and know the Redlock caveats), and **pub/sub**. In Spring: Spring Data Redis, `@Cacheable`/`@CacheEvict`, `RedisTemplate`.

---

## Build it, don't just read it

Add Redis (Docker) to a demo service; cache a Postgres read with `@Cacheable` + a TTL and show the second call skipping the database. Bonus: a fixed-window rate limiter with `INCR` + expiry. If Redis is a gap, this demo plus the honest pivot (Chapter 4) is your whole answer.

---

## Try it

Answer aloud:

1. In one sentence, what *is* Redis?
2. Walk me through cache-aside on both a read and a write.
3. A hot key just expired and your database is getting hammered — what's happening and how do you prevent it?
4. Is Redis durable? Can you lose data? Explain RDB vs AOF.
5. Name three uses of Redis beyond caching, and roughly how one of them works (e.g. a rate limiter).

*Write your answers in [interview-topics-chapter-5-tryit.md](code/interview-topics-chapter-5-tryit.md).*

## The bumper sticker

> *Redis is a cache — say that and the patterns follow: cache-aside with a TTL, invalidate on write, and protect against a stampede. The real interview question is invalidation: what makes your cache wrong and how do you bound it. And if it's a gap, the honest pivot from Chapter 4 still has you covered.*

Next: zooming out from single technologies to how they fit together — **microservices, REST, and the system-design arc** that strings Postgres, Redis, and Kafka into one design.

---

<div align="right">

[Chapter 6 →](interview-topics-chapter-6.md)

</div>
