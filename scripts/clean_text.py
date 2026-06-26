import os
import re

# Folder containing extracted text
input_folder = "cleaned_data"

# Read every raw text file
for filename in os.listdir(input_folder):

    if filename.endswith("_raw.txt"):

        input_path = os.path.join(input_folder, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Remove page numbers like "Page 17"
        text = re.sub(r'Page\s+\d+', '', text)

        # Remove tabs
        text = text.replace('\t', ' ')

        # Replace multiple spaces with one space
        text = re.sub(r' +', ' ', text)

        # Replace multiple blank lines with two newlines
        text = re.sub(r'\n\s*\n+', '\n\n', text)

        # Remove extra spaces at the beginning/end
        text = text.strip()

        # Create cleaned filename
        output_filename = filename.replace("_raw.txt", "_clean.txt")

        output_path = os.path.join(input_folder, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"✅ Cleaned: {filename}")

print("\n🎉 All files cleaned successfully!")