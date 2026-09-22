import re

from langchain_text_splitters import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)


def chunk_document(text: str):

    chunks = splitter.split_text(text)

    data = []

    for i, chunk in enumerate(chunks, start=1):

        data.append({

            "chunk_id": i,

            "text": chunk,

            "char_count": len(chunk),

            "word_count": len(chunk.split())

        })

    return data


if __name__ == "__main__":

    from extractor_api import extract_pdf

    from cleaner_api import clean_text

    while True:

        pdf = input("\nPDF Path: ")

        if pdf.lower() == "exit":
            break

        text = extract_pdf(pdf)

        text = clean_text(text)

        chunks = chunk_document(text)

        print("\nTotal Chunks :", len(chunks))

        print("\n==============================\n")

        print(chunks[0]["text"])

        print("\n==============================")