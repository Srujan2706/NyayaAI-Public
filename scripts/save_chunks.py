import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Folder paths
input_folder = "cleaned_data"
output_folder = "chunks"

# Create chunks folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# LangChain splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

# Process all cleaned text files
for filename in os.listdir(input_folder):

    if filename.endswith("_clean.txt"):

        input_path = os.path.join(input_folder, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = splitter.split_text(text)

        chunk_list = []

        for i, chunk in enumerate(chunks):

            chunk_list.append({

                "id": i,

                "document": filename,

                "text": chunk

            })

        output_file = filename.replace("_clean.txt", "_chunks.json")

        output_path = os.path.join(output_folder, output_file)

        with open(output_path, "w", encoding="utf-8") as f:

            json.dump(chunk_list, f, indent=4, ensure_ascii=False)

        print(f"✅ Saved {len(chunks)} chunks from {filename}")

print("\n🎉 All chunk files created successfully!")