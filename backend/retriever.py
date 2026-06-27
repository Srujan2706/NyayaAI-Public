import re
import chromadb
from sentence_transformers import SentenceTransformer

# -----------------------------------------
# Load Embedding Model
# -----------------------------------------

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Embedding model loaded successfully!")

# -----------------------------------------
# Connect to ChromaDB
# -----------------------------------------

client = chromadb.PersistentClient(path="vector_db/chroma_db")

collection = client.get_collection(name="legal_documents")

print("Connected to ChromaDB!")

# -----------------------------------------
# Retrieval Function
# -----------------------------------------

def retrieve_documents(query, top_k=5):

    # Check if user asks for an Article number
    article_match = re.search(r"article\s+(\d+)", query, re.IGNORECASE)

    if article_match:
        article_no = article_match.group(1)

        print(f"\nSearching directly for Article {article_no}...")

        results = collection.get(
            where={"section": f"Article {article_no}"}
        )

        if len(results["ids"]) > 0:
            return {
                "documents": [results["documents"]],
                "metadatas": [results["metadatas"]],
                "distances": [[0.0] * len(results["documents"])]
            }

    # Semantic search
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results

# -----------------------------------------
# Main Program
# -----------------------------------------

if __name__ == "__main__":

    print("\n==============================")
    print("NyayaAI Retrieval System")
    print("==============================")

    while True:

        query = input("\nAsk a Legal Question (type 'exit' to quit): ")

        if query.lower() == "exit":
            break

        results = retrieve_documents(query)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        print("\n==============================")
        print("Top Retrieved Results")
        print("==============================\n")

        for i in range(len(documents)):

            print(f"Result {i+1}")
            print("-" * 60)

            print("Law      :", metadatas[i]["law"])
            print("Chapter  :", metadatas[i]["chapter"])
            print("Section  :", metadatas[i]["section"])
            print("Title    :", metadatas[i]["title"])

            print("\nDistance :", distances[i])

            print("\nLegal Text:\n")
            print(documents[i])

            print("\n" + "=" * 80)