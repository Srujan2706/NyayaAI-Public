from pathlib import Path
import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from backend.pipeline.upload_pipeline import process_uploaded_pdf
from backend.retrieval.hybrid import hybrid_search
from backend.llm.ollama import generate_answer

from backend.routing.query_classifier import classify_query
from backend.routing.profile_router import answer_from_profile
from backend.routing.general_router import answer_general_query


app = FastAPI(
    title="NyayaAI",
    version="1.0.0"
)


# ==========================================================
# Request Model
# ==========================================================

class QueryRequest(BaseModel):
    question: str
    mode: str = "dynamic"


# ==========================================================
# Home
# ==========================================================

@app.get("/")
def home():

    return {
        "message": "NyayaAI Backend Running"
    }


# ==========================================================
# Upload PDF
# ==========================================================

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):

        return {
            "status": "error",
            "message": "Only PDF files are supported."
        }

    with tempfile.TemporaryDirectory() as temp_dir:

        pdf_path = Path(temp_dir) / file.filename

        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = process_uploaded_pdf(str(pdf_path))

    return result


# ==========================================================
# Ask Question
# ==========================================================

@app.post("/ask")
def ask(request: QueryRequest):

    print("\n" + "=" * 80)
    print("MODE     :", request.mode)
    print("QUESTION :", request.question)
    print("=" * 80)

    # ======================================================
    # General Conversation Router
    # ======================================================

    general_answer = answer_general_query(request.question)

    if general_answer:

        print("✓ Answered from General Router")

        return {
            "question": request.question,
            "answer": general_answer,
            "sources": []
        }

    # ======================================================
    # Intent Classification
    # ======================================================

    intent = classify_query(request.question)

    print("Intent :", intent)

    # ======================================================
    # Uploaded Document Profile Router
    # ======================================================

    if request.mode == "dynamic":

        profile_answer = answer_from_profile(intent)

        if profile_answer:

            print("✓ Answered from Document Profile")

            return {
                "question": request.question,
                "answer": profile_answer,
                "sources": []
            }

    # ======================================================
    # Hybrid Retrieval
    # ======================================================

    retrieved_docs = hybrid_search(
        query=request.question,
        mode=request.mode
    )

    print("\n================ RETRIEVED DOCUMENTS ================\n")

    for i, item in enumerate(retrieved_docs, 1):

        print(f"Result {i}")

        print(item["metadata"])

        print(item["document"][:300])

        print("-" * 60)

    print(f"\nRetrieved {len(retrieved_docs)} documents\n")

    if not retrieved_docs:

        return {
            "question": request.question,
            "answer": (
                "I could not find sufficient information in the available "
                "legal documents to answer your question."
            ),
            "sources": []
        }

    # ======================================================
    # Generate Answer
    # ======================================================

    try:

        answer = generate_answer(
            request.question,
            retrieved_docs
        )

    except Exception as e:

        print("\nLLM ERROR")
        print(e)

        return {
            "question": request.question,
            "answer": (
                "An internal error occurred while generating the answer. "
                "Please try again."
            ),
            "sources": []
        }

    # ======================================================
    # Build Explainability
    # ======================================================

    sources = []

    seen = set()

    for item in retrieved_docs:

        meta = item["metadata"]

        key = (
            meta.get("law"),
            meta.get("section")
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append({

            "law": meta.get("law"),

            "section": meta.get("section"),

            "chapter": meta.get("chapter"),

            "title": meta.get("title"),

            "page": meta.get("page", "-"),

            "score": round(item.get("score", 0), 3),

            "context": item["document"][:700]

        })

    print("✓ Answer Generated")
    print("=" * 80)

    return {

        "question": request.question,

        "answer": answer,

        "sources": sources

    }