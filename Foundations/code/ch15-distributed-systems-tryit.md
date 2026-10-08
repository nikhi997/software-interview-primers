# Chapter 15: When one machine becomes many — Try it

Answer without reopening the chapter. Draw timelines where a prose answer hides an ordering or crash window.

## Partial failure, deadlines, and retries

1. A payment request times out. Draw at least four possible timelines consistent with the silence. What can the caller honestly claim?
2. Give a retry policy for a read-only inventory lookup: retryable failures, attempt cap, exponential delays, jitter, and total deadline.
3. Explain why a timeout is not cancellation and why an operation may finish after its caller gives up.

## Idempotency, replication, and order

4. Design an idempotency-key record for `POST /payments`. What is stored, for how long, and which steps must be atomic?
5. Compare asynchronous and synchronous replication for a user profile and a bank transfer.
6. With five replicas, choose `W` and `R` for one read-heavy and one write-heavy feature. State what quorum does **not** solve.
7. Give a system needing per-key order but not global order. Choose the key and the version/sequence mechanism.

## Coordination and delivery

8. Why does `threading.Lock()` not coordinate two servers? Replace it with two store-enforced alternatives.
9. Contrast quorum and consensus using one concrete decision for each.
10. Trace an at-least-once consumer crashing (a) before its state change and (b) after the change but before acknowledgement. Add inbox deduplication.
11. Draw the transactional outbox. Where can duplicate publication still happen?
12. Challenge the phrase "exactly once": exactly once in which component, and what happens to an external side effect?

## Degradation and recovery

13. A recommendation service is failing. Design a bounded core product response using deadlines, a breaker, bulkheads, and a fallback.
14. Pick RPO and RTO values for a social profile and a bank ledger. Map each number to backup, replication, standby, and drill choices.
15. Explain why replication is not a backup and name the last successful restore test your design would record.

## Self-check

You are done when you can explain, without notes:

- why silence is ambiguous;
- why retry and idempotency belong together;
- why order needs a scope;
- why an in-process lock is not distributed coordination;
- why "exactly once" needs a boundary;
- why RPO and RTO are product requirements before they are infrastructure settings.

[← Back to Chapter 15](../6-distributed-systems/ch15-when-one-machine-becomes-many.md)
