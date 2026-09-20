# Chapter 11: Drawing the system

*[← Chapter 10](hld-chapter-10.md) · [Contents](hld-README.md)*

- [ ] **Mark as read**

An HLD interview produces three artifacts on the whiteboard: a **box-and-arrow diagram**, an **API**, and a **data model**. They're how you communicate the design in your head. This chapter teaches you to produce all three cleanly, so that in Part 4 you can focus on *thinking* instead of fumbling with *how to express it.*

The goal isn't artistic diagrams. It's *legible* ones — a picture the interviewer can follow as you talk, that shows you think in terms of components, data flow, and contracts.

---

## Artifact 1: the architecture diagram

A system diagram is **boxes** (components) connected by **arrows** (requests/data flow). Read left-to-right: client on the left, data stores on the right, requests flowing rightward, responses back.

Here's the canonical skeleton you've built across Parts 1–2. Almost every problem is a variation of it:

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

### How to draw it in an interview (the order matters)

Don't draw all of this at once — *grow* it as you reason, exactly as this book did:

1. **Start with the smallest thing that works:** client → app → database. Three boxes.
2. **Add a component only when you hit its pain**, narrating why: "reads are heavy, so I'll add a cache here"; "this work can be async, so a queue here." The interviewer watches your *reasoning*, and a diagram that grows from need is far more convincing than one memorized whole.
3. **Label the arrows** with what flows ("read", "write", "publish event") when it's not obvious.
4. **Keep it legible.** A clear five-box diagram beats a tangled fifteen-box one. You can always zoom into one box when asked.

> 💡 **Concept notes — draw the data flow, not just the boxes**
> The arrows matter as much as the boxes. The interviewer is tracing: *where does a write go? where does a read go? what happens async?* Be able to put your finger on the diagram and trace one request end-to-end ("a redirect comes in here, hits the cache, on a miss goes to this replica, returns"). That tracing — Step 4 of the ritual in Ch 12 — is what the diagram exists to support.

---

## Artifact 2: the API design

Before internals, define the **contract**: what operations the system exposes. This pins down scope and forces clarity about inputs and outputs. For most systems, a small **REST** API over HTTP:

```
POST /urls
  body:    { "long_url": "https://...", "custom_code": "pasta" (optional) }
  returns: { "short_code": "pasta", "short_url": "https://sho.rt/pasta" }
  201 Created  |  409 Conflict (code taken)  |  429 Too Many Requests

GET /{short_code}
  returns: 302 redirect to the long URL
           404 if not found
```

A good API spec shows: the **endpoints**, the **inputs** (body/params), the **outputs**, and the **error cases** (the status codes from Ch 8 — 409, 429, 404). Mentioning the error/limit cases unprompted signals maturity.

> 💡 **Concept notes — REST vs RPC/gRPC vs GraphQL (one line each)**
> **REST:** resources as URLs, HTTP verbs (GET/POST/PUT/DELETE). The default — simple, universal, great for public APIs.
> **gRPC/RPC:** call remote functions directly, compact binary, very fast. Favored for *internal* service-to-service calls where speed matters.
> **GraphQL:** client asks for exactly the fields it wants in one query. Shines when clients need flexible, nested data and you want to avoid over/under-fetching (mobile apps with many screens).
> Default to REST in an interview unless there's a reason (internal hot path → gRPC; flexible client data needs → GraphQL). Name the reason.

> 💡 **Concept notes — idempotent HTTP verbs**
> By HTTP convention, **GET, PUT, DELETE are idempotent** (repeating them has the same effect) and **POST is not** (two POSTs create two things). This connects straight to Ch 6: for an operation that might be retried, design it to be idempotent — e.g., let the client send an **idempotency key** on a POST so a retried payment doesn't charge twice. Saying this in an interview is a strong signal.

---

## Artifact 3: the data model

What you store and how it's organized. Sketch the main **entities**, their key **fields**, and the **relationships** — like the LLD class diagram, but focused on *storage* and *access patterns* rather than behavior.

```
URL
  short_code   (primary key)
  long_url
  created_by   (user id)
  created_at
  click_count

USER
  user_id      (primary key)
  email
  created_at
```

But the data model isn't just "what fields." The high-value decisions are:

