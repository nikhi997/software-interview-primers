# Chapter 1: The whole app on one server

*[Contents](hld-README.md)*

- [ ] **Mark as read**

Someone hands you this task at work: build a service where people can shorten URLs and visit them. You already designed the *code* for this in LLD. Now the question is different: where does it *run*, and what happens when a lot of people use it?

You nod. Easy enough.

What does it actually have to do, at the infrastructure level? Three things:

1. Accept a request over the network.
2. Run some code (look something up, save something).
3. Send a response back.

That's it. Three things. Let's not pretend it's more.

Here's the first version. The shortest deployable thing that could possibly work: **one machine.**

```
        ┌─────────────────────────────┐
client  │        ONE SERVER           │
───────▶│  ┌───────────────────────┐  │
        │  │  web app (your code)  │  │
        │  ├───────────────────────┤  │
        │  │  database (same box)  │  │
        │  └───────────────────────┘  │
        └─────────────────────────────┘
```

One computer. It runs your web application *and* the database, side by side. A request comes in, the app handles it, reads or writes the database sitting right there on the same disk, sends the answer back.

> 💡 **Concept notes — what's actually on this box**
> A **server** is just a computer that waits for network requests and answers them. Nothing magical — it's a process listening on a port (like 80 for HTTP).
> A **web application** is your code: it parses the incoming request, decides what to do, and builds a response.
> A **database** is a program that stores data on disk in an organized way and answers queries about it. On this single box, it's a process sitting next to your app, talking over a local socket — no network hop.
> A **request** is one round trip: client asks, server answers. Throughput is measured in **requests per second (RPS)**.

And we're done. We deployed a URL shortener. One machine. No load balancer. No cache. No replicas. No "considering scale." Just a box that does the thing.

Here's the part most books get wrong. They look at this and say *"but it's not real! Where's the load balancer! Where's the cache!"* And then they introduce eight components to fix problems we don't have yet.

We're not going to do that. We're going to keep this exact box and ask one question: **what would actually make us change it?**

---

## Pause. What is "architecture," really?

Let me say something blunt before we go further.

Architecture isn't about drawing every component you've heard of. Architecture is about *responding to load.*

A single box can take you remarkably far. A modern server — say 8 cores, 32 GB of RAM — can comfortably handle **thousands of requests per second** for a simple app. If your URL shortener has 100 users, this box will never sweat. Adding a load balancer and three replicas and a Redis cache would be *negative* work: more things to run, more things to break, more money, zero benefit.

So the discipline is: **don't add a component until a number forces you to.**

To know which number forces what, you have to learn to estimate. Let's learn that now, because it's the single most important skill in the whole book.

---

## Back-of-the-envelope: the only math you need

Interviewers don't want precise numbers. They want to see you turn vague words ("millions of users") into rough load ("about 1,200 writes per second, 12,000 reads per second, 350 GB of new data per year"). That's it. Rounding is encouraged.

Here's the entire toolkit. Memorize these.

**Powers of ten (data sizes):**
- Thousand = 10³ = KB-ish
- Million = 10⁶ = MB-ish
- Billion = 10⁹ = GB-ish
- Trillion = 10¹² = TB-ish

**Seconds in a day:** 86,400. Round it to **100,000 (10⁵)**. This single trick makes everything easy.

**The core move — from daily totals to per-second rate:**

$$\text{requests per second} \approx \frac{\text{requests per day}}{10^5}$$

That's it. Daily total divided by 100,000.

### Let's do our URL shortener

Suppose the product manager says: *"We expect 1 million new short URLs created per day."*

Writes per second:

$$\frac{1{,}000{,}000 \text{ writes/day}}{100{,}000 \text{ sec/day}} = 10 \text{ writes/sec}$$

Ten writes per second. That's *nothing.* A cheap laptop does that.

Now reads. URL shorteners are read-heavy — people click links far more than they create them. A common assumption: **100 reads for every write.** So:

$$10 \text{ writes/sec} \times 100 = 1{,}000 \text{ reads/sec}$$

A thousand reads per second. Still very comfortable for one decent box.

> 💡 **Concept notes — the read:write ratio**
> Almost every system is lopsided. Social feeds, URL shorteners, news sites: *read-heavy* (you read far more than you post). Logging or analytics ingestion: *write-heavy*. Knowing which way a system leans tells you where to spend your effort. A read-heavy system gets fixed with caches and replicas; a write-heavy system gets fixed with queues and sharding. You'll feel both in later chapters.

### Now storage

