import os
import json
from sentence_transformers import SentenceTransformer

# Folder paths
input_folder = "chunks"
output_folder = "vector_db"

# Create vector_db folder
os.makedirs(output_folder, exist_ok=True)

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded successfully!\n")

# Process each JSON file
for filename in os.listdir(input_folder):

    if filename.endswith("_chunks.json"):

        filepath = os.path.join(input_folder, filename)

        print(f"Processing: {filename}")

        with open(filepath, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        for chunk in chunks:

            text = chunk["text"]

            # Generate embedding
            embedding = model.encode(text)

            # Convert NumPy array to Python list
            chunk["embedding"] = embedding.tolist()

        output_file = filename.replace(
            "_chunks.json",
            "_embeddings.json"
        )

        output_path = os.path.join(output_folder, output_file)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=4, ensure_ascii=False)

        print(f"✓ Saved embeddings for {filename}\n")

print("===================================")
print("All embeddings generated successfully!")
print("===================================")