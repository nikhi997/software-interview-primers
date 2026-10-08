# Chapter 15: When one machine becomes many

*[← Chapter 14](../5-bonus/ch14-git.md) · [Contents](../foundations-README.md)*

- [ ] **Mark as read**

On one machine, failure is easy to recognize. A function returns or raises. A process is running or dead. A lock either guards the memory every thread can see or it does not.

Add a second machine and certainty disappears.

Service A sends a request to Service B. No response comes back. Did B never receive it? Did B finish the work and the response get lost? Is B slow, dead, or merely unreachable from A? There is no local instruction that can answer. The network has turned one clean failure into several indistinguishable possibilities.

That uncertainty is the mechanism underneath distributed systems. This chapter stays below the architecture diagrams in the HLD track: it starts with the ambiguous missing response, then derives the safeguards people later name **timeouts, retries, idempotency, replication, quorum, consensus, delivery guarantees, graceful degradation, RPO,** and **RTO**.

Core principle: **feel the uncertainty before naming the distributed-systems abstraction.**

---

## The first break: silence is ambiguous

Imagine an order service asking a payment service to charge $20:

```text
order service                 payment service
      |                             |
      |-------- charge $20 -------->|
      |                             | charge succeeds
      |        X response lost      |
      |<.......... silence ..........|
```

From the order service's point of view, this looks identical to at least four other timelines:

1. The request never left.
2. The request arrived, but the payment service crashed before charging.
3. The payment service is alive but slow.
4. The charge succeeded, but the response was lost.
5. The response is still in flight and will arrive later.

On one machine, a caller and callee share a process boundary and a fate. Across a network, they do not. One side can fail while the other succeeds, or both can remain healthy while the link between them fails. That is **partial failure**.

> 💡 **Concept notes — partial failure**
> A distributed system can be partly alive and partly unreachable. A missing response does not reveal which part failed or whether the requested side effect happened. You cannot remove this ambiguity; you can only bound how long you wait, make repetition safe, and design a useful response when certainty is unavailable.

The first habit is therefore not "retry." It is: **state what is known.** After silence, the honest payment status is `UNKNOWN`, not automatically `FAILED`.

---

## Bound waiting: timeouts are deadlines, not diagnoses

Without a timeout, the order service can wait forever. Its worker stays occupied, connection pools fill, queues grow, and one slow dependency becomes a whole-system outage.

A **timeout** gives up waiting after a bound:

```text
request starts
  -> wait up to 800 ms
  -> response arrives: use it
  -> deadline expires: release resources and report "unknown / unavailable"
```

The timeout does **not** cancel history. B may still be processing the request. It does not prove failure; it only says the caller is no longer willing to wait.

Practical rules:

- Set a deadline from the user's total budget. If the page has 2 seconds, one downstream call cannot consume all 2 seconds.
- Pass the remaining deadline downstream so every hop does not start a fresh full timeout.
- Keep connection and request timeouts distinct: connecting and waiting for work are different phases.
- Observe timeout rates and tail latency; a value guessed once and never measured is not a reliability policy.

> 💡 **Concept notes — timeout vs cancellation**
> A timeout ends the caller's wait. Cancellation is a best-effort message asking downstream work to stop. The work may already have committed and may ignore or never receive cancellation. Code must remain correct even when timed-out work finishes later.

---

## Repetition helps only when it is controlled

If the failure was a dropped packet or a brief restart, trying again may succeed. If the dependency is overloaded, immediate retries make it worse: every original request becomes several requests, queues lengthen, more calls time out, and callers retry again. That feedback loop is a **retry storm**.

The mechanism-first retry policy:

```text
attempt 1 fails with a transient error
  -> wait 100 ms + random jitter
attempt 2 fails
  -> wait 200 ms + random jitter
attempt 3 fails
  -> wait 400 ms + random jitter
budget exhausted
  -> stop and surface a bounded failure
```

This is **exponential backoff**: increase the delay after each failure. **Jitter** adds randomness so thousands of clients do not wake and retry in lockstep. A **retry budget** caps total attempts or total elapsed time.

Retry only failures likely to be transient: a timeout, connection reset, or explicit `503 Service Unavailable`. Do not blindly retry invalid input, failed authorization, or a business rejection. Honor `Retry-After` when a server supplies it.

