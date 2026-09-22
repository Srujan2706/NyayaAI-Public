from pathlib import Path
import json
import re
import shutil

from backend.preprocessing.document_classifier import detect_document_type
from backend.preprocessing.extractor_api import extract_pdf
from backend.preprocessing.cleaner_api import clean_text
from backend.preprocessing.chunker_api import chunk_document
from backend.preprocessing.vector_builder_api import build_embeddings
from backend.preprocessing.create_chroma import create_collection
from backend.parsers.ai_parser import parse_document

from backend.utils.config import (
    DYNAMIC_RAW,
    DYNAMIC_CLEANED,
    DYNAMIC_CHUNKS,
    DYNAMIC_EMBEDDINGS,
    DYNAMIC_PROFILES,
    DYNAMIC_DB,
)


def process_uploaded_pdf(pdf_path: str):

    pdf_path = Path(pdf_path)
    # ============================================
# Remove previous uploaded document
# ============================================

    for folder in [

        DYNAMIC_RAW,

        DYNAMIC_CLEANED,

        DYNAMIC_CHUNKS,

        DYNAMIC_EMBEDDINGS

    ]:

        if folder.exists():

            shutil.rmtree(folder)

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    # =====================================================
    # Create folders
    # =====================================================

    DYNAMIC_RAW.mkdir(parents=True, exist_ok=True)
    DYNAMIC_CLEANED.mkdir(parents=True, exist_ok=True)
    DYNAMIC_CHUNKS.mkdir(parents=True, exist_ok=True)
    DYNAMIC_EMBEDDINGS.mkdir(parents=True, exist_ok=True)
    DYNAMIC_PROFILES.mkdir(parents=True, exist_ok=True)

    name = pdf_path.stem

    # =====================================================
    # Extract PDF
    # =====================================================

    pages = extract_pdf(str(pdf_path))

    raw_text = ""

    for page in pages:

        raw_text += f"\n\n<<PAGE {page['page']}>>\n\n"

        raw_text += page["text"]

    raw_file = DYNAMIC_RAW / f"{name}.txt"

    raw_file.write_text(
        raw_text,
        encoding="utf-8"
    )

    # =====================================================
    # Detect Document Type
    # =====================================================

    document_type = detect_document_type(raw_text)

    print("\nDetected Document Type :", document_type)

    # =====================================================
    # AI Parsing
    # =====================================================

    profile = parse_document(
    raw_text,
    document_type
)

    profile_file = DYNAMIC_PROFILES / f"{name}_profile.json"

    with open(profile_file, "w", encoding="utf-8") as f:

        json.dump(
            profile,
            f,
            indent=4,
            ensure_ascii=False
        )

    # =====================================================
    # Clean Text
    # =====================================================

    cleaned = clean_text(raw_text)

    cleaned_file = DYNAMIC_CLEANED / f"{name}_cleaned.txt"

    cleaned_file.write_text(
        cleaned,
        encoding="utf-8"
    )

    # =====================================================
    # Chunking
    # =====================================================

    chunks = chunk_document(cleaned)

    current_page = 1

    for i, chunk in enumerate(chunks):

        if "<<PAGE" in chunk["text"]:

            match = re.search(
                r"<<PAGE\s+(\d+)>>",
                chunk["text"]
            )

            if match:
                current_page = int(match.group(1))

            chunk["text"] = re.sub(
                r"<<PAGE\s+\d+>>",
                "",
                chunk["text"]
            ).strip()

        chunk["chunk_id"] = f"{name}_{i+1}"

        chunk["law"] = name

        chunk["law_full_name"] = name

        chunk["section"] = f"Chunk {i+1}"

        chunk["chapter"] = ""

        chunk["title"] = ""

        chunk["page"] = current_page

        chunk["document_type"] = document_type

    chunk_file = DYNAMIC_CHUNKS / f"{name}_chunks.json"

    with open(chunk_file, "w", encoding="utf-8") as f:

        json.dump(
            chunks,
            f,
            indent=4,
            ensure_ascii=False
        )

    # =====================================================
    # Embeddings
    # =====================================================

    embedded = build_embeddings(chunks)

    embedding_file = DYNAMIC_EMBEDDINGS / f"{name}_embeddings.json"

    with open(embedding_file, "w", encoding="utf-8") as f:

        json.dump(
            embedded,
            f,
            indent=4,
            ensure_ascii=False
        )

    # =====================================================
    # ChromaDB
    # =====================================================

    create_collection(
        DYNAMIC_EMBEDDINGS,
        DYNAMIC_DB,
        "uploaded_document"
    )

    # =====================================================
    # Return
    # =====================================================

    return {

        "status": "success",

        "document": name,

        "document_type": document_type,

        "pages": len(pages),

        "chunks": len(chunks),

        "summary": profile.get("summary", ""),

        "profile": profile

    }


if __name__ == "__main__":

    while True:

        pdf = input("\nPDF Path : ")

        if pdf.lower() == "exit":
            break

        result = process_uploaded_pdf(pdf)

        print("\n")

        print(json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        ))