from backend.service import ask


def main():

    while True:

        question = input("\nAsk: ")

        if question.lower() == "exit":
            break

        result = ask(question)

        print("\n" + "=" * 80)
        print(result["answer"])
        print("=" * 80)

        print("\nSources:\n")

        for source in result["sources"]:

            print(
                f"{source['law']} | "
                f"{source['section']} | "
                f"{source['chapter']}"
            )


if __name__ == "__main__":
    main()