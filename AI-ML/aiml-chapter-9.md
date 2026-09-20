# Chapter 9: What an LLM is really doing

*[← Chapter 8](aiml-chapter-8.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

Welcome to Part 3. Everything before this was foundation; now we build. And we start by dissolving the magic, because you cannot engineer something you think is magic. An LLM feels like it understands you, reasons, and knows things. Under the hood it is doing something almost comically simple, over and over: **predicting the next word.** Once you internalize that, every strength *and* every failure of these models — fluency, hallucination, the context window, the need for good prompts — follows logically. This is the most important chapter for using LLMs well.

> A senior reminder before we start: model names, sizes, and prices change every few months. This chapter teaches the *mechanics*, which don't. Treat specific model capabilities as fast-moving; treat "it predicts the next token" as permanent.

---

## The whole trick: next-token prediction

An LLM is trained on one task: given a stretch of text, predict what comes next. "The capital of France is ___" → "Paris." "def add(a, b): return ___" → "a + b." Do this across essentially all the text humans have written, with a giant Transformer (Chapter 8), and to get good at *predicting* the next word the model is forced to *learn* grammar, facts, reasoning patterns, code, and style — because all of those help it predict better. Understanding emerges as a *side effect* of relentless prediction.

> 💡 **Concept notes — autoregressive generation**
> When an LLM "writes," it generates **one token at a time**: predict the next token, append it, feed the whole thing back in, predict the next, and so on. This is called **autoregressive** generation. It's not planning a whole sentence and typing it out — it's choosing the next token, repeatedly, each choice conditioned on everything so far. This single fact explains a *lot*: why output streams word by word, why it can lose track over long generations, and why the very first tokens it commits to can steer everything after.

> 💡 **Concept notes — tokens (not words)**
> The **token** is the LLM's atomic unit — what a bit is to computing. The model doesn't see words or letters; it reads and writes *tokens*, chunks of text that are often a word or a piece of one ("unbelievable" might be "un," "believ," "able"). Every mechanism in this chapter — next-token prediction, the context window, autoregressive generation — is literally defined over tokens, not words. That's the primary point: tokens are the level of reality the model operates at. Two practical consequences fall out of it: you're **billed per token** (input + output), and the **context window** (below) is measured in tokens — so when you estimate cost or whether something fits, you count tokens, not words. Rough rule of thumb: 1 token ≈ ¾ of a word in English. (Operating on tokens is also why models historically stumbled on "how many r's in strawberry" — they see tokens, not letters.)

---

## Why it's not a database (and why it hallucinates)

This is the single most important practical consequence, so it gets its own section. An LLM does **not** store facts in a lookup table. It stores *statistical patterns* about what text tends to follow what. So when it answers, it is generating *plausible-sounding text*, not retrieving a verified fact. Usually plausible and true coincide. Sometimes they don't — and the model states a falsehood with the exact same confidence as a truth, because it has no internal sense of "I know this" vs "this just sounds right."

> 💡 **Concept notes — hallucination**
> A **hallucination** is when an LLM produces fluent, confident, plausible text that is simply **false** — a made-up citation, a non-existent API method, a wrong date. It's not a bug to be fully patched; it's a *direct consequence* of how the model works. It predicts likely text, and a fake but plausible reference is "likely text." The model has **no built-in notion of truth** and (by default) **no access to a source of truth.** This is *the* central challenge of building with LLMs, and it's why Chapters 11 (give it real data) and 13 (evaluate and guard) exist. The mature builder's mantra: **never trust an LLM's factual claims by default — ground them or verify them.**

---

## The three stages that make a ChatGPT

A raw "predict the next word" model is a strange beast — it'll happily continue your text but won't follow instructions or behave. Turning it into a helpful assistant takes three stages, and knowing them demystifies the whole thing:

> 💡 **Concept notes — pretraining, fine-tuning, RLHF**
> 1. **Pretraining:** train the giant Transformer on a massive pile of internet text via next-token prediction. This is where it learns language, facts, and reasoning. Enormously expensive (the part that costs millions). Result: a **base model** — knowledgeable but unruly, just a text-continuer.
> 2. **Fine-tuning (instruction tuning):** continue training on curated examples of *instructions and good responses*, teaching the model to *follow directions* and answer rather than just continue. Much cheaper than pretraining.
> 3. **RLHF (Reinforcement Learning from Human Feedback):** humans rank competing responses; the model is tuned to produce the kind humans prefer — helpful, harmless, honest-sounding. This is the polish that makes it pleasant and aligned (and is *why* it sometimes refuses or hedges). This is the reinforcement learning flavor from Chapter 1, showing up exactly where promised.
> "Pretrain to know, fine-tune to follow, RLHF to behave" is a clean three-line summary that signals you understand the pipeline.

---

## The context window: the model's working memory

An LLM has no memory between calls. Everything it "knows" about *your* conversation must be fed in as text each time. The amount it can consider at once — your prompt, the conversation history, any documents you paste — is the **context window**, and it's finite.

> 💡 **Concept notes — the context window**
> The **context window** is the maximum amount of text (in tokens) the model can attend to at once — its working memory for a single call. Everything outside it effectively doesn't exist to the model. Implications: (1) **the model is stateless** — "memory" in a chat app is an illusion created by resending the history each turn; (2) long documents may not fit, forcing you to **chunk** and retrieve the relevant parts (RAG, Chapter 11); (3) more context costs more tokens (money and latency) and, past a point, models attend *less* reliably to the middle of very long contexts. Windows have grown large, but "what's in the context is all the model knows right now" is a permanent design constraint you build around.

> 💡 **Concept notes — knowledge cutoff & no live world**
> A base model only knows what was in its training data, which stopped at some **knowledge cutoff** date. It doesn't know today's news, your private documents, or what happened after training — unless you *give* it that information in the context (via tools or retrieval). "It can't know what it wasn't trained on and isn't told" is the framing that makes RAG (Ch 11) and tools (Ch 12) feel obviously necessary rather than fancy.

---

## Controlling the output: temperature

One knob you'll touch constantly. Since the model produces a *probability* for each possible next token, how do you pick? Always the single most likely token (deterministic, repetitive), or sample with some randomness (varied, creative)? That's **temperature.**

> 💡 **Concept notes — temperature**
> **Temperature** controls randomness in token selection. **Low (≈0):** the model almost always picks the most likely token — focused, consistent, repeatable. Use it for factual answers, extraction, code, anything where you want reliability. **High (≈0.8–1+):** more randomness — varied, creative, but also more prone to going off the rails. Use it for brainstorming or creative writing. A common mistake is using high temperature for a task that needs precision and then being surprised by inconsistency. **Match temperature to the task.**

---

## Reasoning models: spending compute to think

Everything above describes a model that answers in one pass — it starts emitting the answer immediately. But the hardest problems (multi-step math, tricky logic, real debugging) reward *working it out* before answering. A newer class of models is trained to do exactly that, and it has changed the cost calculus enough that you need to know it exists.

> 💡 **Concept notes — reasoning models / test-time compute**
> A **reasoning model** is trained (often with reinforcement learning) to generate a long internal chain of thought — "thinking" tokens — *before* it commits to a final answer. It's the chain-of-thought trick from Chapter 10, baked into the model instead of coaxed by your prompt. The key idea is **test-time compute**: rather than spending more only at *training* time (a bigger model), you let the model spend more at *answer* time (think longer), and that extra thinking buys measurably better results on genuinely hard reasoning, math, and coding. This is a new scaling axis. The tradeoffs are the whole point: it's **slower and pricier per answer** — you pay for those hidden thinking tokens too — so it's overkill for simple extraction, classification, or formatting, where a standard model is faster and cheaper. Two practical consequences: (1) a "thinking budget" becomes a knob you match to task difficulty, just like model size (Chapter 14); (2) these models often need **less** prompting, not more — don't tell a reasoning model to "think step by step" (it already does) and go easy on few-shot examples, which can even hurt. Reach for a reasoning model when the task is *hard reasoning*; use a standard model when it's *not*.

---

## Try it

1. Explain in one sentence why an LLM hallucinates, using the phrase "next token." Why is it not simply a fixable bug?
2. Your app needs the model to extract a date from an email and return it in a fixed format. What temperature do you use, and why?
3. A user is upset that ChatGPT "forgot" what they said five messages ago. Explain what's actually happening with the context window and statelessness.
4. Why does asking an LLM about an event from last week often fail or produce a confident wrong answer? What would you need to add to fix it?
5. Put "pretraining," "fine-tuning," and "RLHF" in order and give each a three-word job description.
6. Roughly how many tokens is a 1,000-word document, and why do you care (name two reasons)?
7. When would you reach for a reasoning model instead of a standard one — and what two costs do you accept in return?


---

## The bumper sticker

> *An LLM just predicts the next token from learned patterns — so it's fluent but has no built-in truth, no memory between calls, and no knowledge it wasn't trained on or told. Every technique ahead (prompting, RAG, tools, evals) exists to manage exactly those limits.*

Next: the first lever you have over an LLM's behavior — prompting, treated as engineering rather than guesswork.

---

<div align="right">

[Chapter 10 →](aiml-chapter-10.md)

</div>
