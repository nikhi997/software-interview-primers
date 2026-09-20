# Chapter 6: When work can wait

*[← Chapter 5](hld-chapter-5.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

End of Chapter 5, reads are fast. But look closely at a *write* path. A user signs up. Here's what we make them wait for:

```
user clicks "Sign up"
  → create the account in the database        (50 ms)
  → send a welcome email                       (800 ms — talking to an email provider)
  → generate their profile thumbnail           (1,200 ms — image processing)
  → add them to the analytics pipeline         (300 ms)
  → finally... return "Welcome!"               total: ~2.4 seconds
```

The user stares at a spinner for 2.4 seconds. But ask the honest question: *which of these does the user actually need finished before we can say "Welcome"?*

Only the first one. The account must exist. The email, the thumbnail, the analytics — the user does **not** need those done *right now.* They can happen in the next few seconds, behind the scenes. We're making the user wait for work that could wait.

That's the pain. The fix is to **decouple** the slow optional work from the request, and the tool is a **message queue.**

---

## The idea: hand off the work, answer now

Instead of *doing* the slow work inline, the app drops a **message** ("send welcome email to user 123") onto a queue and immediately returns to the user. Separate **worker** processes pull messages off the queue and do the work whenever they get to it.

```
                          ┌─────────────┐      ┌──────────┐
app server ──"send email"─▶│    QUEUE    │─────▶│ worker 1 │
app server ──"make thumb"─▶│ (messages   │─────▶│ worker 2 │
app server ──"log signup"─▶│  waiting)   │─────▶│ worker 3 │
                          └─────────────┘      └──────────┘
   returns "Welcome!"                          (do the slow
   in 50 ms                                     work later)
```

Now signup is just: create account (50 ms), drop three messages on the queue (a few ms each), return "Welcome!" The user waits ~60 ms instead of 2.4 seconds. The email, thumbnail, and analytics happen moments later, done by workers, with nobody staring at a spinner.

> 💡 **Concept notes — the vocabulary**
> A **message queue** (or message broker) is infrastructure that holds messages until someone processes them. Examples: **RabbitMQ**, **Amazon SQS**, **Apache Kafka**.
> A **producer** puts messages in (here, the app server).
> A **consumer / worker** takes messages out and acts on them.
> **Synchronous** = the caller waits for the result. **Asynchronous (async)** = the caller hands off the work and continues; the result happens later. The queue is how you turn synchronous work asynchronous.

---

## What the queue buys you (beyond speed)

Speed is the obvious win. But the queue gives you three more things that matter just as much:

**1. Decoupling.** The app doesn't know or care who processes the message, or how many workers there are, or whether they're up *right now.* It just drops the message and moves on. Producers and consumers evolve independently.

**2. Load leveling (buffering spikes).** Suppose 100,000 people sign up in one minute during a product launch. Without a queue, 100,000 thumbnail jobs hit your image service at once and crush it. With a queue, all 100,000 messages pile up *in the queue*, and the workers chew through them at their own steady pace. The queue absorbs the spike like a shock absorber. The user-facing signup stays fast the whole time; only the *thumbnails* lag behind by a few minutes — which nobody notices.

**3. Resilience.** If a worker crashes mid-job, or the email provider is down, the message stays in the queue (or goes back into it) and gets retried later. The work isn't lost just because a downstream thing hiccuped. Compare the synchronous version: if the email provider is down, the *entire signup* fails. The queue isolates failures.

> 💡 **Concept notes — load leveling is the killer feature**
> The single most important thing a queue does at scale is *decouple the rate of incoming work from the rate of processing.* Producers can burst; consumers process steadily. Without it, every spike is transmitted directly to your most fragile downstream component. With it, the queue flattens the spike into a manageable stream. Whenever you see "handle traffic spikes" or "ingest a flood of events," think *queue.*

---

## The cost: you traded "done" for "will be done"

Queues aren't free. Naming these costs is the senior move.

**1. Eventual consistency, again.** When you return "Welcome!", the thumbnail does *not* exist yet. For a few seconds the user has an account but a blank avatar. You must design the UX for "not done yet" (show a placeholder). The work is *guaranteed to happen*, but not *yet.* Same eventual-consistency tradeoff we met with replication and caching, in a new costume.

**2. Delivery guarantees — the at-least-once reality.** Most queues guarantee **at-least-once** delivery: a message will be processed, but possibly *more than once* (e.g., a worker processes it, crashes before acknowledging, so the queue redelivers it). This means your workers must be **idempotent.**

> 💡 **Concept notes — idempotency (interview gold)**
> An operation is **idempotent** if doing it twice has the same effect as doing it once. "Set status to PAID" is idempotent (setting it twice = setting it once). "Add $10 to balance" is *not* (twice adds $20). Because queues redeliver, your message handlers must be idempotent — usually by tracking a unique message ID and skipping any ID you've already processed. If an interviewer asks "what if this message is delivered twice?", the answer they want is *"the handler is idempotent — we dedupe on message ID."* Memorize that.

**3. Ordering isn't guaranteed (by default).** With multiple workers pulling in parallel, messages can be processed out of order. If order matters (process "deposit" before "withdraw"), you need ordering guarantees — e.g., Kafka keeps order *within a partition* by routing related messages (same user) to the same partition. Note the echo of sharding: route related things to the same place to keep a property you care about.

**4. More moving parts.** The queue itself is now infrastructure you run, monitor, and keep highly available. If the queue is down, producers can't hand off work. So the queue, like everything, gets run redundantly.

---

## Two flavors of queue (know the difference)

**Task queue (e.g., RabbitMQ, SQS):** a message is a *job to do once.* A worker takes it, does it, and it's *gone.* Good for: send this email, resize this image, charge this card. One message → one action → done.

**Event log / stream (e.g., Kafka):** messages are an *append-only log of events* that can be read by *many* independent consumers, each at its own pace, and replayed. Good for: "user signed up" consumed separately by the email service, the analytics service, *and* the recommendation service — each reads the same event stream independently.

> 💡 **Concept notes — when to reach for Kafka vs a simple queue**
> If one thing needs to happen once → task queue. If *many* systems need to react to the same event independently (and you might add more reactors later), or you need to replay history → event log like Kafka. This maps directly onto the LLD **Observer pattern**: one event, many independent listeners. Kafka is Observer at infrastructure scale. Don't reach for Kafka's complexity when a simple task queue does the job — that's the "don't add a component until forced" rule again.

---

## Async vs sync: the decision rule

How do you know which work to push to a queue? One question:

> **Does the user need this finished before we can answer them?**

- **Yes** → do it synchronously, inline, user waits. (Create the account. Charge the card before confirming the order.)
- **No** → push it to a queue, answer now, do it async. (Email, thumbnails, analytics, search-index updates, notifications.)

A useful tell: anything that's a *side effect* of the main action — notifying, logging, syncing to another system, heavy processing — is usually a queue candidate. The *core state change* the user is waiting on stays synchronous.

---

## What we have now

```
LB ─▶ app servers ─┬─ (sync) ─▶ database / cache  → answer user fast
                   └─ (async) ─▶ QUEUE ─▶ workers ─▶ email, thumbnails,
                                                      analytics, ...
```

User-facing requests are fast because slow side-work is offloaded to workers via a queue, which also absorbs spikes and isolates downstream failures. We pay for it with eventual consistency and the need for idempotent, possibly-out-of-order handlers.

We've made the system fast and well-behaved under bursts. But we've been quietly assuming the data we *do* commit is safe. What does it actually mean for a write to be "saved"? What if a box dies one millisecond after we said "done"? That's durability — and it forces us to confront the famous CAP theorem. Chapter 7.

---

## Try it

1. A user uploads a video. List which steps must be synchronous (user waits) and which should go on a queue, and justify each.
2. Explain load leveling: a launch causes 200,000 image-resize jobs in 30 seconds, but your workers can only do 2,000/sec. What does the queue do, how long until the backlog clears, and why does the user-facing app stay fast?
3. A payment-charge message gets delivered twice due to at-least-once delivery. What goes wrong if the handler isn't idempotent, and exactly how would you make it idempotent?
4. When would you choose Kafka (event log) over a simple task queue? Tie it to the Observer pattern.
5. Give one piece of work that must stay synchronous even though it's slow, and explain why it can't go on a queue.

*Write your answers in [hld-chapter-6-tryit.md](code/hld-chapter-6-tryit.md).*

---

## The bumper sticker

> *If the user doesn't need it finished to get their answer, put it on a queue: you gain speed, spike absorption, and failure isolation — and you pay with eventual consistency and the need for idempotent handlers.*

Next: we keep saying a write is "saved." Time to ask what that actually guarantees when a box dies — and meet CAP.

---

<div align="right">

[Chapter 7 →](hld-chapter-7.md)

</div>
