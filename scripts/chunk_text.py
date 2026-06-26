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

        # Split whenever a new Section starts
        chunks = re.split(r'(?=Section\s+\d+)', text)

        data = []

        for i, chunk in enumerate(chunks):

            chunk = chunk.strip()

            if len(chunk) > 20:

                data.append({
                    "id": i + 1,
                    "document": filename,
                    "text": chunk
                })

        output_file = filename.replace("_clean.txt", "_chunks.json")

        with open(
            os.path.join(output_folder, output_file),
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"✅ Chunked: {filename}")

print("\n🎉 All documents chunked successfully!")