# Companion: Multi-region and event-driven design drills

*[Contents](hld-README.md) · [Visual deepdive](hld-visual-deepdive.md) · [Appendix](hld-appendix.md)*

This is a **companion, not Chapter 17**. The sixteen chapters teach the component vocabulary and the interview ritual. This workbook applies that vocabulary to two pressures the worked problems only touch: surviving the loss of a region, and keeping business state aligned with an event stream.

Do not begin with "active-active" or "Kafka." Begin with a failure and a requirement:

```text
What broke?
  -> what must still work?
  -> what data may be stale or lost?
  -> what is the smallest mechanism that meets that promise?
  -> what new failure, security boundary, and bill did it create?
```

Each drill is deliberately solution-*bounded*, not solution-prescriptive. The acceptance checks tell you what a credible design must explain; they do not dictate a vendor or one canonical diagram.

## How to run a drill

Use a 35-minute interview clock:

1. **5 min — scope and promises.** Functional scope, users/regions, data residency, RPO, RTO, consistency, and what may degrade.
2. **5 min — estimate.** Per-region traffic, data growth, event rate, cross-region bandwidth.
3. **5 min — contracts.** API/event schema, ownership, idempotency key, partition key.
4. **10 min — grow the diagram.** Start with one region. Add a second only in response to latency, residency, or recovery pressure.
5. **5 min — failure trace.** Walk one timeout, duplicate, region loss, replay, or poison event.
6. **5 min — tradeoffs.** Correctness, availability, security, operability, and cost.

For every arrow, label **sync or async**, **source of truth**, **retry owner**, and **maximum acceptable age** when relevant.

---

## Decision cards

These are lookup cards, not answers to paste into every design.

### Active-passive

One region serves traffic; another holds enough replicated state and capacity to take over.

**Earn it when:** disaster recovery matters more than serving writes locally everywhere.

**You must specify:**
- cold, warm, or hot standby;
- replication mode and achievable RPO;
- detection, promotion, DNS/route change, and achievable RTO;
- how failback avoids overwriting writes accepted after promotion;
- whether standby capacity is reserved or provisioned during recovery.

**Cost:** idle or underused capacity, failover machinery, regular drills, cross-region replication.

### Active-active

Multiple regions serve traffic at the same time.

**Earn it when:** users need local latency, a region loss must not stop service, or policy requires regional serving.

**You must specify:**
- where each record is writable;
- how requests remain near their owning data;
- conflict prevention or resolution;
- behavior during an inter-region partition;
- how global uniqueness and cross-region workflows work.

**Cost:** conflict semantics, harder debugging, more data transfer, duplicated capacity, broader security exposure.

Active-active compute does not imply active-active writes. A common middle ground is active app tiers in many regions with each data item having one **home region** for writes.

### Event-driven flow

A service commits its own state, records an outbox event in the same local transaction, and a relay publishes it. Consumers record event IDs in an inbox or make effects naturally idempotent.

**Earn it when:** independent consumers react at different rates, producers must not share consumer uptime, or replay is a real requirement.

**You must specify:** event owner, schema/version, partition key, retention, retry policy, dedupe scope, replay effect, DLQ operations, and observability.

**Cost:** eventual consistency, duplicate handling, ordering scope, schema evolution, lag, and operational recovery.

---

## Drill 1 — Regional product catalog

**Prompt.** An online catalog currently runs in Virginia. Customers in Europe and Asia see slow product pages. Catalog edits happen a few thousand times per day; reads happen hundreds of thousands of times per second. Prices must respect country-specific rules. European customer profile data must remain in the EU.

**Pressure to feel.** Distance dominates read latency, but making every region a writer would create conflict machinery for a mostly-read workload. Residency applies to customer data, not necessarily the public catalog.

**Design task.**
- Add geo-routing and at least one new region.
- Separate public catalog, regional price view, and customer profile by ownership and residency.
- State whether each dataset is active-passive, single-writer with replicas, or multi-writer.
- Define behavior when catalog replication is delayed or one region is isolated.

