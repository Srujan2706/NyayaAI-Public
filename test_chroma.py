import chromadb

client = chromadb.PersistentClient(path="vector_db/chroma_db")

collection = client.get_collection("legal_documents")

print("Total documents in DB:", collection.count())

results = collection.get()

laws = {}

for meta in results["metadatas"]:
    law = meta.get("law", "Unknown")
    laws[law] = laws.get(law, 0) + 1

print("\nDocuments by Law:\n")

for law, count in laws.items():
    print(law, ":", count)