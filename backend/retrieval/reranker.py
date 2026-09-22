from typing import List, Dict, Any

from sentence_transformers import CrossEncoder

from backend.utils.config import (
    RERANK_MODEL,
    RERANK_TOP_K,
)

print("Loading Cross Encoder...")

model = CrossEncoder(RERANK_MODEL)

print("✓ Cross Encoder Loaded")


def rerank(
    query: str,
    results: List[Dict[str, Any]],
    top_k: int = RERANK_TOP_K,
) -> List[Dict[str, Any]]:

    if not results:
        return []

    pairs = [
        (query, item["document"])
        for item in results
    ]

    scores = model.predict(pairs)

    ranked = sorted(
        zip(scores, results),
        key=lambda x: x[0],
        reverse=True,
    )

    reranked = []

    for score, item in ranked[:top_k]:

        item["score"] = float(score)          # Used by Streamlit/API
        item["rerank_score"] = float(score)   # Keep old key for compatibility

        reranked.append(item)

    return reranked


if __name__ == "__main__":

    sample = [
        {
            "document": "Whoever commits murder shall be punished with death or imprisonment for life.",
            "metadata": {
                "law": "BNS",
                "section": "Section 103",
                "title": "Punishment for Murder",
            },
        },
        {
            "document": "Every person has the right to freedom of speech.",
            "metadata": {
                "law": "Constitution",
                "section": "Article 19",
                "title": "Freedom of Speech",
            },
        },
    ]

    results = rerank("punishment for murder", sample)

    for i, item in enumerate(results, 1):
        print("=" * 60)
        print(f"Result {i}")
        print("Score   :", round(item["score"], 4))
        print("Law     :", item["metadata"]["law"])
        print("Section :", item["metadata"]["section"])
        print("Title   :", item["metadata"]["title"])
        print()
        print(item["document"])