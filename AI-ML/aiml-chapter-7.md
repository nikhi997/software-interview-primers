# Chapter 7: Everything becomes a vector

*[← Chapter 6](aiml-chapter-6.md) · [Contents](aiml-README.md)*

- [ ] **Mark as read**

If you remember one idea from this entire track, make it this one. It's the bridge between "classic ML" and "modern AI," it's the engine under semantic search and RAG, and it's why an LLM can seem to *understand* meaning. The idea:

> **Turn anything — a word, a sentence, an image, a user — into a list of numbers (a vector) that captures its meaning, so that "similar in meaning" becomes "close together in space."**

That list of numbers is called an **embedding**, and it is the most important practical concept in this book.

---

## The problem: computers need numbers, but meaning isn't a number

A model can only do math. So how do you feed it the *word* "dog"? The naive answer — assign each word an ID number (dog=5, cat=6, car=7) — is terrible, because the numbers imply relationships that don't exist (is cat the *average* of dog and car?). You need a representation where the numbers actually encode *meaning*. That's what embeddings do.

> 💡 **Concept notes — embedding**
> An **embedding** is a vector (a list of numbers, often hundreds or thousands long) that represents something — a word, sentence, image, product, user — in a way that captures its meaning or properties. The defining feature: **similar things get similar vectors.** "dog" and "puppy" land near each other; "dog" and "democracy" land far apart. The numbers themselves aren't human-readable, but their *geometry* is meaningful — distance and direction encode relationships. Embeddings are *learned* (by neural networks, from data), not assigned by hand.

---

## Meaning becomes geometry

Once things are vectors, you can do *geometry* with meaning. The famous example: take the embedding of "king," subtract "man," add "woman" — and you land almost exactly on "queen." The relationship "male→female" turned out to be a consistent *direction* in the space. Likewise "Paris − France + Italy ≈ Rome." The model was never taught these analogies; they *emerged* because it learned vectors that place words by how they're used.

> 💡 **Concept notes — the embedding space**
> Picture a high-dimensional space where every concept is a point. Regions of the space correspond to themes (animals here, emotions there, programming terms over there). Directions correspond to relationships (gender, tense, capital-of). "Meaning" becomes **location and direction.** This is why we say embeddings let you "do math on meaning" — and it's the foundation of everything that follows.

---

## Measuring similarity: cosine

If similar things are nearby, you need a way to measure "nearby." The standard tool is **cosine similarity** — it measures the *angle* between two vectors, ignoring their length.

> 💡 **Concept notes — cosine similarity**
> **Cosine similarity** scores how aligned two vectors are, from −1 (opposite) through 0 (unrelated) to 1 (identical direction). It looks at the *angle*, not the magnitude, which is what you want for meaning ("dog" and "a big friendly dog" point the same way even if one vector is "longer"). To find what's most similar to a query, you embed the query and find the stored vectors with the highest cosine similarity. This single operation — **embed, then find nearest vectors** — is the heart of semantic search, recommendations, and RAG (Chapter 11).

```python
# Cosine similarity, the whole idea in pure Python:
def dot(a, b):       return sum(x*y for x, y in zip(a, b))
def norm(a):         return sum(x*x for x in a) ** 0.5
def cosine(a, b):    return dot(a, b) / (norm(a) * norm(b) + 1e-9)

dog    = [0.9, 0.1, 0.2]
puppy  = [0.85, 0.15, 0.25]
car    = [0.1, 0.9, 0.8]
print(cosine(dog, puppy))  # high — similar meaning
print(cosine(dog, car))    # low  — unrelated
```

---

## Semantic search: the killer application

Old-fashioned **keyword search** matches *strings*: search "doctor" and you miss documents that say "physician." **Semantic search** matches *meaning*: embed the query and the documents into the same space, and return the documents whose vectors are nearest the query's. Now "physician," "doctor," and "MD" all match because they're close in meaning-space.

> 💡 **Concept notes — semantic vs keyword search**
> **Keyword search** finds exact (or fuzzy) word matches — fast, precise, but blind to meaning and synonyms. **Semantic search** finds *conceptual* matches via embedding similarity — it understands that "how do I reset my password" and "I forgot my login credentials" mean the same thing. Modern systems often combine both (**hybrid search**). Semantic search is what makes "ask a question, get relevant passages" possible, which is exactly what RAG needs (Chapter 11).

---

## Vector databases: nearest-neighbor at scale

Finding the nearest vectors among a handful of items is trivial (the loop above). Doing it among *millions* of vectors, fast, is a real engineering problem — solved by **vector databases.**

> 💡 **Concept notes — vector databases and ANN**
> A **vector database** (Pinecone, Weaviate, Chroma, pgvector, FAISS, and others) stores embeddings and answers "find the k most similar vectors to this one" extremely fast, even over millions or billions of items. It uses **approximate nearest neighbor (ANN)** algorithms — trading a tiny bit of accuracy for enormous speed, because exact search over billions of vectors is too slow. You'll meet vector databases again in Chapter 11; for now, know that they are the storage-and-retrieval backbone of modern AI applications. This is just kNN (Chapter 4) — "find the most similar examples" — industrialized.

---

## Embeddings are everywhere

The pattern generalizes far beyond words:

> 💡 **Concept notes — embeddings beyond text**
> - **Sentences/documents:** embed whole passages for search and RAG.
> - **Images:** embed photos so "find visually similar images" or "search images by text" works (CLIP-style models put images and text in the *same* space).
> - **Products/users:** recommendation systems embed users and items so "users like you also liked" becomes nearest-neighbor lookup.
> - **Code, audio, molecules, anything:** if you can train a model to produce meaning-preserving vectors, you can search, cluster, and compare them.
> Whenever you hear "the system understands similarity" or "semantic," there are embeddings underneath. It is genuinely one of the most reusable ideas in all of software.

---

## Try it

1. Why is assigning each word an arbitrary ID number (dog=5, cat=6) a bad representation? What does an embedding give you that an ID doesn't?
2. Explain "king − man + woman ≈ queen" in terms of directions in the embedding space.
3. Why does cosine similarity look at the *angle* between vectors rather than the distance? When would length not matter for meaning?
4. A user searches your help center for "can't log in." Keyword search returns nothing useful even though there's a great article titled "Resetting a forgotten password." What's happening, and how does semantic search fix it?
5. What problem does a vector database solve that a simple loop over all vectors doesn't, and what does it trade away to do so?


---

## The bumper sticker

> *Embeddings turn meaning into geometry: similar things become nearby vectors, so "understanding similarity" becomes "find the nearest neighbors." Embed, then search — that one move powers semantic search, recommendations, and the retrieval behind every RAG system.*

Next: the architecture that turned good embeddings into ChatGPT — the Transformer, and the attention mechanism at its heart.

---

<div align="right">

[Chapter 8 →](aiml-chapter-8.md)

</div>
