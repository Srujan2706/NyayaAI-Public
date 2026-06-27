import ollama
from retriever import retrieve_documents


def generate_answer(question):

    # Retrieve relevant legal documents
    results = retrieve_documents(question)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Get the first (best) result
    legal_text = documents[0]
    metadata = metadatas[0]

    # Build context for Ollama
    prompt = f"""
You are NyayaAI, an AI-powered legal assistant.

Answer ONLY using the legal text below.

LAW:
{metadata['law']}

SECTION:
{metadata['section']}

TITLE:
{metadata['title']}

LEGAL TEXT:
{legal_text}

QUESTION:
{question}

Give a simple explanation.
"""

    response = ollama.chat(
        model="phi3:mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Return everything instead of only the answer
    return {
        "answer": response["message"]["content"],
        "law": metadata["law"],
        "section": metadata["section"],
        "chapter": metadata["chapter"],
        "title": metadata["title"],
        "legal_text": legal_text
    }


if __name__ == "__main__":

    while True:

        question = input("\nAsk Question (exit to quit): ")

        if question.lower() == "exit":
            break

        result = generate_answer(question)

        print("\n==========================")
        print("LAW      :", result["law"])
        print("SECTION  :", result["section"])
        print("CHAPTER  :", result["chapter"])
        print("TITLE    :", result["title"])

        print("\nLEGAL TEXT\n")
        print(result["legal_text"])

        print("\nAI EXPLANATION\n")
        print(result["answer"])