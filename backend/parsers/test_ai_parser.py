from backend.preprocessing.extractor_api import extract_pdf
from backend.parsers.ai_parser import analyze_document

pdf = input("PDF : ")

pages = extract_pdf(pdf)

text = "\n".join(
    page["text"]
    for page in pages
)

result = analyze_document(text)

print(result)