The important catch: a retry repeats the operation even when the first attempt may have succeeded. Before retrying a side effect, make repetition safe.

---

## Make repetition safe: idempotency

"Set the order status to `PAID`" can happen twice with the same final result. "Add $20 to the merchant balance" cannot. The first is naturally **idempotent**; the second needs protection.

A client supplies a stable idempotency key for one logical operation:

```text
POST /payments
Idempotency-Key: checkout-783-attempt-1

payment service transaction:
  1. look up key
  2. if completed, return the stored result
  3. if absent, record key + perform charge + store result atomically
```

Both the original and the retry use the same key. A *new* purchase uses a new key. The deduplication record and side effect must share a transaction or atomic store operation; otherwise a crash between "charge" and "remember key" recreates the duplicate.

> 💡 **Concept notes — idempotency is a semantic promise**
> HTTP verb conventions help (`GET`, `PUT`, and `DELETE` are intended to be idempotent), but the server's implementation decides whether repetition is safe. An idempotency key identifies one business operation, not one network attempt. Store enough of the first result to return the same outcome on replay, and define how long keys remain valid.

Timeout + bounded retry + idempotency form one unit. A retry policy without idempotency can duplicate effects; idempotency without a bounded retry policy can still overload the system.

---

## One copy dies: derive replication

Now the service is reachable, but its only disk dies. The data is gone. The smallest fix is a second copy:

```text
write
  -> primary copy
  -> replica copy
```

That is **replication**. It can improve durability, availability, or read capacity, but only according to when you acknowledge and where you read.

- **Asynchronous replication:** acknowledge after the primary, copy later. Fast, but the latest acknowledged writes can be lost if the primary dies before copying.
- **Synchronous replication:** wait for another copy before acknowledging. Safer, but adds network latency and may reject writes when replicas are unavailable.
- **Read replicas:** spread reads, but may return stale data because replication takes time.

Replication creates a new problem: copies can disagree. "We have three copies" says nothing by itself about which value a read returns, who may accept writes, or what happens during a network split. Those are separate consistency and coordination choices.

---

## Consistency is about observations; ordering is about relationships

Two clients write `A` and `B` near the same time. Different replicas may receive them in different orders. Ask what observers are promised.

Useful guarantees, from stricter to looser:

- **Strong / linearizable consistency:** after a successful write, later reads behave as if there were one up-to-date copy.
- **Read-your-own-writes:** the writer sees its update, though other users may briefly see older data.
- **Causal consistency:** if B depends on A, everyone observes A before B; unrelated writes may appear in either order.
- **Eventual consistency:** if writes stop, replicas converge; reads may be stale meanwhile.

Ordering also needs a scope. "All events are globally ordered" is expensive and often unnecessary. A chat needs messages ordered **within one conversation**; a ledger needs entries ordered **within one account**. Partitioning related events by `conversation_id` or `account_id` gives a useful local order without forcing unrelated traffic through one global sequencer.

> 💡 **Concept notes — clocks do not create truth**
> Wall clocks on different machines drift, and network delay can reorder arrival. A timestamp is useful metadata, not automatic proof of a global sequence. When order matters, define the scope and use a sequence number, version, log position, or single writer for that scope.

Choose the weakest guarantee that preserves the product invariant. A stale like count is usually acceptable; a stale available balance may not be.

---

## Quorum: overlap reads and writes

Suppose there are `N = 3` replicas. A write waits for `W = 2`; a read consults `R = 2`.

```text
N = 3 copies
W = 2 acknowledgements for a write
R = 2 copies consulted for a read

W + R = 4 > 3
```

Because the read and write sets must overlap, at least one consulted copy has the accepted write. This overlap rule is the intuition behind **quorum**:

```text
W + R > N
```

Increasing `W` spends latency and write availability for fresher, safer writes. Increasing `R` spends read latency and availability. Quorum is not magic:

- the reader still needs versions or timestamps to choose the newest response;
- concurrent writes still need conflict handling;
- sloppy quorums and hinted handoff may weaken the simple guarantee;
- quorum agreement on a value is not automatically leader election or a total event order.

The mechanism is overlap. The abstraction is a tunable consistency policy.

---

## Consensus: the narrow boundary where agreement is unavoidable

