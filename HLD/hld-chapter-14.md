# Chapter 14: Worked problem — Twitter / News Feed

*[← Chapter 13](hld-chapter-13.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

A worked HLD problem. I'm running the six-step ritual from Ch 13. Read this *after* attempting it cold yourself — otherwise you memorize my answer instead of building the muscle.

The problem: *"Design Twitter's news feed. Users post tweets and follow others. Each user has a home timeline showing recent tweets from everyone they follow."*

This problem's signature lesson: **fanout** — and the most-loved tradeoff in all of system design, *fanout-on-write vs fanout-on-read.*

---

## Step 1: Clarify

**Functional:**
- Post a tweet. ✅
- Follow/unfollow users. ✅
- Home timeline: recent tweets from people you follow, newest first. ✅ *(the heart of the problem)*
- Likes/retweets/replies? → *Acknowledge, but focus on the timeline.*

**Non-functional:**
- Scale? → *300M daily users, 600M tweets/day. Massive.*
- Read-heavy? → *Extremely. People scroll far more than they post.*
- Latency? → *Timeline load must be fast (~200 ms). Posting can be slightly slower.*
- Consistency? → *Eventual is fine — a tweet showing up a few seconds late is acceptable.*

Scope locked: the timeline is the problem. Eventual consistency is allowed (that's what makes the fanout tricks legal).

---

## Step 2: Estimate

**Tweets (writes):**
$$\frac{600\text{M/day}}{100{,}000} = 6{,}000 \text{ tweets/sec}$$

**Timeline reads:** 300M users refreshing, say, 10 timelines/day each = 3B reads/day:
$$\frac{3{,}000\text{M/day}}{100{,}000} = 30{,}000 \text{ timeline reads/sec}$$

Read:write ≈ 5:1 at the timeline level, but the *real* asymmetry is hidden in fanout (below).

**Storage:** 600M tweets/day × ~300 bytes ≈ 180 GB/day of tweet text ≈ 65 TB/year. Media (images/video) goes to blob storage + CDN (Ch 9), not counted here.

> 💡 The number that dominates this design isn't reads/sec — it's **followers per user.** A normal user has hundreds of followers; a celebrity has 100M+. That single fact breaks the naive design and forces the signature tradeoff.

---

## Step 3: API + data model

**API:**
```
POST /tweets            { "text": "..." }                  → 201
GET  /timeline?limit=20&cursor=...                          → [tweets]
POST /users/{id}/follow                                     → 200
```

**Data model:**
```
TWEET:     tweet_id (PK), author_id, text, created_at, media_url
USER:      user_id (PK), handle, name
FOLLOW:    follower_id, followee_id        (who follows whom)
TIMELINE:  user_id, [tweet_ids...]         (precomputed feed — see below)
```

**SQL or NoSQL?** Massive scale, simple key-based access, no complex joins on the hot path → **NoSQL** for tweets and timelines (Cassandra-style), sharded by `user_id`. The social graph (FOLLOW) is sometimes a specialized graph store, but a sharded table works for the basics.

---

## Step 4: High-level design — the fanout problem

Here's the crux. To show your home timeline, you need recent tweets from everyone you follow. Two fundamentally different strategies:

### Approach A: Fanout-on-read (pull)

Store each user's tweets in their own list. When someone opens their timeline, **query all the people they follow, pull their recent tweets, merge by time.**

```
read timeline(user):
   followees = who does user follow   (say, 500 people)
   for each followee: fetch their recent tweets
   merge all, sort by time, return top 20
```

- ✅ **Writes are cheap** — posting a tweet just appends to *your* list. One write.
- ❌ **Reads are brutal** — every timeline load queries hundreds of users' tweets and merges them, *on the fly, 30,000 times/sec.* Slow and expensive.

### Approach B: Fanout-on-write (push)

When you post a tweet, **immediately push it into the precomputed timeline of every one of your followers.** Reading a timeline is then just reading your own ready-made list.

```
post tweet(author):
   followers = who follows author   (say, 500 people)
   for each follower: prepend this tweet to their TIMELINE list

read timeline(user):
   return user's precomputed TIMELINE   ← already assembled! one fast read.
```

- ✅ **Reads are trivial** — your timeline is pre-built; just read it. Blazing fast, which is what 30,000 reads/sec needs.
- ❌ **Writes are expensive** — one tweet becomes *N* writes, one per follower.

> 💡 **Concept notes — fanout-on-write vs fanout-on-read**
> **Fanout-on-write (push):** do the work when you *post* — pre-assemble every follower's timeline. Fast reads, expensive writes. Great because the system is read-heavy: do the work once at write time so the billions of reads are cheap.
> **Fanout-on-read (pull):** do the work when you *read* — assemble the timeline on the fly. Cheap writes, expensive reads.
> The default for a read-heavy social feed is **fanout-on-write** — you'd rather pay once per post than repeatedly per read. This is just the caching principle (Ch 5) at the feed level: precompute the answer so reads are cheap.

### The celebrity problem (why pure push breaks)

Fanout-on-write has a fatal edge case. A celebrity with **100 million followers** posts one tweet → that's **100 million writes**, instantly, to push into 100M timelines. This is the **hot key / celebrity problem.** Pure push can't handle it — one tweet would trigger a write storm.

> 💡 **The hybrid answer (this is the senior solution):**
> Use **fanout-on-write for normal users** (push their tweets to followers' timelines — cheap, since they have few followers), **but fanout-on-read for celebrities** (do *not* pre-push their tweets). When a user loads their timeline, they get their precomputed list (from normal-user pushes) **merged at read time** with the latest tweets from the few celebrities they follow (pulled live). Best of both: normal posts stay cheap, celebrity posts don't cause a write storm, and the merge at read time is small (you follow few celebrities). *"Hybrid: push for the masses, pull for celebrities, merge at read time"* is the answer that wins this problem.

```
        ┌─────────────────────────────────────────────┐
post ──▶│ app ──▶ is author a celebrity?                │
        │          no  → fanout-on-write: push to       │
        │                followers' timelines (via queue)│
        │          yes → store only; do NOT fan out      │
        └─────────────────────────────────────────────┘

read ──▶ precomputed timeline  ⊕  live-pull celebrity tweets  → merge → return
```

### The full diagram

```
                  ┌──────────────┐
 users ──────────▶│ load balancer│
                  └──────┬───────┘
                         ▼
                ┌──────────────────┐
                │   app servers    │
                └──┬────────────┬──┘
        post tweet │            │ read timeline
                   ▼            ▼
            ┌──────────┐   ┌──────────────────┐
            │  queue   │   │ timeline cache   │ ← precomputed feeds (Redis)
            └────┬─────┘   │ (hot timelines)  │
   fanout workers│         └────────┬─────────┘
   push to each  │                  │ on miss
   follower's    ▼                  ▼
   timeline ┌─────────────────────────────┐
            │ NoSQL: tweets, timelines,    │ (sharded by user_id, replicated)
            │ follow graph                 │
            └─────────────────────────────┘
   media ──▶ blob storage + CDN (Ch 9)
```

Posting drops the tweet, then a **queue + fanout workers** (Ch 6) asynchronously push it into followers' timelines — so the *poster* doesn't wait for 500 writes; they return immediately and fanout happens in the background. Timelines are cached (Ch 5). Media lives in blob storage + CDN (Ch 9). Every component you've learned, in one design.

---

## Step 5: Deep dive

- *"How is the timeline stored?"* → Per-user list of tweet IDs in a fast store (Redis / Cassandra), capped at the most recent ~800 — nobody scrolls back 10,000 tweets, so we don't store an unbounded feed (bounded, like Ch 8's bounded queues).
- *"Fanout to 500 followers — synchronous?"* → No. The post returns instantly; fanout happens via **async workers** off a queue. The poster never waits for it; followers' timelines update within seconds (eventual consistency — which we allowed in Step 1).
- *"Where's the celebrity threshold?"* → A tunable follower count (e.g., >1M). Above it, switch from push to pull-and-merge.
- *"Ranking, not just chronological?"* → Real feeds rank by a relevance model. Architecturally: a ranking service scores candidate tweets at read time. (Mention it; depth depends on the role.)

---

## Step 6: Bottlenecks & tradeoffs

- **Next bottleneck:** fanout write volume during peak (everyone tweets about a big event). The queue absorbs the spike (load leveling, Ch 6); workers drain it; timelines update a bit slower under load — graceful degradation.
- **Tradeoffs made:** timelines are **eventually consistent** (a tweet appears within seconds, not instantly — we chose fast reads over real-time freshness). We **precompute and store** every active user's timeline (more storage + write work) to make the 30K reads/sec cheap — classic space/work-for-speed trade. Hybrid fanout adds **complexity** (two code paths) to handle celebrities — complexity bought scalability.

---

## The one thing to remember

Every social feed (Twitter, Instagram, Facebook, TikTok) is, at its core, this same fanout question. **Push for the masses, pull for celebrities, merge at read time.** If you can explain *why* — read-heavy systems precompute, but the celebrity hot-key breaks pure precompute — you understand feeds.

---

## Try it

1. Re-derive fanout-on-write vs fanout-on-read from scratch, listing the cost of each, and explain why read-heavy systems default to write.
2. A celebrity with 50M followers posts. Compute the write amplification under pure fanout-on-write. Explain precisely how the hybrid approach avoids it.
3. Where in this design does each appear, and why: a queue, a cache, blob storage, sharding by user_id? Name the pain each solves.
4. Why cap stored timelines at ~800 tweets instead of keeping the full history per user?
5. Adapt the design for Instagram (image-first). What changes, what stays the same? (Hint: Ch 9 does more work here.)

*Write your answers in [hld-chapter-14-tryit.md](code/hld-chapter-14-tryit.md).*

---

## The bumper sticker

> *A news feed is the fanout problem: precompute timelines on write so reads are cheap (it's read-heavy), but fall back to pull-and-merge for celebrities so one post doesn't become 100M writes.*

Next: a chat system, where the signature challenge flips — it's about *real-time delivery* and *connection state*, not fanout.

---

<div align="right">

[Chapter 15 →](hld-chapter-15.md)

</div>
