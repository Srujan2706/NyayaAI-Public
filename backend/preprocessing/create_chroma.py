import json
from pathlib import Path

import chromadb

from backend.utils.config import (
    PERMANENT_DB,
    PERMANENT_EMBEDDINGS,
)

COLLECTION_NAME = "legal_documents"


def create_collection(
    embedding_folder,
    db_path,
    collection_name=COLLECTION_NAME,
):

    print("\n" + "=" * 80)
    print("CREATING CHROMA COLLECTION")
    print("=" * 80)

    print("Embedding Folder :", embedding_folder)
    print("Database Path    :", db_path)
    print("Collection Name  :", collection_name)

    client = chromadb.PersistentClient(path=str(db_path))

    # Delete old collection
    try:
        client.delete_collection(collection_name)
        print(f"✓ Deleted existing collection '{collection_name}'")
    except Exception:
        print("No previous collection found.")

    # Create new collection
    collection = client.create_collection(collection_name)

    print("✓ New collection created")

    files = sorted(Path(embedding_folder).glob("*_embeddings.json"))

    print(f"\nFound {len(files)} embedding file(s)")

    if not files:
        print("❌ No embedding files found.")
        return

    total = 0

    for file in files:

        print("\n" + "-" * 60)
        print("Processing :", file.name)

        with open(file, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        print("Chunks Loaded :", len(chunks))

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for chunk in chunks:

            ids.append(str(chunk["chunk_id"]))
            documents.append(chunk["text"])
            embeddings.append(chunk["embedding"])

            metadata = {}

            for key in [
                "law",
                "law_full_name",
                "part",
                "part_no",
                "chapter",
                "chapter_no",
                "chapter_title",
                "section",
                "section_no",
                "title",
                "parent_id",
                "page",
                "document_type"
            ]:

                value = chunk.get(key)

                if value is None:
                    continue

                if isinstance(value, (str, int, float, bool)):
                    metadata[key] = value
                else:
                    metadata[key] = str(value)

            metadatas.append(metadata)

        print("\nFirst Metadata")
        print(metadatas[0])

        print("\nAdding to Chroma...")

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print("✓ Added", len(ids), "chunks")

        print("Collection Count :", collection.count())

        total += len(ids)

    print("\n" + "=" * 80)
    print("FINAL COLLECTION COUNT :", collection.count())
    print("TOTAL CHUNKS ADDED     :", total)
    print("=" * 80)


def run():

    create_collection(
        PERMANENT_EMBEDDINGS,
        PERMANENT_DB,
        COLLECTION_NAME,
    )


if __name__ == "__main__":
    run()