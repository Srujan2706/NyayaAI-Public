import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from rank_bm25 import BM25Okapi

from backend.utils.config import PERMANENT_CHUNKS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKENIZER_REGEX = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+[A-Za-z]?|[IVXLCDM]+|[()]|[,.;:]", re.IGNORECASE)

_documents: List[Dict[str, Any]] = []
_bm25_model: Optional[BM25Okapi] = None


def tokenize(text: str) -> List[str]:
    if not text:
        return []
    return TOKENIZER_REGEX.findall(str(text).lower())


def load_documents() -> None:
    global _documents, _bm25_model
    logger.info(f"Loading documents from {PERMANENT_CHUNKS}")
    
    _documents = []
    filepaths = sorted(Path(PERMANENT_CHUNKS).glob("*_chunks.json"))
    
    if not filepaths:
        logger.warning(f"No chunk files found in {PERMANENT_CHUNKS}")
        return

    corpus_tokens = []
    
    for filepath in filepaths:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
                for chunk in chunks:
                    _documents.append(chunk)
                    
                    search_text_parts = [
                        str(chunk.get("law", "")),
                        str(chunk.get("law_full_name", "")),
                        str(chunk.get("part", "")),
                        str(chunk.get("chapter", "")),
                        str(chunk.get("chapter_title", "")),
                        str(chunk.get("section", "")),
                        str(chunk.get("title", "")),
                        str(chunk.get("text", ""))
                    ]
                    
                    combined_text = " ".join(part for part in search_text_parts if part.strip())
                    corpus_tokens.append(tokenize(combined_text))
        except Exception as e:
            logger.error(f"Failed to load {filepath}: {e}")

    if corpus_tokens:
        logger.info(f"Loaded {len(_documents)} documents. Initializing BM25...")
        _bm25_model = BM25Okapi(corpus_tokens)
        logger.info("BM25 initialization complete.")
    else:
        logger.warning("No documents successfully parsed. BM25 model not initialized.")


def bm25_search(query: str, k: int = 10) -> List[Dict[str, Any]]:
    if not _documents or _bm25_model is None:
        logger.info("BM25 index not loaded. Loading now...")
        load_documents()
        
    if not _documents or _bm25_model is None:
        return []

    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    scores = _bm25_model.get_scores(query_tokens)
    
    results = []
    for idx, score in enumerate(scores):
        if score > 0.0:
            results.append({
                "document": _documents[idx].get("text", ""),
                "metadata": _documents[idx],
                "score": float(score)
            })
            
    results.sort(
        key=lambda x: (x["score"], x["metadata"].get("token_count", 0)),
        reverse=True
    )
    return results[:k]


def keyword_search(query: str, k: int = 10) -> List[Dict[str, Any]]:
    return bm25_search(query, k)


if __name__ == "__main__":
    import sys
    
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "penalty for theft"
    
    print(f"\n{'-'*50}")
    print(f"Testing BM25 Search Engine")
    print(f"Query: '{query}'")
    print(f"{'-'*50}\n")
    
    results = bm25_search(query, k=5)
    
    if not results:
        print("No results found or index is empty.")
    else:
        print(f"Found {len(results)} relevant results:\n")
        for i, res in enumerate(results, 1):
            meta = res['metadata']
            law = meta.get('law', 'Unknown')
            section = meta.get('section', meta.get('article', 'N/A'))
            title = meta.get('title', 'No Title')
            preview = str(res['document'])[:150].replace('\n', ' ')
            
            print("=" * 70)
            print(f"Result {i}")
            print(f"Score   : {res['score']:.4f}")
            print(f"Law     : {law}")
            print(f"Section : {section}")
            print(f"Title   : {title}")
            print()
            print(preview)
            print()