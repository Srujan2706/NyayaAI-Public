from backend.retrieval.hybrid import hybrid_search
from backend.llm.ollama import generate_answer


def main():

    while True:

        question = input("\nAsk: ")

        if question.lower() == "exit":
            break

        docs = hybrid_search(question)

        answer = generate_answer(question, docs)

        print("\n" + "=" * 80)
        print(answer)
        print("=" * 80)


if __name__ == "__main__":
    main()