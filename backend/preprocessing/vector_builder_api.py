from sentence_transformers import SentenceTransformer
from tqdm import tqdm

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)
print("✓ Embedding model loaded")


def build_embeddings(chunks):

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    results = []

    for chunk, embedding in zip(chunks, embeddings):

        results.append({

            **chunk,

            "embedding": embedding.tolist()

        })

    return results


if __name__ == "__main__":

    from extractor_api import extract_pdf
    from cleaner_api import clean_text
    from chunker_api import chunk_document

    while True:

        pdf = input("\nPDF Path: ")

        if pdf.lower() == "exit":
            break

        text = extract_pdf(pdf)

        text = clean_text(text)

        chunks = chunk_document(text)

        embeddings = build_embeddings(chunks)

        print("\nTotal Embeddings :", len(embeddings))

        print("\nEmbedding Dimension :", len(embeddings[0]["embedding"]))