Sometimes replicas must agree on one answer before proceeding:

- Which node is the leader?
- Who owns this lease?
- What is the next committed log entry?
- Has this configuration change been accepted?

That is the territory of **consensus** protocols such as Raft and Paxos. They use a majority so two isolated minorities cannot both make progress and claim conflicting authority.

```text
five voters split 3 | 2
  -> side with 3 can form a majority and continue
  -> side with 2 cannot safely commit
```

The minority sacrifices availability to prevent split-brain.

> 💡 **Concept notes — quorum vs consensus**
> A read/write quorum is an overlap rule for replicated data. Consensus is a protocol for a group to choose one ordered history or authority despite failures. They both use majorities, but they solve different problems. In application design, use the database, queue, or coordinator's proven implementation; do not invent a consensus protocol in business code.

And keep the boundary narrow. You may need consensus for leader election or metadata, not for every cached profile read.

### A lock is not automatically distributed coordination

`threading.Lock()` from Chapter 9 protects memory shared by threads in **one process**. A second process has a different lock object; a second machine cannot even see it.

```text
server A: Lock() protects A's memory only
server B: Lock() protects B's memory only
```

For a cross-server seat claim, put the invariant where all contenders meet:

- an atomic database update with a condition and version;
- a row lock inside a transaction;
- a unique constraint;
- compare-and-set in a shared store;
- only when necessary, a distributed lease/lock with ownership tokens and expiry.

A distributed lock is not a bigger mutex. Its holder can pause, lose the lease, and resume believing it still owns it. Use **fencing tokens**—monotonically increasing ownership numbers that the protected resource rejects when stale—when an old holder could act after its lease expires.

Prefer atomic data-store operations over a separate distributed lock when possible. The data store already sits at the shared boundary and can enforce the invariant with fewer failure windows.

---

## Messages: delivery is an agreement between broker and consumer

A producer writes an event. A broker delivers it. A consumer changes its database. Where can a crash occur?

```text
receive message
  -> apply database change
  -> acknowledge message
```

If the consumer crashes **before** the database change, the message must return. If it crashes **after** the change but **before** the acknowledgement, the broker redelivers and the change may happen twice.

That yields the practical guarantees:

- **At-most-once:** acknowledge before or do not retry. No duplicates, but loss is possible.
- **At-least-once:** retry until acknowledged. No silent loss while retained, but duplicates are possible.
- **Effectively once:** at-least-once delivery plus idempotent processing or atomic deduplication makes the business effect happen once.

"Exactly once" is always scoped. A broker may process a record exactly once into its own transactional log while an email provider still receives two calls. Ask: exactly once **where**, across **which boundary**, and with **which side effects**?

An **inbox** table records processed event IDs in the consumer's transaction. A **deduplication window** bounds how long those IDs remain. Ordering is commonly guaranteed only within a partition, so route events sharing an ordering requirement to the same partition.

---

## Two writes, one intent: the outbox mechanism

An order service updates its database and publishes `OrderPlaced`. Two independent writes create two failure windows:

```text
DB commit succeeds -> publish fails     => order exists, event missing
publish succeeds   -> DB commit fails   => event describes an order that does not exist
```

The **transactional outbox** turns them into one local transaction:

```text
database transaction:
  INSERT order
  INSERT outbox_event(OrderPlaced)
  COMMIT

relay:
  read unpublished outbox rows
  publish to broker
  mark published
```

The relay may publish twice if it crashes before marking the row, so consumers still need inbox deduplication or idempotent handlers. Outbox solves **atomic state + intent to publish**; it does not promise duplicate-free end-to-end delivery.

---

## When a dependency is sick: degrade instead of cascade

Suppose recommendations time out. The product page can still show title, price, and stock. Failing the entire page turns an optional dependency into a critical one.

Graceful-degradation mechanisms:

- **Fallback:** omit recommendations or use a default.
- **Stale cache:** serve a slightly old value when fresh computation is unavailable.
- **Circuit breaker:** after repeated failures, stop calling the dependency, fail fast, and probe recovery after a cooldown.
- **Bulkhead:** separate thread pools, connection pools, or queues so one dependency cannot consume every resource.
- **Load shedding:** reject low-priority work before core work.
- **Bounded queues:** refuse excess work instead of growing until memory is exhausted.

