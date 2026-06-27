import os
import json
import chromadb

client = chromadb.PersistentClient(path="vector_db/chroma_db")

collection = client.get_or_create_collection(
    name="legal_documents"
)

input_folder = "vector_db"

print("Loading embedding files...\n")

for filename in os.listdir(input_folder):

    if filename.endswith("_embeddings.json"):

        print(f"Reading {filename}")

        filepath = os.path.join(input_folder, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        print(f"Total chunks in {filename}: {len(chunks)}")

        added = 0

        for chunk in chunks:

            try:

                collection.add(
                    ids=[f"{chunk['law']}_{chunk['chunk_id']}"],
                    embeddings=[chunk["embedding"]],
                    documents=[chunk["text"]],
                    metadatas=[{
                        "law": chunk["law"],
                        "section": str(chunk["section"]),
                        "chapter": chunk["chapter"],
                        "title": chunk["title"]
                    }]
                )

                added += 1

            except Exception as e:
                print("Error:", e)

        print(f"Inserted {added} chunks from {filename}\n")

print("----------------------------------")
print("Total documents in DB:", collection.count())
print("----------------------------------")