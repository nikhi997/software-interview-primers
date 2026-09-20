"""
Chapter 7 — Everything becomes a vector.

Embeddings + cosine similarity, in pure Python (no numpy).
"Similar in meaning" becomes "close together in vector space."

These toy 4-dimensional vectors stand in for real embeddings
(which are hundreds or thousands of dimensions, produced by a model).
The MATH is identical to what a real semantic-search system does.

Run:  python3 embeddings_similarity.py
"""


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return sum(x * x for x in a) ** 0.5


def cosine_similarity(a, b):
    # Angle-based similarity: 1.0 = same direction (same meaning),
    # 0.0 = unrelated, -1.0 = opposite. Length is ignored.
    return dot(a, b) / (norm(a) * norm(b) + 1e-9)


# Toy "embeddings": dimensions loosely mean [animal, vehicle, size, speed].
# Notice dog/puppy point the same way; car points elsewhere.
VECTORS = {
    "dog":   [0.9, 0.0, 0.5, 0.4],
    "puppy": [0.85, 0.0, 0.3, 0.5],
    "wolf":  [0.8, 0.0, 0.6, 0.7],
    "car":   [0.0, 0.9, 0.7, 0.9],
    "truck": [0.0, 0.95, 0.9, 0.6],
    "bike":  [0.0, 0.7, 0.3, 0.4],
}


def most_similar(query_word, k=3):
    query = VECTORS[query_word]
    scored = [
        (word, cosine_similarity(query, vec))
        for word, vec in VECTORS.items()
        if word != query_word
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]


if __name__ == "__main__":
    for word in ["dog", "car"]:
        print(f"Most similar to '{word}':")
        for other, score in most_similar(word):
            print(f"   {other:6s}  cosine={score:.3f}")
        print()

    print("Cross-checks (high = similar meaning, low = unrelated):")
    print(f"   dog  vs puppy : {cosine_similarity(VECTORS['dog'], VECTORS['puppy']):.3f}")
    print(f"   dog  vs car   : {cosine_similarity(VECTORS['dog'], VECTORS['car']):.3f}")
    print(f"   car  vs truck : {cosine_similarity(VECTORS['car'], VECTORS['truck']):.3f}")
