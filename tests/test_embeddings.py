import os
import json

folder = "vector_db"

for file in os.listdir(folder):

    if file.endswith("_embeddings.json"):

        path = os.path.join(folder, file)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(file, "->", len(data), "chunks")

        if len(data) > 0:
            print("Law:", data[0]["law"])
            print("------------------------")