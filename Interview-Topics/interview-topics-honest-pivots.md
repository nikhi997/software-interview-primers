# Drill deck: honest pivots for named-technology gaps

*[← Chapter 10](interview-topics-chapter-10.md) · [Contents](interview-topics-README.md)*

The chapters are recall cards per tool. The appendix is the skim-the-morning-of reference. The stack map integrates tools across one request. This drill deck is different: it makes you rehearse **honest gap-bridging** out loud, under a score.

This is not permission to imply experience you do not have. The win condition is the opposite: say the truth cleanly, map the concept underneath, then prove you can reason about the unfamiliar tool without pretending you shipped it.

---

## How to score one answer

Give yourself 60 seconds. Then score each row from 0 to 2.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Honesty | Implies production use you do not have | Names the gap, but vaguely | States exactly what you have and have not run in production |
| Specificity | Generic tool words | One concrete system or task | Concrete system, workload, and responsibility |
| Conceptual mapping | Brand-name swapping only | One shared concept | Two transferable concepts, correctly mapped |
| Caveat awareness | Claims equivalence | Mentions a difference | Names a material difference and why it matters |
| Technical depth | No failure mode | One surface failure | Designs or debugs a concrete flow/failure |
| Concision | Rambling or defensive | Understandable but bloated | Crisp 60-second answer with a clear close |

Target score: **10+ out of 12**. Anything below 8 means you need another pass.

Use the six beats every time:

1. **Truth boundary** — exactly what you have and have not run in production.
2. **Adjacent evidence** — one real system you did use.
3. **Map** — two transferable concepts.
4. **Caveat** — one material difference, so you never claim equivalence.
5. **Demonstrate** — design or debug one concrete flow/failure in the unfamiliar tool.
6. **Close** — hands-on proof or a learning plan.

---

## Drill 1 — Kafka ↔ Pub/Sub

**Prompt:** "Have you used Kafka in production?"

| Beat | 60-second answer |
|---|---|
| Truth boundary | "I have not operated Kafka in production. My production event-driven work has been on Pub/Sub." |
| Adjacent evidence | "I built producers and consumers around topics/subscriptions, handled retries, and made handlers safe for duplicate delivery." |
| Map | "The transferable concepts are at-least-once delivery and consumer idempotency. The second is decoupling side effects from the request path with an event stream." |
| Caveat | "Kafka is a partitioned log with offsets and retention; Pub/Sub is subscription-based and hides more broker mechanics. So I would not claim Kafka ops experience." |
| Demonstrate | "For an `OrderCreated` flow, I would key Kafka messages by `order_id` if I need per-order ordering, commit offsets only after durable processing, and store processed event IDs so payment does not double-charge on redelivery." |
| Close | "To close the brand gap, I would run a local Kafka producer/consumer, force a crash before offset commit, and show the idempotent retry path." |

**Probes**

1. Operational failure: "Consumer lag is rising. What do you check first?"
2. Tradeoff: "When would Kafka be better than Pub/Sub or a normal queue?"
3. Implementation detail: "What does the message key control, and what ordering does Kafka not give you?"

**Score:** honesty __/2 · specificity __/2 · mapping __/2 · caveat __/2 · depth __/2 · concision __/2 = __/12

---

## Drill 2 — Spring Boot ↔ FastAPI

**Prompt:** "Our backend is Spring Boot. Your recent work is FastAPI. Is that a problem?" Use the reverse if Spring is your real production tool.

| Beat | 60-second answer |
|---|---|
| Truth boundary | "I have production experience with FastAPI, not the same depth with Spring Boot. I should be clear about that." |
| Adjacent evidence | "I have built HTTP routes, request validation, dependency-injected services, centralized errors, and integration tests in a real Python service." |
| Map | "The transferable concepts are dependency injection and boundary validation. `Depends` maps to Spring's container handing collaborators in; Pydantic validation maps to bean validation at the request edge." |
| Caveat | "Spring has a richer container and proxy model — `@Transactional`, AOP, bean scopes — so I would pay attention to those Spring-specific gotchas instead of assuming the frameworks are identical." |
| Demonstrate | "For `POST /orders`, I would keep the controller thin, validate the body, inject an order service, start the transaction in the service layer, and centralize 400/409/500 error mapping. In Spring I would check that `@Transactional` is reached through the proxy, not self-invoked." |
| Close | "My proof plan is a small Spring Boot order API with constructor injection, bean validation, a transactional service, and a slice test." |

**Probes**

1. Operational failure: "Latency spikes after a deploy. Which framework-level mistakes do you investigate?"
2. Tradeoff: "What does FastAPI async buy you that Spring MVC may not, and when does it buy nothing?"
3. Implementation detail: "Why is constructor injection easier to test than field injection?"

