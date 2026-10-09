# Chapter 16: When every token has a price tag

*[← Chapter 15](aiml-chapter-15.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

The demo cost nothing — a few cents, lost in the noise. Then it shipped, traffic arrived, and the monthly invoice showed up with four more digits than anyone budgeted for. Nothing broke; that's the trap. The feature works *perfectly* and is quietly bankrupting the team, because you're paying per token, on the biggest model, for every request — including the thousands of trivial ones a far cheaper model would have nailed. Chapter 14 introduced cost as one of the three production tradeoffs; this chapter goes deep, because at scale it becomes its own engineering discipline. The mindset: **feel the bill before reaching for the bigger model.**

---

## Where the money actually goes

You can't optimize a cost you can't estimate, so start by being able to do the arithmetic — the same back-of-envelope move the HLD track drills, pointed at tokens.

> 💡 **Concept notes — the cost equation**
> For token-metered APIs, a call costs roughly **input tokens × input rate + output tokens × output rate**. Only combine the token counts if those rates are equal; cached input and reasoning tokens may have separate accounting. Use the provider's current billing rules rather than assuming one price. Three things drive the bill:
> - **Tokens per call:** both the prompt you send *and* the answer generated are metered (Ch 9). A bloated system prompt or a dumped-in document (Ch 11) costs you on every call, forever.
> - **Model choice:** providers price model tiers differently, and larger or reasoning-heavy models are commonly more expensive and slower. The same task on the wrong model is a permanent multiplier; use current provider pricing for the actual estimate rather than memorizing a ratio.
> - **Call volume:** requests-per-day, plus every extra agent step (Ch 12) and retrieval round-trip, each its own metered call.
> The number you must be able to produce on a whiteboard: **cost-per-request × requests-per-day.** "About 2000 tokens a call at $X per million, times 100k calls a day" is the sentence that turns a vague worry into an engineering target.

---

## The optimization ladder — cheapest lever first

Like the prompt→RAG→fine-tune ladder in Chapter 14, cost has an order. Climb from the cheapest, least disruptive move upward, and stop when the bill is acceptable. Don't start at the bottom by rewriting your architecture.

> 💡 **Concept notes — right-size the model (the biggest single win)**
> Most teams overpay because they use one big model for *everything*. But classification, extraction, routing, and short factual answers don't need a frontier model — a small, cheap one handles them fine. **Match model to task difficulty.** Reserve the expensive model for genuinely hard reasoning. This one change often cuts the bill more than all the others combined, because it attacks the per-token multiplier on your highest-volume, easiest traffic.

> 💡 **Concept notes — making a smaller model earn the route**
> "Small" can mean choosing a smaller hosted model or adapting one you serve yourself. Three common techniques reduce serving cost in different ways:
> - **Quantization** stores/executes weights at lower precision, reducing memory and often improving throughput, with a quality cost that must be measured by task and hardware.
> - **Distillation** trains a smaller student to imitate a stronger teacher on representative examples; it can preserve narrow-task behavior but also copy the teacher's mistakes and blind spots.
> - **Task-specific adaptation** gives a compact model a narrow job — routing, extraction, moderation pre-checks — instead of asking it to be a universal assistant.
> None is a free compression button. Benchmark quality, tail latency, throughput, memory, operational burden, and fallback rate on the actual workload. A self-hosted small model may lower marginal inference cost while adding platform and capacity cost.

> 💡 **Concept notes — on-device is a deployment choice**
> A compact model can run on a user's device for offline operation or to avoid sending raw inputs to a server. The constraints shift to memory, battery, thermals, device variation, and safe updates. Quantization may help it fit, but does not prove the task still works. Measure quality and latency on the slowest supported devices, and disclose any server fallback: a local first step does not imply that all data stays local.

> 💡 **Concept notes — routing and cascading**
> You don't have to choose one model globally. **Routing** sends each request to the right-sized model based on its difficulty (a cheap classifier, or rules, decides). **Cascading** is the lazy version: try the cheap model first, and only **escalate** to the expensive one when the cheap answer fails a quality check (Ch 13). The cascade is only as good as that acceptance check: uncertain, safety-sensitive, or contract-invalid outputs must escalate. Measure the **escalation rate** and final task success together; a "cheap" first stage that escalates almost everything merely adds latency and another billable call.

> 💡 **Concept notes — caching (stop paying twice for the same answer)**
> If the same question comes in repeatedly, don't re-call the model — serve the stored answer. **Exact-match caching** catches identical strings. **Semantic caching** goes further: it embeds the query (Ch 7) and reuses the answer for *similar* questions, not just identical ones ("how do I reset my password" ≈ "I forgot my password"). For a support bot where everyone asks the same ten things, this can erase most of your traffic. Many providers also offer **prompt caching** — a discount for reusing a long, static prompt prefix (system instructions, fixed context) across calls, so you're not billed full price for the same preamble every time.

> 💡 **Concept notes — trim the tokens**
> Every token you don't send is a token you don't pay for, on every call: tighten the system prompt, and have RAG retrieve *only* the relevant chunks (Ch 11) instead of dumping whole documents — cheaper *and* often more accurate, since less noise reaches the model. **Cap output length** so the model can't ramble when a sentence will do. Small per-call savings, multiplied by call volume, become real money.

---

## The tradeoff triangle

Cost doesn't live alone. Push it down hard enough and something else gives — usually quality or latency. Optimization is choosing *what* to trade *where*, not minimizing one number blindly.

> 💡 **Concept notes — cost vs latency vs quality**
> These three pull against each other (this is Chapter 14's juggling act seen from the cost corner):
> - Cheaper, smaller models are often *faster* — so cost and latency sometimes align — but may be *lower quality* on hard tasks.
> - Caching cuts both cost and latency, but risks serving a *stale* answer if your data changed.
> - A cascade saves money but adds latency on the hard cases that get retried up the chain.
> You can't max all three. The discipline is to pick the right tradeoff **per workload**: a high-stakes legal summary earns the expensive model; an autocomplete suggestion does not.

> 💡 **Concept notes — when NOT to optimize (the senior signal)**
> The junior mistake is cutting cost *first* — shipping a tiny model that hallucinates to save money no one was actually worried about, tanking the product to fix a non-problem. **Measure first** (Ch 13): know your cost-per-request and which paths dominate the bill, then optimize the expensive, high-volume paths and leave the cheap ones alone. Premature cost-cutting that wrecks quality is as much an error as ignoring cost entirely. "I'd find the few endpoints driving most of the spend and right-size *those*" beats "I'd use the cheapest model everywhere."

---

## Try it

1. Write the cost equation for an LLM feature, then estimate a monthly bill for a feature doing 50k calls/day at ~1500 tokens per call. Make the per-token price up — show the method, not the number.
2. Your feature uses one large model for everything. What's the single highest-impact cost change, and which traffic does it target?
3. Explain routing vs cascading. When does a cascade *add* latency, and to which requests?
4. What does semantic caching catch that exact-match caching misses? Give an example, and name the risk caching introduces.
5. A teammate proposes switching every endpoint to the smallest model to save money. Why might that be the wrong move, and what would you do instead?
6. Cost, latency, quality — pick a workload where you'd happily spend more, and one where you wouldn't. Justify each.
7. Compare quantization and distillation. What cost does each target, and what task-specific eval would stop you from treating either as a free win?
8. A cheap-model cascade escalates 90% of requests. Why might it cost more and respond slower than calling the large model directly, and which metric exposes the problem?


---

## The bumper sticker

> *Every token is metered, so cost is an engineering variable, not a surprise on the invoice. Estimate cost-per-request, climb the cheapest lever first — right-size the model, route and cache the easy traffic, trim the tokens — and spend big only where the problem is genuinely hard.*

Next: the AI features that don't fit in a chat box — images, audio, and video, and why the machinery you already know still runs them.

---

<div align="right">

[Chapter 17 →](aiml-chapter-17.md)

</div>
