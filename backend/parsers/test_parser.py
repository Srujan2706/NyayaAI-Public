from backend.preprocessing.extractor_api import extract_pdf
from backend.parsers.judgment_parser import parse_judgment

pdf = input("PDF Path : ")

pages = extract_pdf(pdf)

# Convert pages into one string
text = "\n".join(page["text"] for page in pages)

data = parse_judgment(text)

for key, value in data.items():

    print("=" * 80)
    print(key.upper())
    print("-" * 80)

    if isinstance(value, str):
        print(value[:1500])
    else:
        print(value)