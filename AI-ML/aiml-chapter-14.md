# Chapter 14: Shipping AI features

*[← Chapter 13](aiml-chapter-13.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

A working prototype and a shipped feature are different animals. The prototype answers one question in a notebook; the feature answers a million questions a day, fast enough that users don't leave, cheap enough that finance doesn't panic, and reliably enough that it doesn't wake you at 3 a.m. This chapter is about the production realities that turn an LLM demo into a *product* — and they're exactly the engineering concerns that distinguish an "AI Engineer" from someone who's done a tutorial. It's the first of three chapters on production realities — this one on the core tradeoffs, then security and cost.

The mindset shift: in a demo, **quality** is everything. In production, you're juggling quality **against latency, cost, and reliability** — and engineering the tradeoffs.

---

## Latency: LLMs are slow, design around it

LLM calls are *slow* by software standards — often hundreds of milliseconds to many seconds, because the model generates one token at a time (Chapter 9) and bigger/smarter models are slower. Users feel every bit of it.

> 💡 **Concept notes — managing latency**
> - **Streaming:** send tokens to the user *as they're generated* rather than waiting for the full answer. It doesn't reduce total time, but the perceived wait drops hugely — this is why chat UIs type the answer out. Use it almost always for user-facing text.
> - **Model choice:** smaller/faster models answer quicker and cheaper. Don't use your biggest model for a task a small one handles fine (more on this below).
> - **Fewer / parallel steps:** each agent step and each retrieval adds latency; minimize round-trips, and run independent calls in parallel.
> - **Shorter context:** more input tokens = slower (and pricier). Don't stuff the prompt with more than you need.
> "It's correct but takes nine seconds" is a real product failure, not a minor polish item.

---

## Cost: every token is metered

You pay per token, input *and* output (Chapter 9), on every single call. What's trivial in a demo becomes a serious bill at scale, and managing it is a core part of the job.

> 💡 **Concept notes — controlling cost**
> - **Right-size the model:** match model to task difficulty. Use a cheap small model for classification/extraction/routing; reserve the expensive large model for genuinely hard reasoning — and a **reasoning model** (Ch 9), which burns extra "thinking" tokens, only for genuinely hard *reasoning* tasks, since it's the priciest and slowest option. A common pattern is **routing/cascading** — a cheap model handles easy cases and only escalates hard ones to the expensive model.
> - **Caching:** if the same (or very similar) question comes in repeatedly, cache the answer instead of re-calling the model. **Semantic caching** uses embeddings (Chapter 7) to match *similar* questions, not just identical strings. Huge savings for common queries.
> - **Trim tokens:** shorter prompts and retrieved context (Chapter 11) cut cost on every call — and RAG that retrieves *only* the relevant chunks is cheaper than dumping whole documents.
> - **Cap output length:** don't let the model ramble when a sentence will do.
> Cost-per-request × requests-per-day is a number you should be able to estimate. Being able to say "I'd route easy cases to a small model and cache common answers" is a strong, practical signal.

---

## The big decision: prompt vs RAG vs fine-tune

When an LLM feature isn't good enough, you have three levers, and choosing well — in the right order — is one of the most important applied-AI judgments. It ties together Chapters 10, 11, and 9.

> 💡 **Concept notes — the improvement ladder (climb in this order)**
> 1. **Prompt engineering first** (Ch 10): cheapest, fastest to iterate. Better instructions, examples, structure. *Always start here* — surprisingly often it's enough.
> 2. **RAG next, if the problem is missing knowledge** (Ch 11): the model lacks facts or needs current/private data, or it's hallucinating. Give it the data instead of hoping it memorized.
> 3. **Fine-tune last, if the problem is behavior/style/format** (Ch 11): you need a consistent voice, a narrow specialized task, or a rigid output style that prompting can't reliably enforce — and you have good training examples. Most expensive and slowest to update; reach for it only when prompting + RAG genuinely fall short.
> The discipline: **prompt → RAG → fine-tune**, cheapest lever first. The classic mistake is jumping straight to fine-tuning (expensive, slow, often the wrong fix). "I'd exhaust prompting, add RAG if it's a knowledge gap, and only fine-tune for behavior I can't get otherwise" is the answer that shows judgment.

---

## Reliability: build for when the model misbehaves

The model is non-deterministic (Chapter 9) and the API is a third-party dependency that can be slow, rate-limited, or down. Production code plans for all of it.

> 💡 **Concept notes — reliability patterns**
> - **Validate and retry:** check the output (valid JSON? passes guardrails? — Ch 13); if it's malformed, retry, possibly with a corrective nudge. Never assume the model returned what you asked for.
> - **Fallbacks:** have a plan when the model fails, times out, or is rate-limited — a default response, a simpler model, a cached answer, or graceful "try again."
> - **Timeouts & rate-limit handling:** treat the LLM like any external service — set timeouts, back off and retry on rate limits, handle outages.
> - **Idempotency for actions:** if an agent (Ch 12) might retry, make sure it doesn't send the email twice.
> "It worked every time I tried it" is not reliability; designing for the times it *won't* is.

> 💡 **Concept notes — provider fallback without semantic roulette**
> A fallback provider is not a drop-in retry unless it supports the behavior your application depends on. Models differ in tool schemas, structured-output guarantees, tokenization, safety behavior, and supported context. Put them behind a versioned adapter, normalize errors and responses, and maintain a **capability matrix** for each route. Fail over only to a model that passes the same contract and eval slice; otherwise degrade to a human-safe response. Avoid retrying across several providers blindly — that can multiply latency, cost, and side effects.

> 💡 **Concept notes — version, canary, and rollback the whole AI configuration**
> Treat the deployed unit as a bundle: model/provider version, prompt version, tool schemas, retrieval/index version, guardrails, and routing policy. Pin versions where the provider permits it, run offline evals before a change, then canary a small traffic slice while comparing quality, latency, cost, and safety. Keep the prior bundle deployable so rollback is one configuration change, not an emergency rewrite. If a provider retires a model, migrate deliberately through the same eval-and-canary gate; "latest" is not a release strategy.

> 💡 **Concept notes — an LLM call is just another downstream dependency**
> Here's the reframe that turns all of the above from "new AI problems" into "problems you already know how to solve": an LLM API is, architecturally, **just another downstream dependency** — one that happens to be slow, costly, non-deterministic, and occasionally down. Every reflex you built in the HLD track applies directly. It's slow → **cache** repeated or similar calls (above; HLD Ch 5) and push non-urgent work onto a **queue** to process asynchronously (HLD Ch 6). It's rate-limited and can spike → apply **rate limiting and backpressure** (HLD Ch 8). It can hang or fail → **timeouts, retries with backoff, and fallbacks** (a cheaper model, a cached answer, a graceful "try again"). It can stall and drag your app down with it → **isolate** it so its latency doesn't cascade. This is why most "AI products" are really ordinary systems with one unusual dependency wired in: **the LLM is a component inside your architecture, not the architecture.** Treat it like any other flaky third-party service and your system-design instincts carry over wholesale.

---

## LLMOps: it doesn't end at launch

Like any ML system, an LLM feature needs ongoing care — the operational layer often called **LLMOps**.

> 💡 **Concept notes — LLMOps / running it over time**
> - **Logging & observability:** record prompt/model versions, source IDs, latencies, costs, validation outcomes, and redacted tool metadata so you can debug and audit. Sample raw content only where justified, with access controls and retention limits; logs must not become an unrestricted second copy of user data.
> - **Monitoring quality in production:** watch the eval metrics and user signals (Ch 13) over time; quality can **drift** as usage patterns change or as you swap models.
> - **Versioning:** prompts, models, and retrieval data all change — version them so you can reproduce behavior and roll back a bad change.
> - **Continuous evaluation:** re-run your eval set (Ch 13) on every prompt/model change, and feed real production failures back into it.
> - **Model updates:** providers deprecate and upgrade models; a model swap can subtly change behavior, so re-evaluate before adopting one. (This is the operational face of the field's volatility — build so you can swap models without rewriting everything.)
> The theme: **shipping is the start, not the end** — an LLM feature is a living system you observe, measure, and maintain.

> 💡 **Concept notes — three "ops," don't conflate them**
> The word "ops" gets attached to three different things, and interviewers notice when you blur them:
> - **MLOps** — operating the *models you train and deploy*: data and training pipelines, feature stores, model versioning, serving, and watching for **drift** so you know when to retrain. It's classic-ML-and-beyond production discipline (the MLE / platform world).
> - **LLMOps** — the LLM-era slice of that (this section): since you usually *don't* train the model, the moving parts shift to **prompts, retrieval data, evals, and model swaps** — you version and monitor *those* instead of a training pipeline.
> - **AIOps** — the odd one out and a *different axis entirely*: it means **using AI to run IT operations** — anomaly detection on metrics, log analysis, automated incident response. It's an ops-tooling category next to the observability material in HLD Ch 12, and has nothing to do with shipping an AI feature.
> Quick test: MLOps and LLMOps are about *operating the AI you built*; AIOps is about *using AI to operate your systems.* Don't let a résumé line or an interview question slide the three together.

---

## Try it

1. Your LLM feature is accurate but takes 8 seconds to respond. The total generation time can't easily shrink. What's the first thing you do to fix the *user experience*, and why does it help?
2. Describe the prompt → RAG → fine-tune ladder. For each, give the symptom that tells you to use it.
3. Your AI feature's monthly bill is 5× the budget. Name three concrete techniques to cut cost without abandoning the feature.
4. What is semantic caching, and how does it save more than a plain exact-match cache?
5. A teammate says "the model always returns valid JSON, I tested it ten times." Why is that not good enough for production, and what do you add?
6. Name three things you'd log and monitor for a live LLM feature, and what each one helps you catch.
7. A teammate says the LLM API is "a whole new kind of dependency." Push back: name four HLD reflexes (from caching to fallbacks) that apply to it unchanged.
8. Distinguish MLOps, LLMOps, and AIOps in one sentence each. Which one is *not* about operating the AI you built?
9. Your primary provider fails. What must be true before traffic can safely move to a fallback model, and when should the system degrade to a human instead?
10. Why must a rollback restore the prompt, model, tool schemas, and retrieval version as one tested bundle rather than changing only the model name?


---

## The bumper sticker

> *Shipping AI means engineering tradeoffs the demo ignored: stream to hide latency, right-size and cache to control cost, climb the prompt→RAG→fine-tune ladder cheapest-first, and design for the times the model misbehaves. The launch is where the real work — observing, evaluating, maintaining — begins.*

Next, two production taxes the demo hid that deserve their own chapters: keeping the system *safe* from attackers, and keeping it *cheap* at scale.

---

<div align="right">

[Chapter 15 →](aiml-chapter-15.md)

</div>
