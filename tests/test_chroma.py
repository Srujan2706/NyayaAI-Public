from backend.retrieval.chroma import semantic_search

query = input("Ask a legal question: ")

results = semantic_search(query)

for i, doc in enumerate(results["documents"][0]):
    print(f"\nResult {i+1}")
    print("-" * 60)
    print(doc[:800])