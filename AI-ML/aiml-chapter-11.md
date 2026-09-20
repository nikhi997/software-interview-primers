# Chapter 11: Giving the model your data

*[← Chapter 10](aiml-chapter-10.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

Two limits from Chapter 9 block most real LLM products: the model **doesn't know your private/internal data**, and it **hallucinates** when it doesn't know something. Fine-tuning a model on your data is expensive, slow to update, and *still* doesn't guarantee truthfulness. There's a far better, cheaper, and now-standard answer: **don't bake the knowledge into the model — fetch the relevant facts at question time and put them in the prompt.** That technique is **RAG (Retrieval-Augmented Generation)**, and it's probably the single most important architecture in applied GenAI today. If you build one AI feature in your career, it's likely a RAG system.

---

## The idea: open-book instead of closed-book

A plain LLM answering from memory is taking a *closed-book* exam — it recalls what it can and bluffs the rest (hallucination). RAG turns it into an *open-book* exam: when a question comes in, you first **retrieve** the relevant passages from *your* documents, hand them to the model along with the question, and say "answer using *this*." The model's job shifts from "recall the fact" (which it can't reliably do) to "read these passages and synthesize an answer" (which it's excellent at).

> 💡 **Concept notes — RAG (Retrieval-Augmented Generation)**
> **RAG** = retrieve relevant context, then generate an answer grounded in it. The name spells out the flow: **Retrieval** — find the passages from your knowledge base most relevant to the user's question (using embeddings and vector search from Chapter 7); **Augmented** — inject those passages into the prompt, augmenting the model's context with facts it wasn't trained on; **Generation** — ask the LLM to answer *based on them.* The win: the model now answers from *current, private, trustworthy* data you control, dramatically reducing hallucination, and you can **update the knowledge by changing documents — no retraining.** This is why RAG beats fine-tuning for most "answer questions about our stuff" problems.

---

## How RAG actually works, end to end

It's the embeddings machinery from Chapter 7, applied. Two stages — one offline, one at query time.

**Offline (indexing), done once and updated as documents change:**

> 💡 **Concept notes — chunking and indexing**
> 1. **Chunk** your documents into passages — a whole 50-page manual won't fit the context window and retrieving it would be wasteful, so split it into pieces (paragraphs, sections). **Chunking** — choosing how to split — matters a lot: too big and you retrieve irrelevant filler and blow your token budget; too small and you sever the context that makes a passage meaningful. Sensible chunks with a little overlap are a real tuning knob.
> 2. **Embed** each chunk into a vector (Chapter 7).
> 3. **Store** the vectors in a **vector database** (Chapter 7) alongside the original text.

**At query time, every request:**

> 💡 **Concept notes — retrieve, augment, generate**
> 1. **Embed the user's question** into a vector.
> 2. **Retrieve** the top-k most similar chunks via vector search (cosine similarity / nearest-neighbor — Chapter 7). These are your "open book" pages.
> 3. **Augment** the prompt: combine the retrieved chunks + the question into a prompt like *"Using only the context below, answer the question. If the answer isn't in the context, say you don't know.\n\nContext: {chunks}\n\nQuestion: {question}".*
> 4. **Generate:** the LLM answers, grounded in the retrieved text. Bonus: you can show **citations** (which chunks it used), which builds user trust and lets them verify.
> That four-step query path — embed, retrieve, augment, generate — is worth memorizing cold. It's the backbone of nearly every "chat with your docs / knowledge assistant" product.

---

## Grounding: the whole point

The phrase you'll hear constantly is **grounding** — tying the model's answer to real, retrieved evidence rather than its fuzzy memory.

> 💡 **Concept notes — grounding and "say I don't know"**
> **Grounding** means the answer is based on provided source material you can point to. A well-built RAG prompt explicitly instructs: *"Answer only from the context; if it's not there, say you don't know."* This single instruction, plus actually-relevant retrieved context, is what turns a confident bluffer into a trustworthy assistant. Grounding doesn't *eliminate* hallucination (the model can still misread or over-reach), but it's the most effective lever you have, and it makes answers **verifiable** via citations. "Ground it and cite it" is the mature default for any factual LLM feature.

---

## RAG vs fine-tuning: a question you'll be asked

This comparison is a near-guaranteed interview question, and the instinct matters in real design.

> 💡 **Concept notes — when to RAG, when to fine-tune**
> - **RAG** is for giving the model **knowledge** — facts, documents, data that changes. Cheap to update (edit documents), reduces hallucination, supports citations, no training needed. *Use it for: "answer questions about our policies/docs/data," anything where information changes or must be current and verifiable.* This is the **default** for knowledge problems.
> - **Fine-tuning** is for teaching the model a **behavior, style, or format** — talk in our brand voice, always output this exact structure, handle a narrow task in a consistent way. It bakes in *how to act*, not *what's true.* Expensive, slow to update, and it does **not** reliably add factual knowledge or stop hallucination.
> Crisp rule: **RAG for knowledge, fine-tuning for behavior** — and they combine (fine-tune the style, RAG the facts). The classic wrong answer is "fine-tune the model on our docs so it knows them." Knowing why that's usually the *worse* choice than RAG is a strong signal.

---

## Why RAG is often harder than it looks

Don't oversell it in an interview — show you know the failure modes:

> 💡 **Concept notes — RAG's failure modes**
> RAG is only as good as its **retrieval.** If the right chunk isn't retrieved, the model can't use it — and it may then hallucinate anyway or say "I don't know" when the answer *was* in your corpus. Common problems: bad **chunking** (split mid-thought), the question and the relevant passage not being semantically close (so pure embedding search misses it — often fixed with **hybrid search**, combining keyword + semantic, Chapter 7), retrieving too much irrelevant context that drowns the signal, and stale or duplicated documents. "The hard part of RAG is retrieval quality, not the LLM" is the practitioner's truth. Most RAG improvement work is *retrieval* work.

---

## Improving retrieval: BM25, hybrid + RRF, and reranking

The failure-modes note ends on the practitioner's truth — *most RAG improvement work is retrieval work.* So what does that work actually look like? Three techniques do most of the heavy lifting, and naming them is what separates "I'd add RAG" from "I'd build retrieval that works." This is the single most common follow-up to a RAG design question: **"the right chunk isn't being retrieved — how do you fix it?"**

> 💡 **Concept notes — BM25, the keyword workhorse**
> Pure embedding (semantic) search has one real weakness: it can miss on **exact terms** — a product code like `X-450`, a rare surname, an error string like `ECONNREFUSED`, a specific acronym. Two strings can mean different things yet sit close in embedding space, and an unusual token may not be well-represented at all. **BM25** is the classic keyword-ranking algorithm that fixes this. Intuition: a document ranks higher when the query's words appear in it **often** (term frequency), those words are **rare across the whole corpus** (inverse document frequency — matching "ECONNREFUSED" tells you far more than matching "the"), and the match isn't just an artifact of a very long document (**length normalization**). It's the "keyword search" half of Chapter 7's hybrid search, named. It needs no model and no GPU, and it's unbeatable at exact-term recall — which is exactly where embeddings stumble.

> 💡 **Concept notes — hybrid search and Reciprocal Rank Fusion (RRF)**
> Semantic search nails *meaning*; BM25 nails *exact terms.* **Hybrid search** runs both and merges the results so you get the strengths of each. The catch: the two produce *incomparable* scores — a cosine similarity of `0.82` and a BM25 score of `14.3` live on different scales, so you can't just add them. **Reciprocal Rank Fusion (RRF)** sidesteps this by ignoring the raw scores and using only each document's **rank** in each list: a document's fused score is the sum of `1 / (k + rank)` across the lists it appears in (with `k` a small constant like 60). A document that ranks high in *either* list floats up; one that ranks decently in *both* floats highest. Simple, robust, and the default fusion method in most vector databases. "I'd run BM25 and embeddings in parallel and fuse with RRF" is a strong, concrete answer.

> 💡 **Concept notes — reranking with a cross-encoder**
> Retrieval is a two-stage game. Stage one (BM25 + embeddings) is **cheap and approximate** — it scans the whole corpus and hands back the top ~50 candidates, but it scores the query and each document *separately* (a "bi-encoder": embed each independently, compare vectors), so it can't reason about how well they truly fit. Stage two, **reranking**, takes those ~50 and rescores them with a **cross-encoder** — a model that reads the query and a document *together* in one pass and outputs a relevance score. That joint read is far more accurate but far too expensive to run over millions of docs, which is why you only apply it to the shortlist. **Retrieve broad and cheap, then rerank narrow and precise,** and feed only the top few survivors to the LLM. Adding a reranker is one of the highest-ROI upgrades to a struggling RAG system.

> The full modern retrieval stack, then: **BM25 + embeddings → fuse with RRF → rerank the top-k with a cross-encoder → pass the best few to the model.** You won't need every layer on day one — start with embeddings, add BM25 when exact terms get missed, add reranking when precision still isn't enough — but knowing the whole ladder, cheapest rung first, is exactly the judgment a RAG interview is testing.

---

## Try it

1. Explain RAG to a non-technical manager using the "open-book exam" analogy in two sentences.
2. List the four query-time steps of RAG in order.
3. Your company wants an assistant that answers from a constantly-updated internal wiki. Why is RAG a better fit than fine-tuning a model on the wiki?
4. A RAG bot confidently gives a wrong answer that contradicts your docs. Name two likely causes — and note which stage (retrieval vs generation) each is in.
5. Why does chunk size matter? Describe a problem caused by chunks that are too large, and one caused by chunks that are too small.
6. When would you actually fine-tune *instead of* (or in addition to) RAG?
7. A user searches for the exact error code `ECONNREFUSED` and your embedding-only retrieval misses the doc that explains it. Which technique fixes this, and why does it succeed where embeddings failed?
8. You're combining BM25 and embedding results but can't just add their scores. What is RRF, and how does it merge the two lists?
9. What is a cross-encoder reranker, why is it more accurate than the initial retrieval, and why can't you just use it for the whole corpus?


---

## The bumper sticker

> *RAG turns a closed-book bluffer into an open-book assistant: embed the question, retrieve your relevant passages, stuff them in the prompt, and make the model answer from them. RAG for knowledge, fine-tuning for behavior — and the hard part is always retrieval quality.*

Next: letting the model not just *answer* but *act* — calling tools and functions to do things in the world.

---

<div align="right">

[Chapter 12 →](aiml-chapter-12.md)

</div>
