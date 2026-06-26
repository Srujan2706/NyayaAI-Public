from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import json

input_folder = "cleaned_data"
output_folder = "chunks"

os.makedirs(output_folder, exist_ok=True)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

for filename in os.listdir(input_folder):

    if filename.endswith("_clean.txt"):

        input_path = os.path.join(input_folder, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = splitter.split_text(text)

        data = []

        for i, chunk in enumerate(chunks):

            data.append({
                "chunk_id": i + 1,
                "document": filename,
                "text": chunk
            })

        output_file = filename.replace("_clean.txt", "_langchain_chunks.json")

        with open(
            os.path.join(output_folder, output_file),
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"✅ {filename} → {len(chunks)} chunks")

print("\n🎉 All documents processed successfully!")