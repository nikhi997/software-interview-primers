# Chapter 13: The interview ritual

*[← Chapter 12](hld-chapter-12.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

You know the components. You know the tradeoffs. You can draw the diagram. Now: how do you actually *run* an HLD interview without freezing or rambling?

There's a workflow. Six steps. Use it every time. It works because it's how senior engineers actually approach an unfamiliar system — not because it's a memorized script. The same way LLD had its five-step ritual, HLD has this one.

The six steps:

1. **Clarify requirements** — functional + non-functional. Ask before designing.
2. **Estimate** — turn vague scale into numbers (reads/sec, writes/sec, storage).
3. **API + data model** — define the contract and what you store.
4. **High-level design** — the box-and-arrow diagram, grown from the simplest version.
5. **Deep dive** — zoom into the 1–2 hardest components when the interviewer probes.
6. **Bottlenecks & tradeoffs** — name what breaks next and what you traded.

Let's apply it end-to-end to a problem you already half-know.

## The problem: a URL shortener at scale

*"Design a URL shortener like bit.ly. Users submit a long URL, get a short code, and visiting the short code redirects to the original."*

You built the *code* for this in LLD Ch 1 and the *infrastructure intuition* across this book. Now do it as a real interview. **Don't start drawing.** Step 1.

---

## Step 1: Clarify requirements

Ask these *out loud.* The interviewer wants to see you scope before you build.

**Functional (what it does):**
- Shorten a long URL → short code. ✅
- Redirect a short code → long URL. ✅
- Custom aliases (user picks the code)? → *Yes, optional.*
- Expiration / deletion? → *URLs can optionally expire.*
- Analytics (click counts)? → *Yes, basic click tracking.*

**Non-functional (how well it does it):**
- Scale? → *100M new URLs/day, read-heavy.*
- Latency? → *Redirects must be fast — under ~100 ms.*
- Availability? → *Highly available; a down redirect is a broken link everywhere.*
- Consistency? → *Redirects can tolerate slight staleness (eventual is fine); code allocation must be unique (no collisions).*

> 💡 **The clarify move:** separate **functional** ("what features") from **non-functional** ("how fast, how big, how available, how consistent"). The non-functional answers drive the *entire* architecture — "read-heavy, 100M/day, must be fast" is what tells you to cache and replicate. Write the answers down; they're your scope contract.

---

## Step 2: Estimate (the part most candidates skip — don't)

Turn the words into numbers using Ch 1's toolkit (daily ÷ 100,000 ≈ per second).

**Writes:** 100M new URLs/day
$$\frac{100{,}000{,}000}{100{,}000} = 1{,}000 \text{ writes/sec}$$

**Reads:** read-heavy, assume 100:1
$$1{,}000 \times 100 = 100{,}000 \text{ reads/sec}$$

**Storage:** each URL row ~500 bytes
$$100\text{M/day} \times 500\text{ B} = 50\text{ GB/day} \approx 18\text{ TB/year}$$

**Keyspace (how long must the short code be?):** with 100M/day for, say, 10 years ≈ 365 billion URLs. Using base62 characters (a–z, A–Z, 0–9):
$$62^7 \approx 3.5 \times 10^{12} = 3.5 \text{ trillion} \Rightarrow \textbf{7 characters is enough.}$$

> 💡 These four numbers — **1K writes/sec, 100K reads/sec, ~18 TB/year, 7-char codes** — *drive every later decision.* 100K reads/sec screams "cache + replicas." 18 TB/year over years says "this will eventually need sharding." The keyspace math determines the code length. Estimation isn't a ritual box to tick; it's where the design comes from.

---

## Step 3: API + data model

**API** (Ch 11):
```
POST /urls
  body:    { "long_url": "...", "custom_code": "..."(opt), "expires_at": "..."(opt) }
  returns: { "short_url": "https://sho.rt/abc1234" }
  201 | 409 (custom code taken) | 429 (rate limited)

GET /{code}
  returns: 302 redirect → long_url
           404 (not found / expired)
```

**Data model:**
```
URL
  short_code   (primary key — we look up by this)
  long_url
  created_by
  created_at
  expires_at
  click_count
```

**SQL or NoSQL?** Access pattern is dead simple: look up by `short_code` (a key), no joins, no complex queries, but *enormous* scale (18 TB/year, 100K reads/sec). That's the textbook **NoSQL** case — a key-value/wide-column store (DynamoDB, Cassandra) that shards by key natively. Justify it by the access pattern, exactly as Ch 11 said. (You could note SQL works fine at smaller scale; at this scale NoSQL's native sharding wins.)

---

## Step 4: High-level design — and the one interesting algorithm

Now the diagram, grown from simple. But first, the one genuinely interesting design decision in this problem: **how do you generate the short code?** Interviewers always dig here.

**Option A — Hash the URL (e.g., MD5, take first 7 chars).**
- ❌ Collisions: two different URLs can hash to the same 7 chars. You'd have to check-and-retry on every write. And the same URL always makes the same code (maybe fine, maybe a privacy issue).

**Option B — Random 7-char code, check for collision.**
- Works, but as the keyspace fills, collision checks (an extra DB read per write) get more frequent. Fine early, degrades later.

