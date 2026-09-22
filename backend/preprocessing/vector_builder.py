import json
from pathlib import Path
from typing import List, Dict, Any

from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from backend.utils.config import (
    PERMANENT_CHUNKS,
    PERMANENT_EMBEDDINGS,
    EMBEDDING_MODEL,
)

print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)
print("✓ Embedding model loaded")


def process_file(chunk_file: Path) -> None:

    with open(chunk_file, "r", encoding="utf-8") as f:
        chunks: List[Dict[str, Any]] = json.load(f)

    if not chunks:
        print(f"Skipping empty file: {chunk_file.name}")
        return

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    output = []

    for chunk, embedding in zip(chunks, embeddings):

        chunk["embedding"] = embedding.tolist()

        output.append(chunk)

    output_file = (
        PERMANENT_EMBEDDINGS /
        chunk_file.name.replace(
            "_chunks",
            "_embeddings"
        )
    )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"✓ {chunk_file.name} → "
        f"{output_file.name} "
        f"({len(output)} embeddings)"
    )


def run() -> None:

    PERMANENT_EMBEDDINGS.mkdir(
        parents=True,
        exist_ok=True
    )

    files = sorted(
        PERMANENT_CHUNKS.glob("*_chunks.json")
    )

    if not files:
        print("No chunk files found.")
        return

    print(f"\nFound {len(files)} files.\n")

    for file in tqdm(files, desc="Embedding Files"):

        process_file(file)

    print("\n====================================")
    print("✓ All embeddings generated successfully!")
    print("====================================")


if __name__ == "__main__":
    run()