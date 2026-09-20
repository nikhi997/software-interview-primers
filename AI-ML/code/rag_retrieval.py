"""
Chapter 11 — Giving the model your data (RAG).

A toy Retrieval-Augmented Generation pipeline in pure Python (no numpy,
no API calls). It shows the RETRIEVAL half of RAG — the part that actually
decides whether a RAG system works.

Real RAG: embed with a model, store in a vector DB, then call an LLM to
generate. Here we fake the embedding with a tiny bag-of-words vectorizer
so the whole thing runs offline, but the query path is the real one:

    embed the question -> retrieve nearest chunks -> build a grounded prompt

Run:  python3 rag_retrieval.py
"""

import re
from collections import Counter

# --- Our tiny "knowledge base": chunks of internal docs ---
KNOWLEDGE_BASE = [
    "To reset your password, click 'Forgot password' on the login page "
    "and follow the emailed link. The link expires after one hour.",
    "Our refund policy allows returns within 30 days of purchase. "
    "Refunds are processed to the original payment method in 5-7 business days.",
    "The mobile app supports iOS 15 and later and Android 10 and later. "
    "Older devices are not supported.",
    "Business-tier accounts include priority support and a 99.9% uptime SLA. "
    "Contact your account manager to upgrade.",
    "To export your data, go to Settings > Privacy > Export. "
    "We email you a download link when the export is ready.",
]


# Common words carry no meaning for retrieval; a real embedding model learns
# to downweight them automatically. We drop them by hand so this toy matches
# on CONTENT words ("refund", "password") instead of "to"/"the"/"do".
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "for", "from",
    "get", "go", "how", "i", "if", "in", "is", "it", "later", "me", "my",
    "of", "on", "or", "our", "the", "to", "we", "what", "when", "you", "your",
}


def tokenize(text):
    return [w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOPWORDS]


def embed(text):
    # Stand-in for a real embedding model: a bag-of-words count vector
    # over content words only. Crude, but enough to demonstrate
    # "similar text -> similar vector."
    return Counter(tokenize(text))


def cosine_similarity(vec_a, vec_b):
    shared = set(vec_a) & set(vec_b)
    dot = sum(vec_a[t] * vec_b[t] for t in shared)
    norm_a = sum(v * v for v in vec_a.values()) ** 0.5
    norm_b = sum(v * v for v in vec_b.values()) ** 0.5
    return dot / (norm_a * norm_b + 1e-9)


# Precompute "embeddings" for the knowledge base (the offline indexing step).
INDEX = [(chunk, embed(chunk)) for chunk in KNOWLEDGE_BASE]


def retrieve(question, k=2):
    q_vec = embed(question)
    scored = [(chunk, cosine_similarity(q_vec, c_vec)) for chunk, c_vec in INDEX]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]


def build_grounded_prompt(question, retrieved_chunks):
    context = "\n".join(f"- {chunk}" for chunk, _ in retrieved_chunks)
    return (
        "Answer the question using ONLY the context below. "
        "If the answer is not in the context, say you don't know.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )


if __name__ == "__main__":
    questions = [
        "What is the refund policy?",
        "How do I reset my password?",
        "What is the capital of France?",  # not in the KB -> should be weak
    ]
    for q in questions:
        print("=" * 60)
        print(f"Q: {q}")
        retrieved = retrieve(q)
        print(f"Top retrieved chunk (score={retrieved[0][1]:.3f}):")
        print(f"  {retrieved[0][0][:70]}...")
        if retrieved[0][1] < 0.05:
            print("  -> retrieval score is low; a good RAG prompt would let")
            print("     the model answer 'I don't know' instead of hallucinating.")
        print("\n--- Prompt that would be sent to the LLM ---")
        print(build_grounded_prompt(q, retrieve(q)))
        print()
