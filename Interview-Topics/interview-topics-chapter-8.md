# Chapter 8: Cloud (GCP and the portable primitives)

*[← Chapter 7](interview-topics-chapter-7.md) · [Contents](interview-topics-README.md)*

- [ ] **Mark as read**

Cloud is usually the "a plus" line on a JD — "GCP a plus," "AWS preferred" — not a gate. That framing is your friend: the interviewer cares less about which provider's console you've clicked through and more about whether you understand the **primitives** every cloud shares. The concept beneath the brand is exactly that portability: GCP, AWS, Azure, and OCI are different names for the same building blocks. Name the primitive and a provider mismatch stops being a problem.

The principle, one last time: **feel the concept beneath the brand name.** "Pub/Sub" and "Kafka" and "SQS" are async messaging. "Cloud SQL" and "RDS" are managed Postgres. Lead with the concept; the brand is a detail.

---

## Lead with what you actually built

> 💡 **Concept notes — specifics beat buzzwords**
> Interviewers can tell the difference between "I've used GCP" and "I built X on GCP." Be concrete about the services *you* shipped on — for backend work that usually means **Pub/Sub** (event-driven producers/consumers), a managed database, object storage, and a deploy pipeline. Specifics about a real system you owned are worth more than a list of service names.

---

## Pub/Sub: your Kafka bridge

> 💡 **Concept notes — Pub/Sub ≈ Kafka, conceptually**
> GCP **Pub/Sub** is async messaging: **topics and subscriptions**, **push vs pull** delivery, **at-least-once** delivery (so **idempotent** consumers — same rule as Kafka, Chapter 4), **ack deadlines**, **dead-letter topics**, and **ordering keys**. This maps almost one-to-one onto Kafka's concepts, which is exactly why Pub/Sub experience is a legitimate bridge in a Kafka interview. If Kafka is your gap and Pub/Sub is your reality, this is the honest pivot in action.

---

## The portable primitives

> 💡 **Concept notes — the same building blocks, renamed**
> Every cloud gives you: **managed databases** (Cloud SQL / RDS / Azure SQL), **object storage** (GCS / S3 / Blob), **IAM + service accounts**, **secrets management**, **autoscaling**, **managed container runtimes** (Cloud Run / GKE, ECS/EKS, AKS), and **CI/CD**. Architecture reasoning — load balancing, queues, caching, scaling — is provider-agnostic ([HLD](../HLD/hld-README.md) teaches it cloud-neutrally for this reason). Having worked across providers is a *strength*: it proves you learn a new console fast because you already know the concepts.

> 💡 **Concept notes — answering a cloud mismatch**
> "We're on AWS but your background is GCP" is not a real objection — and you should say so calmly: the primitives are identical, only the names differ, and you've reasoned about managed DBs, object storage, IAM, queues, and autoscaling regardless of brand. Don't over-index on one provider's naming when the interviewer cares about the concept. Speak portably.

---

## Try it

Answer aloud:

1. Describe a real system you built on a cloud — be specific about which services and why.
2. How does Pub/Sub compare to Kafka? Where do the concepts line up?
3. "Our stack is AWS, your background is GCP — is that a problem?" Answer it.
4. Name the portable primitives every cloud provides, and the cross-provider equivalents for two of them.
5. Why does the HLD primer teach architecture cloud-neutrally, and how does that help you in a cloud-specific interview?

*Write your answers in [interview-topics-chapter-8-tryit.md](code/interview-topics-chapter-8-tryit.md).*

## The bumper sticker

> *Cloud is usually a "plus," not a gate — and every provider is the same primitives under different brand names. Lead with what you actually built, use Pub/Sub as your Kafka bridge, and treat a provider mismatch as a non-issue: the concepts are identical, the console is a weekend.*

That covers the classic Java-stack brands. If your world is Python, Chapter 9 does the same for **FastAPI** — the framework you'll most often be asked about there.

---

<div align="right">

[Chapter 9 →](interview-topics-chapter-9.md)

</div>