Retries, breakers, and fallbacks must share one latency budget. Three retries behind a 500 ms timeout can quietly make a "2 second" fallback take much longer than 2 seconds.

> 💡 **Concept notes — graceful degradation**
> Decide which features are essential before the outage. Preserve the smallest useful response, label stale or missing data honestly, and protect the core path from optional work. Degradation is a product decision expressed through technical boundaries.

---

## Recovery has two numbers: RPO and RTO

Redundancy handles expected component failure. Disaster recovery asks what happens when a whole region, account, or dataset is lost.

Two product questions become two objectives:

- **RPO — Recovery Point Objective:** how much committed data may we lose? An RPO of 5 minutes means restore may return to a point up to 5 minutes before the incident.
- **RTO — Recovery Time Objective:** how long may the service remain unavailable? An RTO of 30 minutes means restore service within 30 minutes.

The mechanisms follow the numbers:

| Requirement | Mechanism it pressures you toward |
|---|---|
| Smaller RPO | more frequent backups, replicated logs, synchronous cross-site writes |
| Smaller RTO | warm standby, automated failover, pre-provisioned capacity, rehearsed runbooks |
| Protection from deletion/corruption | versioned, immutable, separately authorized backups |
| Proof recovery works | scheduled restore tests and regional failover drills |

Replication is not a backup. It eagerly copies good writes, accidental deletes, and corruption. A backup is an independent recovery point. Likewise, a failover plan never rehearsed is only a document.

RPO and RTO are objectives, not properties a vendor name grants automatically. Measure achieved recovery against them.

---

## The complete failure-first checklist

When one machine becomes many, walk the mechanism in this order:

1. **Silence:** what states are indistinguishable after no response?
2. **Waiting:** where is the deadline, and does it propagate?
3. **Repetition:** which failures are retried, with what backoff, jitter, and budget?
4. **Effects:** what key or atomic operation makes repetition safe?
5. **Copies:** when is a write acknowledged, and how stale may reads be?
6. **Order:** which events must be ordered, and within what key?
7. **Agreement:** is overlap enough, or is there a narrow consensus boundary?
8. **Delivery:** can work be lost, duplicated, or replayed, and where is deduplication?
9. **Degradation:** what useful response survives a dependency failure?
10. **Recovery:** what are the RPO and RTO, and when was restore last tested?

This is not an architecture template. It is a set of questions generated by the ways independent machines fail.

---

## Try it

1. A payment request times out. Name at least four possible timelines consistent with that observation. What status should the order show before reconciliation?
2. Design a retry policy for a read-only inventory lookup. Which errors are retryable, what backoff and jitter do you use, and what total deadline stops the attempts?
3. A retried `POST /payments` must not charge twice. Trace the idempotency-key record and charge through a crash at every step; where must atomicity live?
4. With `N=5`, choose `W` and `R` for (a) write-heavy analytics counters and (b) inventory reservations. Explain the latency and availability cost; do not quote only `W + R > N`.
5. A chat system needs order within each conversation but not across all chats. Pick a partition key and explain why wall-clock timestamps alone are insufficient.
6. Contrast a read/write quorum with consensus. Give one problem for each and one case where application code should delegate the mechanism to infrastructure.
7. Explain why a `threading.Lock` cannot prevent two app servers from selling the same seat. Give two store-enforced alternatives and one hazard of a distributed lease.
8. Trace a consumer crash immediately before and immediately after its database commit. Which delivery guarantee produces each outcome, and how does an inbox table make the effect idempotent?
9. An order write and event publish must agree. Draw the outbox flow, then name the duplicate it still permits.
10. Set an RPO and RTO for profile photos and for a bank ledger. Which mechanisms differ, and how would you prove recovery rather than assume it?

*Write your answers in [ch15-distributed-systems-tryit.md](../code/ch15-distributed-systems-tryit.md).*

---

## The bumper sticker

> *The network turns failure into uncertainty: bound the wait, make repetition safe, coordinate only where invariants demand it, and prove you can recover.*

That closes the Foundations track. The HLD track turns these mechanisms into architecture choices; the appendix and companions turn them into fast recall.

---

<div align="right">

[Appendix →](../foundations-appendix.md)

</div>