**1. SQL or NoSQL?** The single most common data-model question.

> 💡 **Concept notes — SQL vs NoSQL, decided by access pattern**
> **SQL (relational — Postgres, MySQL):** structured rows, rich queries, **joins**, and **ACID transactions** (all-or-nothing, strongly consistent). Choose when you need complex relationships, multi-row transactions, and strong consistency — money, orders, anything relational. The cost: harder to scale writes horizontally (sharding a relational DB is painful).
> **NoSQL (Cassandra, DynamoDB, MongoDB):** flexible schema, built to **shard and scale horizontally** from day one, usually tunable/eventual consistency. Choose for massive scale, simple key-based access, write-heavy or huge datasets where you don't need joins. The cost: weaker transactions, you must design around your queries up front (no ad-hoc joins).
> The deciding question is **your access pattern**: complex relational queries + transactions → SQL; massive scale + simple lookups by key → NoSQL. Modern systems often use *both* (SQL for orders, NoSQL for the activity feed). Justify by access pattern, never by fashion.

**2. What's the index / primary key?** This *is* the access pattern. You look URLs up by `short_code`, so that's the key — making redirects a fast point lookup. If you also need "all URLs by this user," you need an index on `created_by`. Indexes speed reads but slow writes and cost space (Ch 5's tradeoff shape again) — index the fields you *query by*, not everything.

**3. Does it need sharding, and on what key?** Tie back to Ch 4: only if size/writes demand it, and shard on the field matching the dominant query.

---

## Putting the three together — the flow

The three artifacts reinforce each other, and a clean interview produces them in this order:

```
1. API        → defines WHAT the system does (the contract, the scope)
2. Data model → defines WHAT it stores (entities, SQL/NoSQL, keys)
3. Diagram    → defines HOW requests flow through components to serve the API
                using that data
```

API first (it pins scope), then data model (what backs it), then the architecture diagram (how it all connects and scales). In Part 4 you'll see this exact sequence inside the five-step ritual.

> 💡 **Concept notes — the diagram is a conversation, not a deliverable**
> Don't disappear into silent drawing. Narrate as you draw, invite reactions ("does that scope sound right?"), and leave room to grow the diagram when the interviewer adds a requirement. The whiteboard is a shared thinking space — your job is to make your reasoning *visible*, not to produce a perfect picture. An interviewer steering you is a *good* sign; it means they're engaged in your design.

---

## What we have now

You can produce the three artifacts every HLD interview wants — a diagram that *grows* from need, a REST API with its error cases, and a data model with a justified SQL/NoSQL choice and the right keys — and you know the order to produce them (API → data → diagram) and how to narrate while you do it.

That completes the foundation. You have the scaling skeleton (Part 1), the components (Part 2), the vocabulary (Ch 10), and the artifacts (Ch 11). Part 4 puts all of it to work: the interview ritual on a full problem, then three classic worked problems. Chapter 12 starts with the ritual itself, on a URL shortener at scale.

---

## Try it

1. Draw, from memory, the canonical architecture skeleton, and trace a single read request end-to-end with your finger, naming each box it touches.
2. Design the REST API for a pastebin (create a paste, fetch a paste). Include inputs, outputs, and at least two error status codes.
3. For each, pick SQL or NoSQL and justify by access pattern: a banking ledger; a social app's activity feed at billion-user scale; a product catalog with complex filtered search; an IoT sensor ingesting 1M writes/sec.
4. You need to support both "fetch URL by short_code" and "list all URLs created by a user." What keys/indexes does that imply, and what's the cost of adding the second one?
5. Explain why you'd present API before data model before diagram, rather than starting by drawing boxes.

*Write your answers in [hld-chapter-11-tryit.md](code/hld-chapter-11-tryit.md).*

---

## The bumper sticker

> *Three artifacts win the interview: an API that pins scope, a data model justified by access pattern, and a diagram that grows from need — and you narrate all three as you build them.*

Part 3 done. Next: you've designed it and drawn it — now how do you *keep it running?* The deploy, the monitoring, the 2am page — the work the "DevOps people" actually do, and what an interviewer means by "how would you operate this?"

---

<div align="right">

[Chapter 12 →](hld-chapter-12.md)

</div>