**Score:** honesty __/2 · specificity __/2 · mapping __/2 · caveat __/2 · depth __/2 · concision __/2 = __/12

---

## Drill 3 — Redis ↔ local/application caching

**Prompt:** "Have you used Redis for caching and rate limiting?"

| Beat | 60-second answer |
|---|---|
| Truth boundary | "I have used application-level caching patterns; I have not owned a production Redis cluster for this use case." |
| Adjacent evidence | "I have cached expensive reads inside a service, added TTLs, and invalidated entries after writes so stale data was bounded." |
| Map | "The transferable concepts are cache-aside and invalidation. Redis externalizes the cache so multiple instances share it; the same miss → source-of-truth → fill flow still applies." |
| Caveat | "A local cache dies with the process and is not shared; Redis adds network calls, eviction policy, persistence choices, and outage behavior. So the operational profile is materially different." |
| Demonstrate | "For `GET /orders/{id}`, I would read Redis first, fall back to Postgres on a miss, write back with a TTL, and delete the key after an order update. For rate limiting, I would combine increment and first expiry with Lua or a transaction, then decide fail-open or fail-closed if Redis is unavailable." |
| Close | "To prove it, I would add Redis to a small service, show a cache hit avoiding Postgres, then kill Redis and show the chosen fallback." |

**Probes**

1. Operational failure: "A hot key expires and Postgres gets hammered. What happened?"
2. Tradeoff: "When is a local cache better than Redis?"
3. Implementation detail: "Why do you need TTLs even if you invalidate on writes?"

**Score:** honesty __/2 · specificity __/2 · mapping __/2 · caveat __/2 · depth __/2 · concision __/2 = __/12

---

## Drill 4 — AWS ↔ GCP

**Prompt:** "We're on AWS. Your cloud experience is mostly GCP. How quickly can you be productive?"

| Beat | 60-second answer |
|---|---|
| Truth boundary | "My hands-on production cloud work has been mostly GCP, not AWS administration." |
| Adjacent evidence | "I have deployed services on managed container runtimes, used managed databases, configured service identities, handled secrets, and debugged logs/metrics around event-driven workers." |
| Map | "The transferable concepts are managed infrastructure primitives and least-privilege service identity. Cloud SQL maps to RDS, GCS to S3, Pub/Sub to SNS/SQS or Kafka-style messaging depending on the need, and Cloud Run/GKE to App Runner/ECS/EKS." |
| Caveat | "The IAM syntax, networking defaults, quotas, and console workflows differ. I would not pretend those are automatic; I would pair or read the runbooks before changing production policy." |
| Demonstrate | "For the order service, I would ask where containers run, which managed Postgres/Redis/Kafka equivalents are used, how service roles reach them, where secrets live, and which metrics define health. Those questions transfer cleanly across providers." |
| Close | "My learning plan is to map the team's AWS services to primitives, deploy one non-production service, and make one runbook update after verifying it with a teammate." |

**Probes**

1. Operational failure: "The service cannot connect to the database after deploy. What cloud layers do you check?"
2. Tradeoff: "Managed runtime vs Kubernetes: what do you gain and lose?"
3. Implementation detail: "What's the difference between a user's identity and a service account or IAM role?"

**Score:** honesty __/2 · specificity __/2 · mapping __/2 · caveat __/2 · depth __/2 · concision __/2 = __/12

---

## Drill 5 — OAuth2 ↔ sessions

**Prompt:** "Have you implemented OAuth2/OIDC, or only session-based login?"

| Beat | 60-second answer |
|---|---|
| Truth boundary | "I have implemented session-cookie auth; I have not been the primary owner of a production OAuth2/OIDC integration." |
| Adjacent evidence | "I have handled login state, server-side session storage, logout/revocation, `401` vs `403`, and role-based authorization in an application." |
| Map | "The transferable concepts are authentication versus authorization, and a credential carried on each request. A session ID is opaque and looked up server-side; a JWT access token is signed and verified by the API." |
| Caveat | "OAuth2 is delegated authorization, and OIDC adds identity with an ID token. That redirect/token lifecycle is different from a simple first-party session, especially refresh tokens, scopes, issuer/audience validation, and early revocation." |
| Demonstrate | "For `POST /orders`, I would validate the access token signature, issuer, audience, expiry, and `orders:create` scope. Expired or invalid token returns `401`; valid token without scope returns `403`. I would keep access tokens short-lived and protect refresh tokens carefully." |
| Close | "To close the gap, I would build a small OIDC login against a real provider in a dev app and document the token validation path." |

