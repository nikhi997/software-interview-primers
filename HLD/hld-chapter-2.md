# Chapter 2: When one machine isn't enough

*[← Chapter 1](hld-chapter-1.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

End of last chapter we had two boxes: one app server, one database server. It handles our load fine. But it has a problem we named and didn't fix: **if the app server dies, the whole service is down.** And we have no headroom — if traffic doubles, one box can't take it.

We named the feeling: *one of anything is a single point of failure, and one of anything has a ceiling.* The fix for both is the same word: **more than one.**

Let's add a second app server.

---

## The naive move (and why it breaks)

Just run the app on two boxes.

```
client ──▶ app server A ──▶ database
client ──▶ app server B ──▶ database
```

Now the question: when a request comes in, *which* server gets it? The client doesn't know there are two. It just knows one address.

You need something in front that takes every incoming request and hands it to one of the servers. That something is a **load balancer.**

```
            ┌──────────────┐
client ────▶│              │───▶ app server A ──┐
client ────▶│ load balancer│───▶ app server B ──┼──▶ database
client ────▶│              │───▶ app server C ──┘
            └──────────────┘
```

> 💡 **Concept notes — the load balancer**
> A **load balancer (LB)** is a box (or managed service) that sits in front of your app servers. Clients talk to *it*. It forwards each request to one of the servers behind it, spreading the load. Common strategies: **round-robin** (just rotate through them), **least-connections** (send to the server handling the fewest requests right now), or **hashing** (send the same client to the same server). It also does **health checks** — if server B stops responding, the LB notices and stops sending it traffic. That single feature is what removes the app-server single-point-of-failure: a dead server just gets routed around.

So with three app servers behind a load balancer:
- **No single point of failure on the app tier.** One dies, the LB routes around it.
- **Horizontal headroom.** Need more capacity? Add server D. Add server E. The LB spreads load across all of them.

> 💡 **Concept notes — horizontal vs vertical scaling**
> **Vertical scaling (scale up):** make the one box bigger — more CPU, more RAM. Simple, but there's a hard ceiling (the biggest machine you can buy) and it's a single point of failure.
> **Horizontal scaling (scale out):** add more boxes. No real ceiling, and survives a box dying. The catch: your app has to be *able* to run on many boxes at once. That catch is the whole rest of this chapter.

---

## The hidden trap: state on the server

Here's where beginners get burned, and it's the most important idea in the chapter.

Suppose your app stores something *in the server's memory* between requests. The classic example: login sessions.

```
User logs in → app server A creates a session in its RAM → returns "you're logged in"
Next request → load balancer sends it to server B → server B has no idea who you are → "please log in"
```

The user gets randomly logged out, because the LB sent them to a *different* server that doesn't have their session. The app worked perfectly on one box. It breaks the instant there are two — not because of load, but because it kept **state** locally.

This is the rule that makes horizontal scaling possible:

> **Make your app servers stateless.** Any request can go to any server and get the same result. No request depends on something a *specific* server happens to remember.

Where does the state go instead? Out of the app server, into a shared place that *all* servers can reach:
- Sessions → a shared store like Redis, or a signed token the client carries (a JWT).
- Uploaded files → shared blob storage (Ch 9), not the server's local disk.
- Anything that must persist → the database, not server RAM.

> 💡 **Concept notes — stateless ≠ no state anywhere**
> Stateless doesn't mean the system forgets things. It means the *app servers* don't hold the only copy of anything important. State still exists — it just lives in a shared tier (database, cache, blob store) that every app server can reach equally. The app servers become interchangeable, disposable workers. You can kill one, add one, replace one, and nothing is lost. That disposability is the entire point.

### Try it in your head

Why can't we just configure the load balancer to *always* send the same user to the same server (so server A keeps their session)? That's called **sticky sessions**, and it's a real option — but list the cost. (Answer: if server A dies, everyone "stuck" to it loses their session anyway; and load gets uneven because you can't freely rebalance. Sticky sessions trade away the very disposability that made horizontal scaling good. Usually better to externalize the state.)

---

## Redoing the estimate: how many app servers?

Estimation tells us *how many* boxes, not just whether to scale.

Say one app server handles **1,000 requests/sec** comfortably (a reasonable rough number for a simple app). Our URL shortener at peak needs, from Ch 1, ~1,000 reads/sec + 10 writes/sec ≈ 1,000 RPS. So **one server is technically enough** — but we run *at least two or three* anyway. Why?

**Redundancy, not just capacity.** If you run exactly enough servers to handle the load, then the moment one dies you're *under* capacity and the rest get overwhelmed — a cascading failure. The rule of thumb: run enough that you can **lose one and still serve peak load.** This is called **N+1 redundancy.** Need 1 server's worth of capacity? Run 2. Need 4? Run 5.

Now suppose the product takes off: 50,000 reads/sec. At 1,000 RPS/server that's 50 servers, plus one for redundancy → **~51 servers** behind the load balancer. Because they're stateless, this is just... more identical boxes. No redesign. *That's* the payoff of statelessness.

---

## Wait — is the load balancer now the single point of failure?

Sharp question, and exactly the kind an interviewer loves when *you* raise it.

Yes. We removed the app-server SPOF and seemingly created a new one: if the load balancer dies, everything is unreachable.

In practice this is solved by running the load balancer **redundantly too** — two LBs, with automatic failover (if the primary dies, DNS or a floating IP points at the backup). Managed load balancers from cloud providers do this for you and present a single reliable address. The mental model to carry: *whenever you add a box to remove a single point of failure, check whether the new box is itself a single point of failure, and answer for it.*

---

## What we have now

```
              ┌──────────────┐
client ──────▶│     load     │──▶ app server A ──┐
client ──────▶│   balancer   │──▶ app server B ──┼──▶ database
client ──────▶│ (redundant)  │──▶ app server C ──┘
              └──────────────┘
```

- App tier scales horizontally and survives a box dying.
- App servers are **stateless** — any request to any server.
- Load balancer is itself redundant.

But look at the right side. Every app server still talks to **one database.** All those stateless, scalable, redundant app servers funnel into a single database box. We can add fifty app servers, but they all read and write the *same* database. That database is now:
1. A single point of failure again (if it dies, all fifty app servers have nothing to talk to), and
2. The new bottleneck (one box can only serve so many queries).

We moved the problem one tier to the right. That's the pain that opens Chapter 3.

---

## Try it

1. An app keeps a per-user shopping cart in the app server's memory. It runs fine on one server. List exactly what goes wrong when it scales to three servers behind a round-robin load balancer, and the fix.
2. You measure that one app server handles 800 RPS before latency spikes. Your peak load is 6,000 RPS. How many servers do you run if you want to survive losing one at peak? Show the arithmetic.
3. "Sticky sessions" let you keep session state on the app server by always routing a user to the same box. Name two costs of this versus externalizing sessions to a shared store.
4. You add a load balancer to remove the app-server single point of failure. In one sentence, explain why the load balancer doesn't just *move* the SPOF, and what makes that true.

*Write your answers in [hld-chapter-2-tryit.md](code/hld-chapter-2-tryit.md).*

---

## The bumper sticker

> *Scale out by making servers stateless and identical — then the only question left is how many. Every box you add to kill a single point of failure, check that it isn't a new one.*

Next: fifty app servers, one database. The database is now the wall. Time to give the data more than one box.

---

<div align="right">

[Chapter 3 →](hld-chapter-3.md)

</div>