Each stored URL is, say, the short code + the long URL + a little metadata. Call it **500 bytes** to be safe.

Per day:

$$1{,}000{,}000 \text{ URLs} \times 500 \text{ bytes} = 5 \times 10^8 \text{ bytes} = 500 \text{ MB/day}$$

Per year:

$$500 \text{ MB/day} \times 365 \approx 180 \text{ GB/year}$$

So after a year, ~180 GB. After five years, under 1 TB. **A single modern disk holds that without blinking.**

Stop and notice what just happened. We took "1 million URLs a day" — which *sounds* huge — and discovered it's 10 writes/sec and under a terabyte for years. **The one box is fine.** The estimate told us not to over-build. That is the estimate's main job early on: permission to keep it simple.

---

## So what *would* make us change it?

We keep the one box until a specific thing breaks. Here are the real failure points, roughly in the order they bite:

**1. The box dies.** It's one machine. If its disk fails or it reboots, your *entire service is down*, and if the disk is truly gone, your *data is gone too.* This isn't a load problem — it's a **single point of failure.** Even at 10 users, this is the first real risk. (Fix lives in Ch 2 and Ch 3: more than one machine, and copies of the data.)

**2. Traffic outgrows one box.** Today it's 1,000 reads/sec. Suppose the product takes off and it's 50,000 reads/sec. One box can't serve that. (Fix: Ch 2 — multiple app servers behind a load balancer.)

**3. The database outgrows one box.** Either the data won't fit on one disk, or the query volume saturates one database process. (Fix: Ch 3 replication, Ch 4 sharding.)

**4. Reads repeat themselves.** The same popular links get fetched millions of times, each hitting the disk. (Fix: Ch 5 — caching.)

Notice the pattern. We're not going to add components because a diagram says so. We're going to add each one **the moment a specific number or failure makes the box insufficient — and not one moment sooner.**

---

## The first crack: app and database on the same box

There's one change worth making almost immediately, and it's worth understanding *why*, because it teaches the core reflex of this whole book.

Right now the app and the database share a machine. That's convenient but it couples two things that grow differently:

- The **app** is CPU-bound — it's busy parsing requests and running logic.
- The **database** is memory- and disk-bound — it's busy holding data and reading/writing it.

When they share a box, they fight over the same RAM and disk. A heavy query can starve the app; a traffic spike on the app can starve the database. And you can't scale them independently — if you need more app capacity, you're forced to also pay for database capacity you didn't need.

So the first real move is tiny: **pull the database onto its own machine.**

```
        ┌──────────────┐         ┌──────────────┐
client  │  app server  │  network│   database   │
───────▶│  (your code) │────────▶│   server     │
        └──────────────┘         └──────────────┘
```

> 💡 **Concept notes — what this cost us**
> We gained independent scaling and isolation. But we paid a price: there's now a **network hop** between app and database. A local socket call is microseconds; a network call is milliseconds. Every design move in this book is a trade like this — you fix one thing and pay for it somewhere else. The skill is *naming the cost out loud.* An interviewer who hears "this adds a network round-trip of a few milliseconds per query, which is fine because we're not latency-critical here" is hearing a senior engineer.

That's the whole chapter's lesson in one move: separate things that grow differently, and say what it cost.

---

## What we have now

A two-box system: app server, database server. It comfortably handles our estimated load (10 writes/sec, 1,000 reads/sec, sub-terabyte storage for years). We can scale the app and the database independently.

It still has the big unsolved problem: **if either box dies, we're down.** One app server, one database — two single points of failure. That's the pain that opens the next chapter.

---

## Try it

Before moving on, do these on paper. The arithmetic *is* the skill.

1. A photo-sharing app expects **500 million** photo *views* per day and **5 million** uploads per day. Compute reads/sec and writes/sec. What's the read:write ratio?
2. Each photo averages **2 MB**. How much new storage per day? Per year?
3. At what point (which of the four failure points above) does the single-box design first break for this photo app — and why is it a *different* failure point than for the URL shortener?
4. In one sentence each: name the cost we paid when we split the database onto its own box, and the benefit we got.

*Write your answers in [hld-chapter-1-tryit.md](code/hld-chapter-1-tryit.md).*

---

## The bumper sticker

> *Start with one box. Add a component only when a specific number or failure forces it — and say what it cost.*

Next chapter: the box can die, and the traffic is climbing. Time for more than one app server — and the new problem that creates.

---

<div align="right">

[Chapter 2 →](hld-chapter-2.md)

</div>
