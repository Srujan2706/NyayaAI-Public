import os
import json
import re

# Folder containing chunk JSON files
input_folder = "chunks"

# Full names of laws
law_names = {
    "BNS": "Bharatiya Nyaya Sanhita, 2023",
    "BNSS": "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "BSA": "Bharatiya Sakshya Adhiniyam, 2023",
    "Constitution": "Constitution of India"
}

# Process every chunk file
for filename in os.listdir(input_folder):

    if filename.endswith("_chunks.json"):

        filepath = os.path.join(input_folder, filename)

        print(f"\nProcessing: {filename}")

        with open(filepath, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        law = filename.replace("_chunks.json", "")

        current_chapter = "Unknown"

        for i, chunk in enumerate(chunks):

            text = chunk.get("text", "")

            # ---------- Chapter ----------
            chapter_match = re.search(
                r'CHAPTER\s+[IVXLC\d]+',
                text,
                re.IGNORECASE
            )

            if chapter_match:
                current_chapter = chapter_match.group()

            # ---------- Section ----------
            section_match = re.search(
                r'Section\s+(\d+)',
                text,
                re.IGNORECASE
            )

            if section_match:
                section = section_match.group(1)
            else:
                section = "Unknown"

            # ---------- Title ----------
            lines = text.split("\n")

            title = "Unknown"

            for line in lines:

                line = line.strip()

                if line == "":
                    continue

                if line.lower().startswith("section"):
                    continue

                if line.upper().startswith("CHAPTER"):
                    continue

                title = line
                break

            # ---------- Chunk ID ----------
            if "chunk_id" in chunk:
                chunk_id = chunk["chunk_id"]

            elif "id" in chunk:
                chunk_id = chunk["id"]

            else:
                chunk_id = i

            # ---------- Add Metadata ----------
            chunk["chunk_id"] = chunk_id

            # Remove old id if it exists
            if "id" in chunk:
                del chunk["id"]

            chunk["law"] = law
            chunk["law_full_name"] = law_names.get(law, law)
            chunk["source_file"] = law + ".pdf"
            chunk["chapter"] = current_chapter
            chunk["section"] = section
            chunk["title"] = title

        # Save updated JSON
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=4, ensure_ascii=False)

        print(f"✓ Metadata added successfully to {filename}")

print("\n====================================")
print("All metadata added successfully!")
print("====================================")