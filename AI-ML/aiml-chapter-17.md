# Chapter 17: Beyond text — multimodal models

*[← Chapter 16](aiml-chapter-16.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

For sixteen chapters we've talked as if AI means *text in, text out.* But the models your product actually reaches for increasingly take a picture, a sound clip, or a video — and hand one back. If you work anywhere near media, you're already living this: a model that picks the best **thumbnail** is doing vision, one that writes **closed captions** is doing speech recognition, and one that **translates** an episode's subtitles is doing sequence-to-sequence over text. The good news is that almost nothing you've learned is wasted. The two ideas that powered LLMs — *everything becomes a vector* (Chapter 7) and *attention scales* (Chapter 8) — are exactly what make multimodal models work. This chapter shows how, and how to reason about the AI features that don't fit in a chat box. The through-line: **a picture, a sound, and a sentence are all just vectors — the machinery didn't change, only the shape of what you feed it.**

---

## The one idea: put every modality in the same vector space

The move that unlocks all of multimodal AI is one you already have — embeddings (Chapter 7), stretched to cover more than words.

> 💡 **Concept notes — the shared embedding space (CLIP)**
> Train a model on pairs of images and their text captions, and push *both* into the **same** vector space, and something remarkable happens: a photo of a dog and the words "a dog" land near each other. This is what **CLIP**-style models do — a shared space where *meaning* is comparable *across* modalities, not just within one. Once an image and a sentence live in the same geometry, "find the image that matches this caption" (or the reverse) is the *same* nearest-neighbor search you used for semantic text search in Chapter 7. Cross-modal search, zero-shot image classification ("is this vector closer to `cat` or `dog`?"), and matching a **thumbnail** to an episode's description all fall out of one move: **put different modalities in one embedding space and compare with cosine similarity.** The most important idea in modern AI (embeddings) is also the one that makes multimodal possible.

---

## Models that see: vision-language models

Once images are vectors, an LLM can consume them right alongside words.

> 💡 **Concept notes — vision-language models (VLMs)**
> A **vision-language model (VLM)** is an LLM that can *see*: you feed it an image (or several) plus text, and it reasons over both. Under the hood the image is chopped into patches, each turned into a vector (an embedding again), and fed into the transformer alongside the text tokens — **attention (Chapter 8) doesn't care whether a vector came from a word or an image patch.** That's why one architecture generalizes across modalities. VLMs power "describe this image," visual question answering, pulling text out of a screenshot (OCR), and judging whether a **thumbnail** is clear, safe, and on-brand. Crucially, everything you know about LLMs still applies: they're fluent, they **hallucinate** (confidently mis-describing an image is the visual version of Chapter 9), and they need grounding and evaluation before you trust them.

---

## Models that hear: speech in and speech out

Audio becomes computable the same way — turn the waveform into a sequence you can model.

> 💡 **Concept notes — ASR and TTS**
> Two workhorses bridge audio and text. **ASR (automatic speech recognition)** converts speech *to* text — the technology behind **closed captions**, transcripts, and voice commands. **TTS (text-to-speech)** goes the other way, generating natural-sounding audio from text (dubbing, accessibility, voice assistants). Both are sequence models at heart: ASR maps an audio sequence to a token sequence — the *same shape* of problem as **translation** (one sequence in, another out), which is why the Transformer handles it. Practically, ASR is rarely perfect — accents, background noise, and unusual names trip it up — so a serious caption pipeline pairs it with review or correction. That's not a workaround; it's the "never trust the model's raw output" discipline from Chapter 13 applied to a new modality.

---

## Models that create: image and video generation

Generation flips the arrow — a prompt in, a brand-new image or clip out.

> 💡 **Concept notes — diffusion (generating images)**
> A widely used technique for image and video generation is **diffusion**: the model learns to start from pure noise and repeatedly *denoise* it, step by step, toward an image that matches your prompt. It's a different mechanism from next-token prediction, but the mental model is familiar — a model that learned patterns from enormous amounts of data and now produces plausible *new* samples. Uses range from marketing art and **thumbnail** generation to synthetic training data. The usual cautions apply, amplified: cost and latency are higher, output is non-deterministic, and there are real **safety and rights** issues — deepfakes, training-data provenance, likeness and copyright — that you treat as first-class concerns, not afterthoughts.

---

## Building with it: same playbook, new inputs

The reassuring part: shipping a multimodal feature leans on every instinct from Part 3.

> 💡 **Concept notes — multimodal is the same discipline**
> - **Multimodal RAG:** embed images or audio into the shared space (above) and retrieve *across* modalities — "find frames that match this description," "pull the transcript passage for this clip." It's Chapter 11 with richer inputs.
> - **The same production realities (Chapter 14), sharper:** multimodal calls are usually *slower and pricier* — an image is worth many tokens, audio more still — so caching, right-sizing, and treating the model as *just another dependency* matter even more.
> - **The same evaluation discipline (Chapter 13):** you still need a test set and a way to score "is this caption accurate?" or "is this thumbnail appropriate?" — often with a **VLM-as-judge**, the multimodal cousin of LLM-as-judge.
> The takeaway: **multimodal changes the inputs, not the playbook.** If you can ground, cost-manage, and evaluate a text feature, you can do it for a visual or audio one.

---

## Real-time multimodal: the clock becomes part of correctness

Batch transcription can wait for a whole file. A live voice or video assistant cannot: audio frames keep arriving while the model is reasoning, the user may interrupt, and an answer that arrives after the conversation moved on is wrong even if its words are perfect.

You can use a **native multimodal model** that accepts audio/video directly, or an explicit pipeline such as ASR → text model → TTS. Native input can retain cues a transcript loses; a separate pipeline offers inspectable intermediate results and independent components. Neither architecture removes the need to evaluate turn-taking, timing, privacy, and action safety.

> 💡 **Concept notes — streaming, turn-taking, and synchronization**
> A real-time pipeline usually performs streaming input → incremental ASR/vision features → model reasoning → streaming output. Track **time to first useful output** and end-to-end turn latency, not just total processing time. Support **barge-in**: when the user starts speaking, cancel or pause stale generation rather than talking over them. Keep timestamps and provenance so a statement can be tied to the audio span or video frame that caused it; late or out-of-order frames must not update the wrong turn.

> 💡 **Concept notes — partial evidence is unstable**
> Streaming ASR revises earlier words as more audio arrives; a frame can be blurry until the next one; silence detection can end a turn too early. Separate **provisional** state from **committed** state. Do not trigger a side effect from a partial transcript. Buffer enough context to make the decision reliable, define a commit condition, and keep a human approval gate for high-impact actions. Handle disconnects, jitter, and backpressure explicitly, and disclose/obtain consent appropriate to recording and retention.

Evaluation now needs scripted conversations with overlap, interruptions, noise, accents, delayed frames, and reconnects. Score transcript/vision quality, turn detection, cancellation correctness, latency percentiles, and whether any action used provisional evidence.

---

## Try it

1. Your team wants to auto-pick the best **thumbnail** for each episode from a set of candidate frames. Sketch how a shared image–text embedding space (CLIP-style) turns this into a search problem.
2. A VLM confidently describes a person in a photo who isn't there. Which Chapter 9 concept is this, and how would you catch it before it ships?
3. Your closed-caption pipeline uses ASR but keeps getting character names wrong. Why does this happen, and what would you add rather than assuming the model is "good enough"?
4. Explain diffusion in one or two sentences to a non-technical PM. Why is "start from noise and denoise" a reasonable way to make an image?
5. Why are multimodal calls usually more expensive and slower than text-only ones, and which Chapter 14 techniques still apply?
6. You're asked, "How would you evaluate an AI thumbnail-selection feature?" Answer it using the eval discipline from Chapter 13 — what's your test set, and what's your judge?
7. A voice assistant starts answering, but the user interrupts to correct an account number. What must the runtime cancel, what state is provisional, and what evidence can be committed?


---

## The bumper sticker

> *Multimodal AI isn't a new field to learn — it's the ideas you already have, generalized: everything (a pixel patch, an audio frame, a word) becomes a vector, attention chews on those vectors regardless of where they came from, and the same grounding, cost, and evaluation discipline still decides whether it works. A picture, a sound, and a sentence are all just vectors; the machinery didn't change, only the shape of what you feed it.*

Next: everything comes together — first the AI/ML interview ritual, then the context and workflow discipline that keeps a long-running AI system coherent.

---

<div align="right">

[Chapter 18 →](aiml-chapter-18.md)

</div>
