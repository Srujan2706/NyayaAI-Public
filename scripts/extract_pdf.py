import fitz
import os

# Input and output folders
dataset_folder = "datasets"
output_folder = "cleaned_data"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Process every PDF
for filename in os.listdir(dataset_folder):

    if filename.endswith(".pdf"):

        pdf_path = os.path.join(dataset_folder, filename)

        pdf = fitz.open(pdf_path)

        text = ""

        for page in pdf:
            text += page.get_text()

        output_file = os.path.join(
            output_folder,
            filename.replace(".pdf", "_raw.txt")
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"✅ Extracted: {filename}")

print("\nAll PDFs extracted successfully!")