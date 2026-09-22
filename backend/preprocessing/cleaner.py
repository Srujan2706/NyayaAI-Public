import os
import re

INPUT_FOLDER = "data/raw/text"
OUTPUT_FOLDER = "data/processed/cleaned"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def clean_text(text: str) -> str:

    replacements = {
        "â€”": "—",
        "â€“": "–",
        "â€œ": '"',
        "â€\x9d": '"',
        "â€˜": "'",
        "â€™": "'",
        "Â": "",
        "\ufeff": "",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    text = re.sub(r"\t", " ", text)
    text = re.sub(r" +", " ", text)

    text = re.sub(
        r"THE CONSTITUTION OF INDIA",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^\d+\s*$",
        "",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"^\d+\s*Subs\..*$",
        "",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"^\d+\s*Ins\..*$",
        "",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"^\*.*$",
        "",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def process_file(filename):

    input_path = os.path.join(INPUT_FOLDER, filename)

    output_path = os.path.join(
        OUTPUT_FOLDER,
        filename.replace("_raw.txt", "_clean.txt")
    )

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    cleaned = clean_text(text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"✓ {filename}")


def run():

    files = sorted([
        f
        for f in os.listdir(INPUT_FOLDER)
        if f.endswith("_raw.txt")
    ])

    print("\n========== Cleaning ==========\n")

    for file in files:
        process_file(file)

    print("\n==============================")
    print("Cleaning Completed")
    print("==============================")


if __name__ == "__main__":
    run()