from pathlib import Path
import fitz


def extract_pdf(pdf_path: str):
    """
    Extracts text from a PDF while preserving page numbers.

    Returns:
        List[dict]
        [
            {
                "page": 1,
                "text": "..."
            },
            ...
        ]
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    document = fitz.open(pdf_path)

    pages = []

    for page_no, page in enumerate(document, start=1):

        pages.append({
            "page": page_no,
            "text": page.get_text()
        })

    document.close()

    return pages


if __name__ == "__main__":

    while True:

        pdf = input("\nPDF Path: ")

        if pdf.lower() == "exit":
            break

        extracted = extract_pdf(pdf)

        print("\n==============================\n")

        print("Total Pages :", len(extracted))

        print("\nFirst Page:\n")

        print(extracted[0]["text"][:1000])

        print("\n==============================")