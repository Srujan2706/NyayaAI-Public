import os
import re
import json

input_folder = "cleaned_data"
output_folder = "chunks"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):

    if filename.endswith("_clean.txt"):

        input_path = os.path.join(input_folder, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        print(f"\nProcessing: {filename}")

        # ---------------------------------------
        # Constitution Chunking
        # ---------------------------------------

        if filename.startswith("Constitution"):

            # Split before every article number like:
            # 1.
            # 2.
            # 21.
            chunks = re.split(
                r'(?=^\d+\.\s)',
                text,
                flags=re.MULTILINE
            )

        # ---------------------------------------
        # BNS / BNSS / BSA Chunking
        # ---------------------------------------

        else:

            chunks = re.split(
                r'(?=Section\s+\d+)',
                text,
                flags=re.IGNORECASE
            )

        data = []

        chunk_id = 1

        for chunk in chunks:

            chunk = chunk.strip()

            if len(chunk) < 100:
                continue

            data.append(
                {
                    "id": chunk_id,
                    "document": filename,
                    "text": chunk
                }
            )

            chunk_id += 1

        output_file = filename.replace(
            "_clean.txt",
            "_chunks.json"
        )

        output_path = os.path.join(
            output_folder,
            output_file
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(f"✓ Created {len(data)} chunks")

print("\n====================================")
print("All documents chunked successfully!")
print("====================================")