**Acceptance checks.**
- Routing considers health and residency, not only nearest geography.
- A user never crosses a prohibited data boundary through failover, logs, backups, or analytics.
- Public catalog reads remain useful when the source region is unavailable.
- Price staleness has an explicit maximum age and visible fallback.
- Cross-region transfer and duplicate-cache cost are estimated.

**Follow-ups.**
1. Marketing now requires a price change to be visible worldwide in under five seconds.
2. EU regulation forbids support engineers outside the EU from reading profile payloads.
3. The nearest region is healthy, but its catalog replica is 20 minutes behind.

---

## Drill 2 — Checkout with a disaster-recovery promise

**Prompt.** Checkout runs in one region. The business asks for **RPO ≤ 30 seconds** and **RTO ≤ 10 minutes** after a full regional loss. It can tolerate browsing during failover, but must not oversell inventory or charge a card twice.

**Pressure to feel.** "Put it in two regions" does not define recovery. Inventory and payment correctness need narrower, stronger mechanisms than browsing.

**Design task.**
- Choose cold, warm, or hot active-passive and justify it from the RTO.
- Trace order, inventory reservation, payment request, and confirmation.
- Define replication and backup separately.
- Show detection, promotion, traffic switch, reconciliation, and failback.

**Acceptance checks.**
- The acknowledged-write path is consistent with the claimed 30-second RPO.
- Payment uses an idempotency key stable across retries and failover.
- Inventory reservation has one authority or a conflict-proof allocation scheme.
- Backups are isolated from replicated corruption/deletion and are restore-tested.
- The 10-minute RTO includes human/automation decision time, capacity, routing TTLs, and dependency readiness.

**Follow-ups.**
1. Finance changes RPO to zero for captured payments.
2. The primary region returns after the standby has accepted writes for an hour.
3. The payment provider's webhook arrives in both regions.

---

## Drill 3 — Global collaborative documents

**Prompt.** Users in three continents edit shared documents. Local typing must feel instant. A document's edits must converge, comments must not appear before the text they reference, and enterprise tenants choose the region where document contents live.

**Pressure to feel.** Low-latency local writes and a single global order pull in opposite directions. Residency limits where payloads can travel.

**Design task.**
- Choose a home-region, single-writer, CRDT/OT, or hybrid model.
- Define ordering scope for edits, comments, and unrelated documents.
- Route a user close to compute without silently moving regulated data.
- Explain offline edits, reconnect, conflict handling, and snapshots.

**Acceptance checks.**
- The design distinguishes convergence from strong consistency.
- Causal relationships have an explicit mechanism; wall clocks alone are not the order.
- Region failover does not violate the tenant's residency policy.
- Encryption keys, logs, search indexes, and backups follow the same residency boundary as primary data.
- The design names latency and egress costs of cross-region collaboration.

**Follow-ups.**
1. Legal hold requires immutable edit history.
2. Two users edit offline for a day.
3. A tenant moves its residency choice from EU to Canada.

---

## Drill 4 — Order placed, five consumers

**Prompt.** Committing an order should trigger inventory, email, loyalty points, fraud analysis, and analytics. Today the order service calls all five synchronously. One slow consumer makes checkout fail.

**Pressure to feel.** The order must commit without sharing every consumer's availability, but "DB write then publish" has a gap.

**Design task.**
- Introduce an outbox and event relay.
- Define the `OrderPlaced` event contract and owner.
- Choose a partition key and explain what order it preserves.
- Give each consumer a retry and idempotency strategy.

**Acceptance checks.**
- Order state and intent to publish commit atomically in one local transaction.
- Relay duplicates are expected, not hand-waved away.
- Inventory and loyalty effects dedupe in the same transaction as their state change.
- Email's external side effect has an explicit provider idempotency or reconciliation story.
- Analytics can lag without blocking checkout.
- Event schema evolution does not require a coordinated deploy of all consumers.

