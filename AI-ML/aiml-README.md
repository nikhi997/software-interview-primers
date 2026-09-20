# AI/ML Primer — Reading order and study contract

A 18-chapter primer on the AI and machine learning every software engineer now needs — written in the conversational style of the LLD, HLD, DSA, and Behavioural primers in this collection. Built around a single principle: *feel the data before reaching for the model.*

This is the future-proofing track. The other four prepare you for the interview loop as it has been for a decade. This one prepares you for where the loop — and the job — is *going*: a world where "can you wire an LLM into a product, ground it in real data, and know when it's lying?" is becoming as standard a question as "reverse a linked list."

## Why this track exists now

Two things happened at once. First, **AI stopped being a specialist niche.** You no longer need a PhD and a GPU cluster to build something real — a few API calls put a frontier model in your app this afternoon. That collapsed the barrier, and the industry noticed: "AI Engineer" went from a rare title to one of the fastest-growing roles, and ordinary backend/full-stack postings now list "experience integrating LLMs" as a plain requirement.

Second, **the interview adapted.** Even non-AI roles increasingly probe whether you understand embeddings, RAG, hallucination, and the cost/latency tradeoffs of shipping AI features. Not because every job is an ML job, but because *every* product is sprouting AI features and teams need engineers who won't treat the model as magic.

This primer makes you that engineer: fluent in the fundamentals so you're not faking it, and fluent in the applied GenAI layer so you can actually build.

## The one idea

Every AI course starts with math — gradients, matrices, loss surfaces — and most engineers bounce off it, concluding ML is "not for them." Then they swing to the opposite error: they treat an LLM API as a magic oracle, paste in a prompt, and are baffled when it hallucinates or costs a fortune.

We avoid both traps with one reframe: **machine learning is just learning a function from data instead of writing it by hand.** That's the whole concept. When the rules are too messy to code by hand (what makes an email spam? is this review positive?), you show a model thousands of examples and it *learns* the rule. Everything else — neural nets, transformers, LLMs — is that same idea, scaled up and made more powerful.

And because the model is *learned from data*, the data is the real lever. A mediocre model on great data beats a great model on garbage data, every time. So before you reach for a fancier model, you look at the data — its quality, its leaks, what it actually represents. *Feel the data before reaching for the model.* That instinct is what separates engineers who ship working AI from those who ship confident nonsense.

## How AI/ML interviews are actually scored

Whether it's a dedicated ML round or AI questions sprinkled into a normal loop, interviewers are checking whether you can:

1. **Frame a problem as ML — or correctly decide it isn't one.** Knowing when *not* to use ML is a senior signal.
2. **Reason about data** — splits, leakage, what the features represent, why the metric matches the business goal.
3. **Explain the core machinery** without hand-waving — what training does, what an embedding is, why transformers won.
4. **Apply the GenAI layer** — prompt, RAG, agents, and the failure modes of each.
5. **Think about production** — latency, cost, evaluation, hallucination, and the fine-tune-vs-RAG-vs-prompt decision.

This book builds all five, fundamentals first so the applied layer rests on something solid.

## Reading order

Read in sequence. Each chapter assumes the previous ones.

**Part 1 — ML fundamentals (the mental model)**
- Chapter 1: Learning a function instead of writing it *(what ML is, and when not to use it)*
- Chapter 2: The data is the model *(features, splits, leakage, the data-first mindset)*
- Chapter 3: How a model actually learns *(loss, gradient descent, overfitting, bias–variance)*
- Chapter 4: The classic toolbox *(regression, trees, kNN — and which to reach for)*
- Chapter 5: Knowing if it actually works *(evaluation, the metric that matches the goal)*

**Part 2 — Deep learning and representations**
- Chapter 6: Neural networks from the perceptron up *(layers, activations, backprop intuition)*
- Chapter 7: Everything becomes a vector *(embeddings — the most important idea in modern AI)*
- Chapter 8: The architecture that ate the field *(CNNs/RNNs briefly, then Transformers and attention)*

**Part 3 — The GenAI / LLM applied layer**
- Chapter 9: What an LLM is really doing *(tokens, next-token prediction, pretraining → fine-tuning → RLHF, reasoning models)*
- Chapter 10: Prompting as engineering *(zero/few-shot, system prompts, structured output, failure modes)*
- Chapter 11: Giving the model your data *(RAG, embeddings, vector databases, chunking, grounding)*
- Chapter 12: Letting the model act *(agents, tool/function calling, the ReAct loop, reliability)*
- Chapter 13: Knowing it works, keeping it safe *(evals, hallucination, guardrails — the eval-first discipline)*
- Chapter 14: Shipping AI features *(latency, cost, caching, fine-tune vs RAG vs prompt, LLMOps)*
- Chapter 15: Attacking your own LLM *(prompt injection, jailbreaks, red-teaming, defense in depth)*
- Chapter 16: When every token has a price tag *(cost estimation, right-sizing, routing, caching)*
- Chapter 17: Beyond text — multimodal models *(shared embeddings/CLIP, vision-language models, ASR/speech, image generation)*

