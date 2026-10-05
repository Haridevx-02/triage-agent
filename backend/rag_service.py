import json
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_PATH = BASE_DIR / "knowledge_base" / "insurance_knowledge.json"


@lru_cache(maxsize=1)
def get_knowledge_documents() -> List[Dict[str, str]]:
    """Load the local insurance knowledge base used for retrieval."""
    if not KNOWLEDGE_PATH.exists():
        return []

    with KNOWLEDGE_PATH.open("r", encoding="utf-8") as handle:
        raw_documents = json.load(handle)

    documents = []
    for item in raw_documents:
        if not isinstance(item, dict):
            continue
        documents.append({
            "title": str(item.get("title", "Knowledge Item")),
            "tags": " ".join(str(tag) for tag in item.get("tags", [])),
            "content": str(item.get("content", "")),
        })

    return documents


@lru_cache(maxsize=1)
def build_retriever():
    """Create a lightweight TF-IDF retriever over the knowledge base."""
    documents = get_knowledge_documents()
    if not documents:
        return None, None, []

    texts = [
        f"{doc['title']} {doc['tags']} {doc['content']}"
        for doc in documents
    ]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix, documents


def retrieve_knowledge(query: str, top_k: int = 3) -> List[str]:
    """Return the most relevant knowledge snippets for the query."""
    query = (query or "").strip()
    if not query:
        return []

    vectorizer, matrix, documents = build_retriever()
    if vectorizer is None or matrix is None or not documents:
        return []

    transformed_query = vectorizer.transform([query])
    similarities = cosine_similarity(transformed_query, matrix).flatten()
    top_indexes = similarities.argsort()[-top_k:][::-1]

    matches = []
    for index in top_indexes:
        score = float(similarities[index])
        if score <= 0:
            continue
        matches.append(f"{documents[index]['title']}: {documents[index]['content']}")

    return matches


def build_rag_context(query: str, member_context: Optional[str] = None, top_k: int = 3) -> str:
    """Build a retrieval-augmented context block for prompt injection."""
    matches = retrieve_knowledge(query, top_k=top_k)
    if not matches:
        return ""

    rag_block = "RELEVANT KNOWLEDGE BASE:\n" + "\n\n".join(f"- {m}" for m in matches)
    if member_context:
        return f"{member_context}\n\n{rag_block}"
    return rag_block