**Failure trace.** Walk crashes:
1. before order commit;
2. after order/outbox commit but before publish;
3. after publish but before marking outbox delivered;
4. after consumer state commit but before broker acknowledgement.

---

## Drill 5 — Ordering without a global bottleneck

**Prompt.** A marketplace emits `ListingCreated`, `PriceChanged`, `ListingSold`, and `ListingRemoved`. Millions of listings change independently. A search consumer must never resurrect a sold listing because it processed an old price event late.

**Pressure to feel.** Global order is unnecessary; per-listing order is essential. Retries and parallel consumers create reordering.

**Design task.**
- Pick event key, partition count, and consumer concurrency.
- Add entity versioning and define behavior on a gap.
- Explain partition reassignment and hot listings.
- Define replay from the beginning into a new search index.

**Acceptance checks.**
- Events for one listing have a stable order, while unrelated listings process in parallel.
- Search applies only a newer version and treats duplicate versions idempotently.
- Missing versions trigger retry/reconciliation rather than silent corruption.
- Replay writes to an isolated target or uses a replay-safe effect.
- Retention is long enough for the stated replay objective.

**Follow-ups.**
1. One celebrity listing receives 20% of all updates.
2. Partition count doubles.
3. A producer bug emits version 43 before version 42.

---

## Drill 6 — Poison messages, retries, and the DLQ

**Prompt.** A shipping consumer fails on one malformed address. The broker retries immediately forever, blocking later orders in that partition.

**Pressure to feel.** Retrying a permanent error is not resilience. Moving an event aside restores flow but creates operational debt.

**Design task.**
- Classify transient, permanent, and unknown failures.
- Set bounded backoff, jitter, attempt count, and per-message timeout.
- Define the dead-letter queue record and replay workflow.
- Preserve the evidence needed to fix or compensate.

**Acceptance checks.**
- A poison message cannot block healthy traffic forever.
- The DLQ stores original payload reference, schema version, error, attempts, timestamps, and trace/correlation IDs without leaking restricted data.
- Alerting is based on age/rate/business impact, not merely DLQ non-emptiness.
- Replay is authenticated, audited, rate-limited, idempotent, and can target a small selection.
- There is an owner and deletion/retention policy; the DLQ is not a graveyard.

**Follow-ups.**
1. The bug affected 10 million events.
2. Payloads contain payment details.
3. Replaying fixed events would send duplicate customer emails.

---

## Drill 7 — Rebuild a projection by replay

**Prompt.** A new recommendation feature needs six months of purchase events. Existing consumers only processed events live. The team wants to replay history without harming checkout or duplicating loyalty points.

**Pressure to feel.** Replay is a second workload with old schemas and side effects. "Reset the offset" is not a complete plan.

**Design task.**
- Separate the new projection's consumer group and storage.
- Estimate replay throughput, duration, and production headroom.
- Handle schema evolution and deleted-user/privacy requirements.
- Define cutover from replay to live tail.

**Acceptance checks.**
- Replay cannot invoke unrelated side effects.
- Production traffic receives capacity priority and backpressure.
- Old event schemas are readable or explicitly migrated.
- A watermark/checkpoint supports resumable replay.
- Cutover has no gap or double-count between historical and live processing.
- Erasure and residency policies apply to retained events and derived projections.

---

## Drill 8 — Active-active wallet: challenge the premise

**Prompt.** A product manager asks for active-active wallet writes in every region so balance updates are always local and the wallet remains writable during any regional partition.

**Pressure to feel.** Two isolated regions can each spend the same money. Availability and low latency do not repeal the invariant.

**Design task.**
- Challenge or narrow the requirement.
- Offer at least two alternatives: home-region writes, escrowed regional limits, or a globally coordinated ledger.
- Explain user experience during a partition.
- Define reconciliation and audit.

