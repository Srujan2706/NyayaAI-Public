import os
import re

input_folder = "cleaned_data"

for filename in os.listdir(input_folder):

    if filename.endswith("_raw.txt"):

        input_path = os.path.join(input_folder, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        # -------------------------
        # Basic Cleaning
        # -------------------------

        text = text.replace("\t", " ")

        text = re.sub(r' +', ' ', text)

        # -------------------------
        # Constitution Cleaning
        # -------------------------

        if filename.startswith("Constitution"):

            # Remove page header
            text = re.sub(
                r'THE CONSTITUTION OF INDIA',
                '',
                text,
                flags=re.IGNORECASE
            )

            # Remove page numbers (lines containing only digits)
            text = re.sub(
                r'^\d+\s*$',
                '',
                text,
                flags=re.MULTILINE
            )

            # Remove amendment footnotes
            text = re.sub(
                r'^\d+Subs\..*$',
                '',
                text,
                flags=re.MULTILINE
            )

            text = re.sub(
                r'^\*.*$',
                '',
                text,
                flags=re.MULTILINE
            )

            text = re.sub(
                r'^\*\*.*$',
                '',
                text,
                flags=re.MULTILINE
            )

            text = re.sub(
                r'^\*\*\*.*$',
                '',
                text,
                flags=re.MULTILINE
            )

        # -------------------------
        # Remove extra blank lines
        # -------------------------

        text = re.sub(r'\n\s*\n+', '\n\n', text)

        text = text.strip()

        output_filename = filename.replace("_raw.txt", "_clean.txt")

        output_path = os.path.join(input_folder, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Cleaned: {filename}")

print("\nAll files cleaned successfully!")
