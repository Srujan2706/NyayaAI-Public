import chromadb

client = chromadb.PersistentClient(path="vector_db/chroma_db")
collection = client.get_collection("legal_documents")

results = collection.get(where={"section": "Article 21"})

print("Found:", len(results["documents"]))

if len(results["documents"]) > 0:
    print("\nMetadata:")
    print(results["metadatas"][0])

    print("\nDocument:")
    print(results["documents"][0][:1000])