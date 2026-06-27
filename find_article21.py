import chromadb

client = chromadb.PersistentClient(path="vector_db/chroma_db")
collection = client.get_collection("legal_documents")

results = collection.get(where={"law": "Constitution"})

found = False

for meta, doc in zip(results["metadatas"], results["documents"]):
    if meta["section"] == "Article 21":
        print("FOUND ARTICLE 21")
        print(meta)
        print("-" * 60)
        print(doc[:1000])
        found = True
        break

if not found:
    print("Article 21 NOT FOUND")