# Chapter 13: Knowing it works, keeping it safe

*[← Chapter 12](aiml-chapter-12.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

A demo that works once is easy. A product that works *reliably*, for thousands of users, on inputs you never imagined, without saying something false or harmful — that's the hard part, and it's what companies actually pay for. The discipline that gets you there is **evaluation** (evals): systematically measuring whether your LLM system does what it should. This is the chapter that most separates people who've *shipped* AI from people who've only *played* with it, and interviewers know it. The mindset to adopt: **eval-first** — you can't improve, or trust, what you don't measure.

---

## Why evaluating LLMs is uniquely hard

With a classic classifier you have crisp metrics (Chapter 5) — the answer is right or wrong. LLM output is open-ended: there are *many* good answers to "summarize this article," and "quality" includes correctness, relevance, tone, format, and safety all at once. You can't just compute accuracy.

> 💡 **Concept notes — why "is it good?" is hard for LLMs**
> LLM outputs are **open-ended and subjective** — no single correct string to compare against. Worse, they're **non-deterministic** (Chapter 9): the same input can yield different outputs, so a single test pass proves little. And failures are often *subtle* — a confident, fluent, well-formatted answer that happens to be factually wrong looks fine until someone checks. So evaluation can't be an afterthought or a vibe check; it needs to be systematic, repeatable, and run on many cases.

---

## How to actually evaluate

There's a ladder of techniques, from cheap-and-narrow to expensive-and-rich. Good systems use several.

> 💡 **Concept notes — the evaluation toolkit**
> - **A test/eval set:** a curated collection of representative inputs with known-good expected outputs (or acceptance criteria). This is the foundation — your prompt "unit tests" from Chapter 10, grown up. Run it after *every* change to catch **regressions**.
> - **Code-based / rule checks:** cheap, deterministic checks for objective properties — is it valid JSON? Right length? Contains required fields? No banned words? Use these wherever the criterion is mechanical.
> - **LLM-as-judge:** use a (often stronger) LLM to *grade* your system's outputs against a rubric — "Does this answer correctly address the question using only the provided context? Score 1–5." Scales far better than human review and correlates surprisingly well, though it has biases (e.g., favoring longer answers) and isn't infallible. A workhorse of modern LLM evaluation.
> - **Human evaluation:** people rate outputs. The gold standard for nuanced quality, but slow and expensive — so you reserve it for a sample and for calibrating your automated judges.
> - **Production monitoring & user signals:** thumbs up/down, did the user retry or rephrase, did they escalate to a human? Real usage surfaces failures your test set missed — feed those back into the eval set.
> The pattern: **automate what you can (rules + LLM-judge), sample with humans, and monitor production** — then loop the failures back in.

> 💡 **Concept notes — task-specific metrics**
> Tie metrics to the job: for **RAG** (Ch 11), measure *retrieval* quality (did we fetch the right chunks?) **separately** from *answer* quality (faithfulness to the retrieved context, aka "is it grounded or did it stray?") — because, as Chapter 11 warned, most RAG failures are retrieval failures, and lumping them together hides where the problem is. For **classification/extraction** tasks, the Chapter 5 metrics (precision/recall) apply. For **agents** (Ch 12), measure task completion rate and steps taken. Match the measurement to what the system is supposed to do.

---

## The eval-first development loop

The senior workflow inverts the beginner's. Beginners tweak the prompt and eyeball one output. Builders build the eval *first*, then change things and *measure*.

> 💡 **Concept notes — why eval-first**
> Without evals you're flying blind: you change a prompt, one example looks better, you ship — and you've silently broken five other cases (Chapter 10's regression problem at scale). With an eval set, every change produces a *number* you can compare, so improvement becomes engineering rather than guesswork. The loop: **define what "good" means → build an eval set → measure the current system → change one thing → re-measure → keep it only if the number improved.** "How would you evaluate this?" is one of the most revealing AI interview questions, and "I'd build an eval set and measure before/after each change" is the answer that signals real experience.

---

## Keeping it safe: the production responsibilities

Beyond "is it correct," a shipped LLM system has safety obligations. The big ones:

> 💡 **Concept notes — hallucination, in production**
> You can't eliminate hallucination (Chapter 9), so you *manage* it: **ground** answers in retrieved sources (RAG, Ch 11), instruct the model to **say "I don't know"** rather than guess, show **citations** so users can verify, and **measure faithfulness** in your evals. For high-stakes domains (medical, legal, financial), keep a **human in the loop** and never let raw model output be the final authority. The goal is a system that's *honest about its uncertainty*, not one that's impossibly always-right.

> 💡 **Concept notes — guardrails**
> **Guardrails** are checks around the model that catch bad inputs and outputs:
> - **Input guardrails:** filter or flag malicious/off-topic/abusive requests and **prompt-injection** attempts (Ch 10) before they reach the model.
> - **Output guardrails:** scan responses before they reach the user — block toxic content, leaked secrets or PII, off-brand or out-of-scope answers, invalid formats. Often a mix of rules and a classifier/moderation model.
> - **Scope enforcement:** keep the assistant on its job ("I can only help with Acme product questions") so it can't be talked into giving medical or legal advice.
> Guardrails wrap the model in a layer you *do* control around a component you *don't* fully control.

> 💡 **Concept notes — bias, privacy, and responsible use**
> LLMs learned from human text and carry its **biases** (Chapter 2's "the model mirrors its data," at internet scale) — test for unfair behavior across groups. Respect **privacy**: don't send sensitive user data to third-party APIs without care, and be mindful of what's logged. Be transparent that users are talking to AI. These responsible-AI concerns are increasingly part of both the job and the interview; showing you think about *harm*, not just *accuracy*, is a maturity signal.

---

## Checkpoint — end of the applied build (Ch 9–14 core)

You can now reason about a real LLM product end to end:
- **Ch 9:** what the model truly does (predict tokens) and its built-in limits.
- **Ch 10:** prompting as tested, structured engineering — and prompt injection.
- **Ch 11:** RAG to ground answers in your data.
- **Ch 12:** tools and agents to let it act — under guardrails.
- **Ch 13:** evals to measure quality, and safety layers to contain it.
One piece remains before the interview chapter: actually *shipping* this — latency, cost, and operations.

---

## Try it

1. Why can't you evaluate a summarization feature with simple "accuracy" the way you'd evaluate a spam classifier? Name two complications.
2. What is "LLM-as-judge," when would you use it over human eval, and what's one of its weaknesses?
3. For a RAG system, why do you evaluate retrieval quality *separately* from answer quality? What does each tell you?
4. Describe the eval-first development loop. Why is changing a prompt *without* an eval set risky?
5. Distinguish input guardrails from output guardrails, and give one concrete example of each.
6. You can't eliminate hallucination. List three things you'd do to manage it in a production assistant.


---

## The bumper sticker

> *You can't improve or trust what you don't measure — so build the eval set first, then change things and watch the number. Wrap the model you don't control in guardrails you do, ground answers to fight hallucination, and treat safety as a feature, not an afterthought.*

Next: the last applied chapter — actually shipping AI features, where latency, cost, and operations decide whether your clever system survives contact with production.

---

<div align="right">

[Chapter 14 →](aiml-chapter-14.md)

</div>