**Acceptance checks.**
- No answer relies on last-write-wins for money.
- The chosen model states where a spend obtains authority.
- Failure mode is explicit: reject, queue, use a bounded offline allowance, or accept a compensating risk.
- Ledger entries are immutable, idempotent, and traceable.
- Security covers key custody, privileged access, and cross-region replication.
- Cost compares always-on capacity and coordination latency with the business value.

This drill is passed when you can say, politely and precisely, **which combinations of promises cannot all be met**.

---

## Drill 9 — Regional notification platform

**Prompt.** A platform sends email, SMS, and push notifications for teams worldwide. Tenants choose allowed delivery regions. Providers rate-limit by country. Some campaigns are scheduled; security codes are urgent. A provider outage must not delay codes behind marketing traffic.

**Pressure to feel.** This combines geo-routing, residency, queues, ordering, priorities, retries, and external side effects.

**Design task.**
- Partition tenant configuration and message payloads by allowed region.
- Separate priority lanes and bulkheads.
- Route to regional providers with health and cost in mind.
- Design outbox/inbox, provider idempotency, status events, DLQ, and replay.

**Acceptance checks.**
- Security-code traffic has reserved capacity and tighter expiry than campaigns.
- A retry after unknown provider outcome cannot casually send twice.
- Failover respects tenant residency and provider-country rules.
- Status transitions tolerate duplicate/out-of-order callbacks using versions.
- Expired notifications are dropped, not delivered late.
- Per-tenant encryption, quotas, audit, and deletion are explicit.
- The cost model includes provider rates, inter-region transfer, standby workers, and retained event storage.

---

## Cross-cutting review sheet

After any drill, grade the design from 0–2 on each row.

| Area | 0 | 1 | 2 |
|---|---|---|---|
| Failure-first | Started with products/tools | Named a failure | Derived each major component from a failure or requirement |
| Regional mode | Said active-active/passive only | Chose a mode | Defined writes, failover, failback, split behavior, and capacity |
| Routing/residency | Nearest region only | Mentioned policy | Health, policy, data, logs, backups, and keys stay compliant |
| RPO/RTO | Said "high availability" | Gave numbers | Numbers map to mechanisms and rehearsed evidence |
| Event atomicity | Dual write | Outbox named | Local transaction, relay duplicates, and consumer dedupe traced |
| Ordering/replay | Claimed ordered/exactly once | Named a key | Scope, versions, gaps, retention, checkpoint, and safe effects covered |
| Retry/DLQ | Retry forever | Bounded attempts | Classification, backoff, owner, secure replay, and alerts covered |
| Security | "Encrypt it" | Auth + encryption | Threat boundary, least privilege, key/data locality, audit, retention |
| Cost | Ignored | Named one cost | Capacity, egress, storage, operations, and business value compared |
| Degradation | Everything fails | Named fallback | Core path, stale limits, load shedding, and recovery are explicit |

**Passing bar:** no zero, and at least 15/20. A high score with an impossible invariant is still a fail.

---

## Closing prompts

Answer each in one minute:

1. When does active-passive beat active-active even if budget is unlimited?
2. Why can active-active application servers still have single-writer data?
3. How can geo-routing violate residency even when the primary database is compliant?
4. What exactly does an outbox make atomic, and what duplicate remains?
5. Why is ordering normally scoped to a key or partition?
6. What makes replay different from ordinary retry?
7. What operational promise does a DLQ create?
8. Why is "exactly once" incomplete without naming the boundary?
9. Which costs grow fastest as regions are added?
10. What evidence proves an RTO instead of merely claiming one?

The target is not a more elaborate diagram. It is a design whose failure behavior, recovery promise, security boundary, and bill are as deliberate as its happy path.

<div align="right">

[Visual deepdive →](hld-visual-deepdive.md) · [Appendix →](hld-appendix.md) · [Contents](hld-README.md)

</div>
