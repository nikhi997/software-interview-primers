# Interview-Topics — the 10-chapter named-technology recall layer (Java · Spring Boot · Postgres · Kafka · Redis · auth · cloud · FastAPI · platform operations)

A 10-chapter primer on the **named technologies** that job descriptions list by brand — "Java, Spring Boot, Kafka, Postgres, Redis, GCP, FastAPI, Kubernetes, Terraform" — and that interviewers probe with "have you used X?" Written in the same conversational style as the LLD, HLD, DSA, Behavioural, AI/ML, and Foundations primers in this collection.

Core principle: **feel the concept beneath the brand name.**

---

## Why this track exists

The other six tracks teach *concepts* on purpose — they avoid vendor and framework specifics so the ideas transfer anywhere. Foundations teaches what an index is; HLD teaches what a message queue is; LLD teaches dependency inversion. But a real job description rarely says "we need someone who understands caching." It says **"Redis."** It doesn't say "event streaming" — it says **"Kafka."** Not "dependency injection" — **"Spring Boot."**

This track is the bridge. Each chapter takes one named technology a backend JD asks for, and answers the two questions an interviewer actually has:

1. **"Do you know this tool well enough to be productive day one?"** — the must-know recall.
2. **"Do you understand the *concept* underneath, or just the brand?"** — the follow-up that separates a memorized answer from a real one.

That second question is the whole game, and it's why this track points *down* to the concept books constantly. Kafka is a partitioned, replayable **log**. Redis is a **cache** (mostly). Spring is **dependency injection** with conveniences. When you can name the concept beneath the brand, you can answer any follow-up — and you can honestly bridge a gap ("I've used GCP Pub/Sub, which is the same concept as Kafka") instead of bluffing.

## The one idea

Every "have you used X?" question is really *"do you understand the concept X implements?"* A brand name is a label on a mechanism. Interviewers test the mechanism. So for each technology, learn the **one-line concept** it is, then the handful of specifics that prove you've actually touched it. Brand on top, concept underneath — that's how you answer the recall question *and* survive the follow-up.

## How this track is different from the others

This is the only track that is deliberately **vendor-specific**, because that's what JDs are. So it's built for **fast recall and honest gap-bridging**, not deep teaching:

- Each chapter is a **recall card grown into a chapter**: the must-knows, the questions you'll actually be asked with strong answer sketches, where to go deeper (the concept books), and the traps that expose a shallow answer.
- The depth stops at "competent practitioner who can field a follow-up." For the *why* beneath any concept, the chapter links the relevant Foundations / HLD / LLD chapter.
- A recurring move is the **honest pivot**: when you haven't used a tool in production, name the concept you *have* used and bridge. Chapter 4 (Kafka) builds the template; it works for any gap.

## Reading order

Read the chapters your JD names; they're independent. A typical backend JD touches most of them.

- Chapter 1: Java core *(collections, concurrency, the JVM — the language fluency screen)*
- Chapter 2: Spring Boot *(DI, REST, JPA & transactions, testing — usually the headline skill)*
- Chapter 3: PostgreSQL *(indexes, query plans, ACID & isolation, schema — where "Have" gets exposed as shallow)*
- Chapter 4: Kafka *(partitions, consumer groups, delivery semantics — and the honest-pivot template for any gap)*
- Chapter 5: Redis *(cache-aside, eviction, invalidation, the non-cache uses)*
- Chapter 6: Microservices, REST & system design *(boundaries, idempotency, the outbox, the design arc)*
- Chapter 7: Auth *(authentication vs authorization, sessions vs JWT, OAuth2/OIDC, auth across microservices)*
- Chapter 8: Cloud *(GCP specifics, and the portable primitives that survive a cloud switch)*
- Chapter 9: FastAPI *(the Python web framework — ASGI async, Pydantic, Depends; the parallel to Spring Boot)*
- Chapter 10: Platform engineering & production operations *(containers, orchestration, delivery, IaC, secrets, telemetry, safe rollout, incidents)*

**Field guide:** [One authenticated order through the stack](interview-topics-stack-map.md) — one concrete request traced across gateway, auth, framework, Redis, Postgres, outbox, Kafka, cache, and platform operations.

**Drill deck:** [Honest pivots for named-technology gaps](interview-topics-honest-pivots.md) — scored 60-second drills for bridging unfamiliar brands without implying experience you do not have.

**Appendix:** a per-technology glossary and a full interview question bank by chapter — the skim-the-morning-of reference.

Role split: the **chapters** are recall cards per tool, the **appendix** is the morning-of reference, the **stack map** integrates tools across one request, and the **pivot deck** rehearses honest gap-bridging.

## How to study

Same spaced method as Foundations — this track is tested by *speaking*:

- **Session 1 (read):** read the chapter, absorb the concept-beneath-the-brand framing. Don't take notes.
- **Session 2 (recall, next day):** close the file, write each technology's one-line concept + must-knows from memory, then check.
- **Session 3 (say it out loud):** answer the "Try it" questions aloud as if to an interviewer — especially the honest-pivot for any gap.

≈1–1.5 hours per chapter — shorter than the teaching tracks, because these are recall-focused.
Chapter 10 also includes a dependency-free Python lab for rollout gates, redaction, and trace
propagation.

## Prerequisites

- The concept tracks this one points to: [Foundations](../Foundations/foundations-README.md) (SQL, OS, networking), [HLD](../HLD/hld-README.md) (caching, queues, consistency), [LLD](../LLD/lld-README.md) (SOLID, dependency inversion). You can read this track standalone, but the follow-up answers live there.
- Comfort writing code in at least one backend language.

## The bumper sticker

> *A job description names tools; an interviewer tests the concepts underneath them. Learn the one-line concept beneath each brand — Kafka is a log, Redis is a cache, Spring is dependency injection — and you can answer the recall question, survive the follow-up, and honestly bridge any gap instead of bluffing it.*

---

<div align="right">

[Chapter 1 →](interview-topics-chapter-1.md)

</div>
