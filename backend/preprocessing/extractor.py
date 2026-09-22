import os
import fitz


INPUT_FOLDER = "data/raw/pdf"
OUTPUT_FOLDER = "data/raw/text"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def extract_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF.
    """

    document = fitz.open(pdf_path)

    pages = []

    for page in document:

        text = page.get_text("text")

        if not text.strip():
            print(f"⚠ Scanned page detected (Page {page.number + 1})")

        pages.append(text)

    document.close()

    return "\n".join(pages)


def save_text(text: str, output_path: str):

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def process_all_pdfs():

    pdf_files = sorted([
        file
        for file in os.listdir(INPUT_FOLDER)
        if file.lower().endswith(".pdf")
    ])

    if not pdf_files:
        print("No PDF files found.")
        return

    print("\n========== Extracting PDFs ==========\n")

    for pdf in pdf_files:

        pdf_path = os.path.join(INPUT_FOLDER, pdf)

        output_path = os.path.join(
            OUTPUT_FOLDER,
            pdf.replace(".pdf", "_raw.txt")
        )

        try:

            text = extract_pdf(pdf_path)

            save_text(text, output_path)

            print(f"✓ {pdf}")

        except Exception as e:

            print(f"✗ {pdf}")

            print(e)

    print("\n====================================")
    print("PDF Extraction Completed")
    print("====================================")


def run():
    process_all_pdfs()


if __name__ == "__main__":
    run()