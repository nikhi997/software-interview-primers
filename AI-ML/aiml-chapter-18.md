# Chapter 18: The AI/ML interview ritual and the roles map

*[← Chapter 17](aiml-chapter-17.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

You've built the whole stack of understanding — from "ML learns a function" to "here's how I'd ship and operate a RAG-plus-agent system under guardrails." This final chapter does two jobs. First, it gives you a **ritual** for AI/ML interview questions, the way the other tracks gave you UMPIRE, STAR, and the design frameworks — a repeatable way to turn a vague question into a strong answer. Second, it maps the **new roles** so you can aim your preparation at the job you actually want, and offers a few words on staying future-proof in a field that reinvents itself yearly.

---

## The one ritual: DRESS the problem

AI/ML interview questions ("design a system to answer questions over our docs," "how would you reduce hallucination," "build a feature that summarizes support tickets") reward a structured response that mirrors this whole track. Use **DRESS**:

> 💡 **Concept notes — the DRESS ritual**
> - **D — Data first.** What data exists? Labeled? How much? Quality, bias, leakage? (Ch 2) *Always open here* — it signals the data-first instinct and it's where real projects live. If there's no data, say what you'd collect.
> - **R — Rule out ML (and right-size it).** Does this even need ML/an LLM, or would simpler logic do? If it needs a model, does it need the *biggest* one? (Ch 1, Ch 14) Showing you'd *not* over-engineer is a senior signal.
> - **E — Estimate the approach.** Pick the method and justify it: classic model vs deep learning vs LLM; for LLMs, the prompt→RAG→fine-tune ladder (Ch 14). Name the tradeoffs out loud.
> - **S — Ship it.** Latency, cost, reliability, guardrails, security (prompt injection!), human-in-the-loop for risky actions (Ch 14, 15, 16). This is where most candidates are thin — being strong here sets you apart.
> - **S — Score it.** How do you *know* it works? Pick metrics that match the goal (Ch 5), build an eval set, measure before/after, monitor in production (Ch 13). "How would you evaluate this?" is the question candidates most often fumble — don't.
> **DRESS** = Data, Rule-out, Estimate, Ship, Score. It's just this track's spine turned into five prompts you can walk through out loud.

---

## What AI/ML interviews actually test

Depending on the role, you'll hit some mix of these. Know which your target role emphasizes (the roles map below tells you):

> 💡 **Concept notes — the question families**
> - **Concept checks:** "Explain overfitting / embeddings / attention / RLHF / RAG vs fine-tuning." Direct recall of the fundamentals in this book. Be able to explain each *simply* — explaining clearly is itself the signal.
> - **ML system design:** "Design a recommendation / fraud / search / Q&A-over-docs system." The big one for ML and AI engineers — use DRESS. Cover data, model choice, serving, evaluation, monitoring.
> - **LLM/GenAI applied:** "Build a chatbot over our knowledge base," "reduce hallucination," "make this agent reliable." The fastest-growing family — Chapters 9–17 are your script, including the multimodal twist (vision, speech, image generation) when the product handles more than text.
> - **Coding:** data manipulation, sometimes implementing a simple model or a retrieval/similarity function, increasingly "build a small LLM-powered feature with an API." (Your DSA track covers the algorithmic side.)
> - **Behavioral & judgment:** "Tell me about an ML project," plus responsibility questions — bias, safety, when *not* to use AI. (Your Behavioural track applies directly; the AI twist is showing maturity about *harm*, not just accuracy.)

---

## The roles map: aim at the right target

"AI/ML" is not one job. The titles overlap and shift, but here's the durable shape of the landscape so you can aim your prep:

> 💡 **Concept notes — the five role archetypes**
> - **AI Engineer / GenAI Engineer** *(the fastest-growing, and what much of Part 3 prepares you for)*: builds applications *on top of* existing models — RAG systems, agents, LLM features, prompt pipelines. Strong **software engineering** + applied LLM skills (prompting, RAG, tools, evals, shipping). Usually does **not** train models from scratch. If you're a software engineer adding AI, this is your most natural target.
> - **Machine Learning Engineer (MLE)**: builds and deploys ML *models* in production — training pipelines, feature engineering, serving, scaling, monitoring. Solid software engineering + classic ML depth (Parts 1–2) + MLOps. The bridge between data science and production systems.
> - **Data Scientist**: focuses on extracting insight from data — analysis, experimentation (A/B tests), statistics, and often classic modeling. Heavier on stats and communication, lighter on production engineering. More analysis than shipping.
> - **MLOps / ML Platform Engineer**: builds the *infrastructure* that trains, deploys, monitors, and scales models — pipelines, serving, observability, the LLMOps layer (Ch 14). Heavy software/infra, lighter on modeling itself.
> - **Research Scientist / ML Researcher**: invents new models and methods. Deep math, usually a PhD, publishes papers. Creates the techniques the other roles *use*. The smallest and most specialized slice.
> Two practical truths: (1) the **AI Engineer** path has the lowest barrier for an existing software engineer and the most open roles right now — Part 3 is its core curriculum; (2) the lines blur and titles vary by company, so read the *responsibilities*, not just the title.

---

## Staying future-proof in a field that won't sit still

The honest meta-skill, and the reason this track is built the way it is:

> 💡 **Concept notes — what stays true while everything changes**
> Specific models, prices, tools, and benchmarks churn every few months — chasing them is a treadmill. What *doesn't* change is the conceptual layer you've learned: a model is a function learned from data; the data is the real lever; embeddings turn meaning into geometry; an LLM predicts the next token and so has no built-in truth; RAG grounds it; tools let it act; evals tell you if it works. **Master the durable concepts and you can pick up any new tool in an afternoon, because you understand what it *is*.** Concretely, to stay future-proof: (1) build the concept foundation (this book), (2) **actually build things** — a RAG app, a small agent — because hands-on beats reading, (3) keep a light finger on the pulse (follow a few credible sources) without chasing every release, and (4) lean into the durable engineering skills (system design, evaluation, judgment about *when not* to use AI) that no model release will obsolete.

---

## The final checkpoint — the whole track in one breath

If you can give this answer cold, you're ready:

> *"Machine learning learns a function from data instead of you writing it, so the data — not the model — is the real lever. You train by minimizing loss with gradient descent, balancing overfitting against underfitting, and you start simple. Deep networks learn their own features; embeddings turn meaning into geometry so 'understanding similarity' becomes nearest-neighbor search; and the Transformer's attention scaled that into LLMs. An LLM just predicts the next token, so it's fluent but has no built-in truth or memory — which is why we prompt it carefully, ground it with RAG, let it act through guarded tools, and above all evaluate it. Shipping means trading quality against latency and cost, climbing prompt→RAG→fine-tune cheapest-first, and operating it like the living system it is."*

That's not memorization — it's the through-line you now actually understand. Walk into the room and **feel the data before reaching for the model.**

---

## Try it

1. You're asked: "Design a system that answers customer questions from our help docs." Walk through all five DRESS steps out loud. Where does most of your time go?
2. An interviewer asks, "How would you reduce hallucination in this assistant?" Give a layered answer touching grounding, prompting, and evaluation.
3. You're a backend engineer wanting into AI. Which role archetype is your most realistic first target, and which chapters of this book are its core?
4. "Why not just fine-tune a model on all our documents?" Answer it the way Chapters 11 and 14 taught you.
5. The interviewer ends with "the field moves so fast — how do you keep up?" Give the future-proof answer.
6. Recite the one-breath summary above from memory. Where do you stumble? That's your next study session.


---

## The bumper sticker

> *Every AI/ML interview rewards the same move: DRESS the problem — Data first, Rule out over-engineering, Estimate the approach, Ship it, Score it. Aim at the role whose responsibilities fit you, master the durable concepts over the churning tools, and the field stops being intimidating and becomes yours to build in.*

That's the track. The appendix that follows is your reference shelf — a glossary, the roles map at a glance, a tools landscape, projects to prove your skills, and an interview question bank. Use it to review, and revisit any chapter whose bumper sticker you can't yet say in your own words.

---

<div align="right">

[Appendix →](aiml-appendix.md)

</div>
