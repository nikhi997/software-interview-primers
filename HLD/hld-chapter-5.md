# Chapter 5: When reads repeat themselves

*[← Chapter 4](hld-chapter-4.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

End of Part 1 we had the full scalable data tier: sharded, replicated, routed by consistent hashing. It can hold any amount of data and survive failure. But it's *wasteful.* Every read travels to a database box and reads from disk — even when it's the same popular URL fetched ten million times today.

Watch the waste. Some celebrity tweets a link. Suddenly one short code gets 5 million clicks in an hour. Each click:

```
client → load balancer → app server → database → read from disk → back
```

The answer is *identical* every single time, but we recompute it from disk 5 million times. That's the pain: **we keep paying full price for an answer we already know.**

The fix is the highest-leverage move in all of system design: **caching.**

---

## What a cache is

A **cache** is a small, fast store that holds copies of frequently-needed data so you don't have to recompute or re-fetch it. "Fast" because it lives in **RAM**, not on disk.

The numbers are the whole reason caching exists. Roughly:

| Operation | Time | Relative |
|---|---|---|
| Read from RAM | ~100 nanoseconds | 1× |
| Read from SSD | ~100 microseconds | ~1,000× slower |
| Read from disk (HDD) | ~10 milliseconds | ~100,000× slower |
| Network round-trip (same datacenter) | ~0.5 milliseconds | ~5,000× slower |

Reading from memory is **thousands of times faster** than from disk or across the network. A cache turns a 10 ms database read into a 0.1 ms memory read. Multiply that by 5 million celebrity-link clicks and you see why caching is the first thing engineers reach for when something is slow.

> 💡 **Concept notes — where the cache lives**
> Usually a dedicated in-memory store like **Redis** or **Memcached**, running on its own box(es), shared by all app servers. An app server checks the cache first; only on a miss does it bother the database. The cache is *not* the source of truth — it's a fast copy of data that ultimately lives in the database.

---

## The cache-aside pattern (learn this one cold)

The most common caching strategy, and the default answer in interviews:

```
read(key):
    value = cache.get(key)
    if value is not None:        # CACHE HIT
        return value
    value = database.get(key)    # CACHE MISS
    cache.set(key, value)        # remember it for next time
    return value
```

1. Look in the cache first.
2. **Hit** (found it) → return immediately. Fast path.
3. **Miss** (not there) → read the database, *store the result in the cache*, return it. Next time it'll be a hit.

> 💡 **Concept notes — hit rate is everything**
> The **cache hit rate** is the fraction of reads served from cache. If 95% of reads are hits, only 5% touch the database — you've cut database load by 20×. Caching works because of **skew**: real traffic isn't uniform. A small fraction of items (popular URLs, hot products, trending posts) get the vast majority of requests. Cache those, and a tiny cache covers most traffic. This is the **Pareto / 80-20** principle showing up in infrastructure.

### Estimate it

Our celebrity link: 5 million clicks/hour ≈ **1,400 reads/sec** for that one URL. Without a cache, all 1,400/sec hit the database. With cache-aside and that URL cached, the *first* request is a miss (one DB read) and the next 1,399/sec every second are memory reads. The database load for that hot URL drops from 1,400/sec to roughly *zero.* One cache entry absorbed a celebrity.

---

## The hard part: the cache can be wrong

A cache is a *copy.* The instant the real data changes, every copy is potentially **stale.** This is the central caching problem, and the famous quip is true:

> *"There are only two hard things in computer science: cache invalidation and naming things."*

Concrete failure: a URL's destination is edited (or an account is deleted), but the cache still holds the old value. Reads keep returning the dead/old answer until the cache is corrected. **Invalidation** is how you keep the cache honest. Three approaches:

**1. TTL (time-to-live) — expire entries after a set time.**
Store each entry with an expiry: "keep this for 60 seconds, then drop it." After expiry, the next read misses and re-fetches fresh data.
- ✅ Dead simple. Self-healing — staleness lasts at most one TTL.
- ❌ Data can be stale for up to the TTL. You trade freshness for simplicity. Short TTL = fresher but more DB load; long TTL = less load but staler. Tuning this is a real lever.

**2. Write-through / explicit invalidation — update or delete the cache when the data changes.**
On a write, also update the cached copy (write-through) or just delete it so the next read re-fetches (invalidate-on-write).
- ✅ Cache stays fresh.
- ❌ More complex; every write path must remember to touch the cache. Miss one and you leak stale data.

**3. Combine them.** Invalidate on write *and* set a TTL as a safety net for any invalidation you miss. Common in practice.

> 💡 **Concept notes — the freshness/load tradeoff has no free answer**
> You cannot have a cache that is *both* perfectly fresh *and* takes all load off the database for free. Every scheme trades freshness against database load and complexity. The interview skill is stating the trade for *this* data: "URL destinations rarely change, so a 5-minute TTL is fine — worst case a redirect is 5 minutes stale, and we cut DB reads by 50×." That sentence is the whole job.

---

## Two failure modes worth knowing by name

These come up in strong interviews; knowing the names is a signal.

**Thundering herd (cache stampede).** A super-popular cached item expires. In the same instant, thousands of requests all miss, and *all of them* hit the database at once to recompute it — the very spike the cache existed to prevent. Fixes: let only one request recompute while others wait (a lock), or refresh hot keys *before* they expire.

**Cache penetration.** Requests for keys that *don't exist* (e.g., random invalid short codes from a scanner). They always miss the cache and always hit the database. Fix: cache the "not found" answer too (a negative cache entry), or use a Bloom filter to reject keys that definitely don't exist before touching the DB.

> 💡 **Concept notes — how a Bloom filter says "definitely not"**
> A **Bloom filter** answers one question fast and in tiny space: *have I definitely never seen this key?* It's a bit array (all zeros) plus *k* independent hash functions. To **add** a key, hash it *k* ways and set those *k* bits to 1. To **check** a key, hash it the same *k* ways: if *any* of those bits is 0, the key was **definitely never added** — skip the DB. If *all* are 1, it's **probably** present, so you do the real lookup. The asymmetry is the whole trick: **false positives are possible, false negatives are not.** It can wrongly say "maybe" but never wrongly say "no" — and a "no" is always safe to trust, which is exactly what you want as a cheap gate in front of the database. It costs a few bits per key (it stores no values), and the classic version can't delete (clearing a bit could break another key that shares it). Tune the false-positive rate by spending more bits and more hashes for fewer wrong "maybes." *For the URL shortener:* load every real short code into the filter; a scanner's random code fails the filter instantly and never reaches the DB.

---

## Eviction: the cache is small on purpose

A cache holds far less than the database — it's expensive RAM. When it fills up, adding a new entry means **evicting** an old one. The policy decides which:

- **LRU (Least Recently Used):** evict the entry untouched for the longest. The overwhelmingly common default — recently-used things are likely to be used again. *(You may have built an LRU cache as an LLD/DSA exercise — HashMap + doubly linked list. Same idea, now as infrastructure.)*
- **LFU (Least Frequently Used):** evict the *least often* accessed. Better for stable hot sets, costlier to track.
- **FIFO:** evict oldest-inserted. Simple, usually worse than LRU.

You rarely implement eviction (Redis does it), but you should know *LRU is the default and why.*

---

## Where caches live (the layers)

Caching isn't one box — it's a *strategy applied at every layer.* From client to database:

```
browser cache → CDN (Ch 9) → load balancer → app
   → in-memory app cache → distributed cache (Redis) → database
                                                          (which has
                                                           its own
                                                           internal cache)
```

Each layer that answers a request means the layers behind it never see it. The closer to the user you cache, the more work you save — but the staler the data can get and the less control you have. We'll see the CDN (caching *static files* near the user) in Chapter 9.

---

## What we have now

Our system: scalable data tier (Part 1) fronted by a cache. Hot reads are served from memory in microseconds; the database only sees misses and writes. With a good hit rate, one small cache absorbs the vast majority of read traffic — including celebrity-sized spikes.

We've made reads fast. But every operation so far has been **synchronous** — the user waits for it to finish. What about work that *doesn't* need the user to wait? Sending a welcome email, generating a thumbnail, updating analytics? Making the user wait for those is the next pain — and queues are the fix. That's Chapter 6.

---

## Try it

1. A product page is read 10,000 times/sec but its data changes a few times a day. Design the caching: which pattern, what TTL, and what's the worst-case staleness a user could see? Justify the TTL.
2. With a 90% cache hit rate and 50,000 reads/sec total, how many reads/sec actually reach the database? What hit rate would you need to get that under 1,000/sec?
3. Explain the thundering-herd problem in your own words, and give one fix.
4. A scanner sends millions of requests for random invalid IDs. Why does your cache not help, and what's it called? Name a fix.
5. Why is LRU the default eviction policy? Describe a traffic pattern where LFU would beat it.

*Write your answers in [hld-chapter-5-tryit.md](code/hld-chapter-5-tryit.md).*

---

## The bumper sticker

> *Cache the hot minority in memory to absorb most reads — then spend all your worry on keeping the copy honest, because a cache is only as good as its invalidation.*

Next: not all work needs to happen while the user waits. Time to put slow work in a queue and answer the user *now*.

---

<div align="right">

[Chapter 6 →](hld-chapter-6.md)

</div>