**Probes**

1. Operational failure: "A signing key rotates and valid users start getting `401`. What do you inspect?"
2. Tradeoff: "Why are sessions easier to revoke than JWTs?"
3. Implementation detail: "What is the difference between an access token, refresh token, and ID token?"

**Score:** honesty __/2 · specificity __/2 · mapping __/2 · caveat __/2 · depth __/2 · concision __/2 = __/12

---

## Drill 6 — Postgres ↔ another relational DB

**Prompt:** "We use Postgres heavily. Your production database was MySQL/SQL Server/Oracle. How does that translate?"

| Beat | 60-second answer |
|---|---|
| Truth boundary | "My production depth is stronger in another relational database than in Postgres internals specifically." |
| Adjacent evidence | "I have designed relational schemas, written joins, added indexes for query patterns, debugged slow queries, and used transactions to protect invariants." |
| Map | "The transferable concepts are relational modeling and ACID transactions. B-tree indexes, query planners, isolation, constraints, and connection pools are not Postgres-only ideas." |
| Caveat | "Postgres has its own details: MVCC behavior, `VACUUM`, index types like GIN/partial/expression indexes, default read-committed isolation, and `EXPLAIN ANALYZE` plan shapes. I would learn those specifics rather than claiming every database behaves the same." |
| Demonstrate | "For the order write, I would put `orders` and `outbox_event` in one transaction and enforce a unique idempotency key. If duplicates race, the constraint wins and the app returns the original result or `409`. If a query is slow, I would inspect `EXPLAIN ANALYZE`, check selectivity and index use, then change the index or query." |
| Close | "My proof plan is to load sample order data into Postgres, create the idempotency constraint, run a slow query, and show the plan before and after the index." |

**Probes**

1. Operational failure: "A high-update table gets slower over time. What Postgres-specific issue might be involved?"
2. Tradeoff: "Why not index every column?"
3. Implementation detail: "What does the leftmost-prefix rule mean for a composite index?"

**Score:** honesty __/2 · specificity __/2 · mapping __/2 · caveat __/2 · depth __/2 · concision __/2 = __/12

---

## Drill 7 — Kubernetes / GitOps platform ↔ another orchestrator or deployment system

**Prompt:** "We run Kubernetes with Argo CD. Have you operated that stack in production?"

| Beat | 60-second answer |
|---|---|
| Truth boundary | "I have shipped and operated containerized services through another orchestrator/deployment controller; I have not been the primary production owner of Kubernetes with Argo CD." |
| Adjacent evidence | "I have built immutable images, set health checks and resource sizing, promoted artifacts through gated environments, handled secret delivery, watched rollout telemetry, and rolled back unhealthy releases." |
| Map | "The transferable concepts are scheduling and desired-state reconciliation. A Deployment asks a controller to maintain replicas and roll versions; GitOps asks a controller to reconcile reviewed repository state into the cluster." |
| Caveat | "Kubernetes adds exact object and control-plane semantics—Pods, Deployments, Services, probes, requests/limits, RBAC—and Argo adds sync, health, drift, and promotion behavior. I would not equate another platform's commands or rollback details with those." |
| Demonstrate | "For an order-service canary, I would promote one signed image digest, use startup/readiness/liveness for distinct failure meanings, expose a small traffic cohort, gate on errors/latency/business signals, and keep database changes expand/contract compatible. A failed gate stops exposure and triggers the rehearsed rollback or roll-forward path." |
| Close | "I would close the brand gap by deploying the Chapter 10 lab service to a disposable cluster, deliberately failing readiness and a canary gate, and documenting reconciliation and recovery." |

**Probes**

1. Operational failure: "The database is down. Which probe should fail, and why not restart every Pod?"
2. Tradeoff: "When is a managed container runtime simpler than Kubernetes?"
3. Implementation detail: "What is the difference between an image tag and a digest, and which do you promote?"

**Score:** honesty __/2 · specificity __/2 · mapping __/2 · caveat __/2 · depth __/2 · concision __/2 = __/12

---

## Final self-check

Before you use any answer in an interview, replace the sample truth boundary with your real one. If the honest sentence feels weaker, do not blur it. Strength comes from the next five beats: evidence, mapping, caveat, demonstration, and a concrete learning plan.

## The bumper sticker

> *An honest pivot is not a loophole. It is a disciplined answer: state the gap, prove the adjacent experience, map the concepts, name the difference, debug one real flow, and close with proof. Never borrow production experience you do not have; borrow the concept you genuinely understand.*

---

<div align="right">

[Appendix →](interview-topics-appendix.md)

</div>
