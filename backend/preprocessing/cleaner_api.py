import re


def clean_text(text: str) -> str:

    text = text.replace("\x0c", "\n")

    text = re.sub(r"\r", "\n", text)

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    text = re.sub(
        r"^\s*\d+\s*$",
        "",
        text,
        flags=re.MULTILINE
    )

    text = text.replace("â€”", "—")

    text = text.replace("â€“", "–")

    text = text.replace("â€˜", "'")

    text = text.replace("â€™", "'")

    text = text.replace("â€œ", '"')

    text = text.replace("â€\x9d", '"')

    return text.strip()


if __name__ == "__main__":

    from extractor_api import extract_pdf

    while True:

        pdf = input("\nPDF Path: ")

        if pdf.lower() == "exit":
            break

        text = extract_pdf(pdf)

        cleaned = clean_text(text)

        print("\n==============================\n")

        print(cleaned[:1500])

        print("\n==============================")