**Option C — Counter + base62 encoding (the clean answer).**
Keep a global counter. Each new URL gets the next integer, encoded into base62 → a short code. Integer 1 → "1", integer 125 → "21", etc. **No collisions ever** (every integer is unique), no collision-check read, codes are short.
- The catch: a *single* global counter is a bottleneck and a SPOF. The fix is elegant — **hand out ranges.** A coordination service (or each app server) grabs a block of, say, 1,000 IDs at a time ("you own 1,000,000–1,000,999") and serves them locally, only coordinating once per 1,000 URLs. This is roughly how real systems (and Twitter's Snowflake ID generator) do it.

> 💡 **Concept notes — why counter+base62 wins here**
> It turns code generation into a *guaranteed-unique* operation with no read-before-write, and the range-allocation trick removes the single-counter bottleneck. When an interviewer asks "how do you avoid collisions?", "counter with base62, handing out ID ranges to each server to avoid a central bottleneck" is the answer that ends the line of questioning. Name the SPOF (the counter) *and* its fix (ranges) in the same breath.

Now the architecture, using our numbers:

```
            ┌──────────────┐
 users ────▶│ load balancer│
            └──────┬───────┘
                   ▼
         ┌───────────────────┐   429 if abusive (Ch 8 — protect code creation)
         │   app servers     │◀──rate limiter
         │   (stateless)     │
         └──┬─────────────┬──┘
   reads    │             │   writes
            ▼             ▼
      ┌──────────┐   ┌─────────────────────┐
      │  cache   │   │ NoSQL store         │
      │ (Redis)  │   │ sharded by short_code│
      │ hot URLs │   │ + replicated        │
      └──────────┘   └─────────────────────┘
                          ▲
                   ID-range allocator (counter → base62)
   click events ──▶ queue ──▶ workers ──▶ analytics store  (async, Ch 6)
```

**Trace a redirect (the 100K/sec hot path):** request → LB → app server → **check cache** (hot codes live here, ~99% hit rate given skew) → on hit, 302 redirect in a few ms; on miss, read a replica, populate cache, redirect. The cache absorbs the celebrity-link spikes from Ch 5. *This is why redirects stay under 100 ms.*

**Trace a create (1K/sec):** request → LB → rate limiter (stop keyspace abuse) → app server → grab next ID from its range → base62 encode → write to NoSQL store → return short URL.

**Click analytics:** don't make the redirect wait to increment a counter. Drop a "click" event on a **queue**; workers aggregate counts asynchronously (Ch 6). The redirect stays fast; analytics are eventually consistent — which is fine for a click count.

---

## Step 5: Deep dive (be ready to zoom in)

The interviewer will poke one box. Common probes and the crisp answers:

- *"How does the cache stay correct?"* → URLs rarely change, so a long TTL is fine; on the rare edit/expiry, invalidate the key. Worst case a redirect is briefly stale — acceptable (Ch 5).
- *"What if a server dies holding an unused ID range?"* → We lose that block of IDs (small gaps in the sequence). Harmless — we have 3.5 trillion codes; gaps don't matter. (Naming this tradeoff is the win.)
- *"100K reads/sec on the database?"* → No — the *cache* serves ~99% of reads; only misses (a few thousand/sec) hit the replicas, which scale horizontally (Ch 3).
- *"Custom alias collisions?"* → Custom codes need a uniqueness check (a consistent write — CP for this path), unlike generated codes which are collision-free by construction.

---

## Step 6: Bottlenecks & tradeoffs (close strong)

End by naming what breaks *next* and what you traded — this is the senior close.

- **Next bottleneck:** the analytics store as click volume grows → shard it, or push to a dedicated analytics pipeline.
- **Tradeoffs made:** click counts are *eventually* consistent (we chose speed of redirect over real-time counts — AP for analytics); generated codes are sequential-ish, so a clever user could enumerate codes → if that's a concern, add randomization within each range (privacy vs simplicity tradeoff). Say these out loud.

---

## The ritual, abstracted

That's the whole loop you'll reuse on every problem:

```
1. Clarify   → functional + non-functional (non-functional drives everything)
2. Estimate  → reads/sec, writes/sec, storage; the numbers ARE the design
3. API+data  → contract + storage + SQL/NoSQL justified by access pattern
4. HLD       → diagram grown from simple; trace read path and write path
5. Deep dive → zoom into the 1–2 hardest pieces on demand
6. Tradeoffs → name the next bottleneck and what you sacrificed
```

Internalize the *order*. Candidates who jump straight to step 4 (drawing boxes) without 1–3 look junior, no matter how good the boxes are. The estimate and the clarifications are what make the boxes *justified.*

---

## Try it

Before the worked problems, run the full ritual *out loud, on paper, timed to 35 minutes* for **Design Pastebin** (users paste text, get a link, others view it). Do all six steps. Specifically: estimate assuming 10M pastes/day; decide SQL vs NoSQL and where the paste *text* lives (hint: Ch 9); design the read path for a viral paste; and name one bottleneck and one tradeoff. Only then read Chapter 14.

*Write your answers in [hld-chapter-13-tryit.md](code/hld-chapter-13-tryit.md).*

---

## The bumper sticker

> *Six steps, in order: clarify, estimate, API+data, diagram, deep-dive, tradeoffs. The estimate and the clarifications are what turn a pile of boxes into a justified design.*

Next: three full worked problems — Twitter feed, chat, and ride-sharing — each running this exact ritual, each introducing one signature new idea.

---

<div align="right">

[Chapter 14 →](hld-chapter-14.md)

</div>