**Part 4 — Interview and future-proofing**
- Chapter 18: The AI/ML interview ritual + the roles map *(how it's asked, and how to stay future-proof)*

**Appendix:** Glossary of every term, the roles map (AI Engineer vs ML Engineer vs Data Scientist vs MLOps vs Research), the tools landscape, a project list to build proof, and an interview question bank.

**[Rebuild labs](aiml-rebuild-labs.md):** an 18-lab active workbook, one lab per chapter, all built around a single running scenario. Use it *during* Session 2 of each chapter, not after the book.

**[Model to Product](aiml-model-to-product.md):** all 18 chapters retold as one continuous product build — the same customer-support copilot, evolving decision by decision from a rules engine to a fully guarded, evaluated, multimodal system. Read it *after* Chapter 18, when you're ready to see the whole shape at once.

## Runnable code

Three dependency-free Python snippets (no numpy, no API keys) that make the load-bearing ideas concrete. Run each with `python3`:

- [code/gradient_descent.py](code/gradient_descent.py) — Chapter 3. Fits a line by gradient descent from scratch: predict, measure loss, step downhill, repeat. Watch the loss fall and `w`, `b` converge to the true values.
- [code/embeddings_similarity.py](code/embeddings_similarity.py) — Chapter 7. Cosine similarity over toy "embeddings": `dog` lands near `puppy`, far from `car`. The exact math a semantic-search engine uses.
- [code/rag_retrieval.py](code/rag_retrieval.py) — Chapter 11. The retrieval half of a RAG pipeline: embed the question, fetch the nearest doc chunks, build a grounded prompt — and watch an out-of-scope question score near zero so the model can say "I don't know."

These three are **concept demos** — each one isolates a single idea so you can watch it happen in twenty lines. They are not the same thing as the labs below, which build a whole system.

## Companions

Two more documents sit alongside the eighteen chapters and the appendix. They're not chapters — nothing in the reading order depends on them — but they're where the book stops being something you read and starts being something you've built.

- **[Rebuild labs](aiml-rebuild-labs.md)** is the Session 2 workbook. Where a chapter's own "Try it" section asks you to explain an idea, each lab asks you to build a small, runnable piece of it — with an observable acceptance criterion, not a worksheet answer — and to deliberately reproduce the chapter's failure mode before fixing it. Open the matching lab right after you finish a chapter's Session 1 read; work through it in Session 2 instead of (or alongside) the chapter's own hands-on prompt. Every lab is provider-neutral and fixture-first: nothing requires an API key or a paid model to pass, though each one names an optional real-model extension for when you want to go further.
- **[Model to Product](aiml-model-to-product.md)** is the synthesis pass. It's one fictional company's support copilot, traced from Chapter 1's first rules-vs-learned decision all the way to Chapter 18's finished, defensible architecture — with every move justified by a failure, evidence, and a gate to proceed, the same way a real team would have to justify it to a skeptical lead. Read it *after* Chapter 18, once the whole book is behind you, so you can see the eighteen separate ideas as one continuous set of engineering decisions instead of eighteen separate topics.

None of this replaces the appendix's **Build these** project list (Section D) — those are longer, standalone portfolio projects meant to prove your skills to an interviewer over days or weeks. The labs are shorter, scoped to one chapter each, and meant to be done *while* you're reading the book, not after it.

## Prerequisites

- Comfort writing basic Python (the DSA primer's level is plenty).
- High-school math: you should be okay with the *idea* of a function, a slope, and an average. We build every other concept — vectors, gradients, probabilities — from scratch and keep the math to intuition, not proofs.
- **No prior ML knowledge.** That's the whole point.

## Study contract — do not skip

AI/ML rewards *building* over reading even more than DSA does. Each chapter is **3 sessions, NOT one sitting:**

**Session 1 (45–60 min):** Read the chapter once. Run any code block. Do the inline "try it" prompts. Don't take notes — just absorb the mental model.

**Session 2 (45–60 min, next day):** Rebuild the idea from memory in your own words, *and* do the chapter's hands-on bit — for the fundamentals chapters that's running/modifying the code; for the GenAI chapters, the core labs stay fixture-first so you can test schemas, retrieval, retries, permissions, and cost without an API key. When the lab asks about prompt quality, few-shot gains, abstention, or model resistance to attack, use the optional real/local-model extension if you have access; fixtures cannot prove those behaviors. Reading about hallucination teaches you nothing; *causing* one with a real or local model teaches you everything.

**Session 3 (30 min, day after):** Explain the chapter to yourself in 5 sentences — what problem it solves, the core mechanism, the main failure mode, when to use it, how it connects to the next chapter.

≈2.5 hours per chapter. The GenAI half especially: you must *build*, not just read. The appendix's project list is where the learning sets.

## Checkpoints

- **After Ch5:** Given a business problem, can you decide if it's an ML problem, name the data you'd need, the model class you'd start with, and the metric you'd judge it by — *and* explain why ML might be the wrong tool?
- **After Ch8:** Can you explain, with no hand-waving, what an embedding is and why the Transformer architecture made modern LLMs possible?
- **After Ch14:** Given "add an AI feature to our product," can you sketch the whole thing — prompt vs RAG vs fine-tune, the data flow, how you'd evaluate it, and the cost/latency tradeoffs?
- **After Ch16:** Can you red-team that same feature — name its top attack (especially indirect injection through retrieval) and the defenses — *and* estimate its cost and the levers you'd pull to cut it?
- **After Ch17:** Can you handle a mixed AI/ML interview — a fundamentals question *and* a "design an LLM-powered feature" question — talking clearly throughout?

If a checkpoint fails, **stop and redo** the prior chapters and build something with them. Don't proceed.

## A note on honesty and pace

This field moves fast — specific model names, prices, and tools change every few months. So this primer deliberately teaches the **durable** layer: the concepts and tradeoffs that have held since the transformer arrived and will outlast whichever model is on top this quarter. Where something is fast-moving (model names, exact context limits), the book says so and teaches you the *shape* of the thing, not a number to memorize. Future-proofing isn't knowing today's leaderboard — it's understanding the machinery well enough that a new model is just a faster version of something you already grasp.

## The bumper sticker

> *Machine learning is learning a function from data instead of writing it by hand — so the data, not the model, is the real lever. Feel the data before reaching for the model, and an LLM stops being magic and becomes a component you can engineer.*

---

<div align="right">

[Chapter 1 →](aiml-chapter-1.md)

</div>
