# Chapter 8: When too many requests arrive

*[← Chapter 7](hld-chapter-7.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

Everything so far assumed requests arrive at a reasonable rate. Reality disagrees. Sources of *too many* requests:

- A buggy client stuck in a retry loop, hammering you 1,000×/sec.
- A scraper trying to download your entire dataset.
- An attacker trying to brute-force short codes, or just to knock you over.
- A legitimate viral spike that's simply more than you provisioned for.

Without protection, any of these can exhaust your capacity and take the service **down for everyone** — the well-behaved users included. That's the pain: *one abusive or runaway client shouldn't be able to degrade everyone else.*

The fix is to learn to say **"no, slow down"** — gracefully and fairly. Two related tools: **rate limiting** (capping how much a client may do) and **backpressure** (pushing back when the system is overloaded).

---

## Rate limiting: a cap per client

A **rate limiter** enforces a rule like *"each user may make at most 100 requests per minute."* Over the limit, you reject the extra requests — typically with HTTP status **429 Too Many Requests** — instead of trying to serve them and falling over.

```
request from user X
   → rate limiter: has X used up their quota this window?
        → no  → allow, let it through
        → yes → reject with 429 "slow down"
```

> 💡 **Concept notes — where the limiter sits**
> Rate limiting usually lives at the **edge** — in the load balancer, an API gateway, or a thin layer in front of the app — so abusive traffic is rejected *before* it reaches and wastes your expensive app and database tiers. The counters (how much each client has used) live in a fast shared store like **Redis**, because all your edge nodes must agree on a user's count — otherwise a user could get their full quota *per server* by spreading requests across the fleet. (Note the echo of Ch 2: shared state goes in a shared store, not on individual stateless nodes.)

### The algorithms (know token bucket cold; know the others by name)

**Token bucket — the default answer.**
Picture a bucket that holds up to **B** tokens and refills at **R** tokens per second. Each request must take one token; no token available → rejected.

```
bucket capacity B = 10 tokens, refill R = 1 token/sec
- start full (10 tokens)
- 10 requests arrive at once → all allowed (drains bucket to 0)  ← burst absorbed
- 11th immediately → no token → 429
- wait 5 sec → 5 tokens refilled → 5 more allowed
```

- ✅ Allows short **bursts** (up to bucket size) while capping the *sustained* rate. This matches real usage — people click in bursts, then pause. It's why token bucket is the most popular choice.
- The two knobs map to real intent: **B** = how big a burst you tolerate; **R** = the long-run average rate you allow.

**Fixed window:** count requests per clock window ("max 100 per minute, reset on the minute").
- ✅ Trivial to implement (a counter with a TTL).
- ❌ **Boundary spike:** a user can do 100 at 11:59:59 and 100 more at 12:00:00 — 200 in one second, because the window reset between them.

**Sliding window:** smooth the boundary by counting over a rolling window rather than a fixed clock period. More accurate, slightly more expensive. Fixes the fixed-window boundary spike.

**Leaky bucket:** requests enter a queue and drain at a fixed rate; overflow is dropped. Smooths bursts into a *steady* outflow (vs token bucket, which lets bursts through). Good when the thing downstream needs a constant rate.

> 💡 **Concept notes — token bucket vs leaky bucket in one line**
> **Token bucket** lets bursts *through* (good for APIs — users burst then idle). **Leaky bucket** forces a *smooth, constant* output rate regardless of input burstiness (good for protecting a downstream that hates spikes). Pick based on whether you want to *allow* bursts or *flatten* them.

There's a runnable token-bucket limiter in `code/rate_limiter.py` — read it to see how few lines the core idea takes.

---

## What to rate-limit *by*

The limiter's fairness depends entirely on the **key** you count against:

- **By user / API key:** fairest for authenticated APIs — each account gets its own quota.
- **By IP address:** the fallback for anonymous traffic, but blunt — a whole office or campus behind one NAT shares an IP, and attackers rotate IPs.
- **By endpoint:** stricter limits on expensive or sensitive operations (login attempts, search, writes) than on cheap ones.

Often you combine them: a global per-IP limit to blunt floods, *plus* a per-user limit for fairness, *plus* a tight per-endpoint limit on `/login` to stop credential-stuffing.

---

## Backpressure: when the system itself is the limit

Rate limiting caps *clients.* But sometimes the load is legitimate and you're simply at capacity — the database is maxed, the queue is backing up. Continuing to accept work you can't handle just makes everything slower for everyone and can trigger a **cascading failure** (one overloaded component times out, callers retry, the retries add *more* load, the whole system spirals down).

**Backpressure** is the system signaling "I'm full, hold off" *upstream*, so load is shed deliberately instead of everything collapsing.

> 💡 **Concept notes — backpressure vs rate limiting**
> **Rate limiting** is a *policy*: "this client may do at most X" — decided in advance, per client.
> **Backpressure** is a *reaction to real-time load*: "the system is overloaded *right now*, so reject/slow down regardless of who you are." Rate limiting is the speed limit sign; backpressure is the traffic cop waving cars away from a jammed intersection. You want both.

### Tools of graceful degradation

When overloaded, shed load *deliberately* in priority order rather than failing randomly:

- **Load shedding:** drop low-priority work first (analytics events before checkout requests). Decide *what* to sacrifice before you're forced to.
- **Circuit breaker:** if a downstream dependency is failing, *stop calling it* for a while (the breaker "trips") and fail fast, instead of piling up requests that will time out anyway. After a cooldown, test if it's recovered. This prevents one sick service from dragging down everything that calls it. (A slow, flaky **LLM / AI API** is a textbook modern example of a dependency to wrap in a breaker with timeouts and fallbacks — the AI/ML track treats an LLM call as exactly this kind of downstream dependency.)
- **Graceful degradation:** serve a reduced experience instead of an error — stale cached data, a simplified page, "recommendations unavailable" while the core page still loads. *A degraded answer beats no answer.*
- **Bounded queues:** queues (Ch 6) must have a *maximum size*. An unbounded queue under overload grows until it runs out of memory and crashes — turning a slowdown into an outage. A bounded queue rejects new work when full: that rejection *is* backpressure.

> 💡 **Concept notes — backpressure is mostly implicit, not a notification you handle**
> A common misread: "signal upstream" sounds like servers *send messages* that you must subscribe to and act on. They mostly don't. Most backpressure falls out of resources already in the request path: a full **bounded queue** makes `put()` *block*; an exhausted **connection pool** makes the next `acquire()` *block*; a saturated receiver shrinks its **TCP window** so the sender's `send()` *blocks*. The blocking *is* the signal — each layer slows down simply because its call into the layer below is stuck, with no listener code anywhere. So you don't write notification handlers; you **bound your queues, size your pools, and set timeouts**, and the slowdown propagates upstream for free. The genuinely explicit part is **priority** — *what* to sacrifice is a business judgment the runtime can't infer, so load-shedding rules and request classes are real code. Circuit breakers and retry-backoff are explicit too, but you *configure a library*, not hand-roll a state machine.

> 💡 **Concept notes — the retry-storm trap**
> Naive retries make overload *worse*: a struggling service returns errors, every client immediately retries, the retries multiply the load, and the service is now drowning in retries of failed requests. Fixes: **exponential backoff** (wait longer between each retry: 1s, 2s, 4s…) plus **jitter** (randomize the wait so clients don't all retry in sync) plus a **retry cap**. "Retry with exponential backoff and jitter" is a phrase worth memorizing — interviewers listen for it.

---

## Bringing it back to our system

For the URL shortener:
- **Creation endpoint** (`POST /shorten`): expensive-ish, abuse-prone → strict per-user/per-IP token-bucket limit. Stops someone from minting millions of codes to exhaust the keyspace.
- **Redirect endpoint** (`GET /{code}`): cheap, must stay fast and available, mostly served from cache → loose limit, mainly per-IP flood protection.
- **Backpressure:** if the database tier is struggling, prioritize redirects (the core product) and shed non-essential work (analytics writes can be dropped or deferred). The redirect keeps working even as we shed the rest.

Different limits per endpoint, matched to cost and importance — the same "choose per feature" discipline as CAP in Ch 7.

---

## What we have now

The system now protects itself: per-client rate limits reject abuse at the edge before it wastes the expensive tiers, and backpressure (load shedding, circuit breakers, bounded queues, graceful degradation) keeps overload from cascading into a full outage. One abusive or runaway client can no longer take everyone else down.

One category of pain is left before we name the vocabulary: we've assumed all our data is small rows in a database. But real systems serve *big files* — images, videos, documents — and serving those from your app servers is its own disaster. That's blob storage and the CDN. Chapter 9.

---

## Try it

1. Implement token bucket in words for "20 requests/sec sustained, bursts up to 50." Give B and R. What happens to the 51st simultaneous request, and how long until 10 more are allowed?
2. Explain the fixed-window boundary problem with a concrete timeline, and how sliding window fixes it.
3. Why must rate-limit counters live in a shared store (e.g., Redis) rather than in each edge server's memory? What abuse becomes possible if they don't?
4. Describe a retry storm and the three-part fix that prevents it.
5. Your database tier is overloaded by legitimate traffic. Rate limiting per client won't help (everyone's within their quota). Name three backpressure/degradation techniques you'd apply and what each sacrifices.

*Write your answers in [hld-chapter-8-tryit.md](code/hld-chapter-8-tryit.md).*

---

## The bumper sticker

> *Protect the system from clients with per-key rate limits at the edge, and protect it from itself with backpressure — shed low-priority load deliberately so overload degrades gracefully instead of cascading into an outage.*

Next: real systems serve big files, not just rows. Serving a 2 GB video from your app server is a category error. Time for blob storage and the CDN.

---

<div align="right">

[Chapter 9 →](hld-chapter-9.md)

</div>
