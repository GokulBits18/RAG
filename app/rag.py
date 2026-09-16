"""
Core RAG logic: embeddings, vector store (Chroma), retrieval, and generation
via a local Ollama server.
"""

import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer

from .ingest import build_chunks

CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
COLLECTION_NAME = "docs"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:latest")

_embed_model = None
_chroma_client = None
_collection = None


def get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model


def get_collection():
    global _chroma_client, _collection
    if _collection is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = _chroma_client.get_or_create_collection(COLLECTION_NAME)
    return _collection


def index_documents(force: bool = False) -> int:
    """
    Build chunks from data/ and embed+store any that aren't already indexed.
    Returns the number of chunks newly added.
    """
    collection = get_collection()

    if force:
        existing_ids = collection.get()["ids"]
        if existing_ids:
            collection.delete(ids=existing_ids)

    chunks = build_chunks()
    if not chunks:
        return 0

    existing_ids = set(collection.get()["ids"])
    new_chunks = [c for c in chunks if c["id"] not in existing_ids]
    if not new_chunks:
        return 0

    model = get_embed_model()
    texts = [c["text"] for c in new_chunks]
    embeddings = model.encode(texts, show_progress_bar=False).tolist()

    collection.add(
        ids=[c["id"] for c in new_chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"source": c["source"]} for c in new_chunks],
    )
    return len(new_chunks)


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Embed the query and return the top_k most relevant chunks."""
    collection = get_collection()
    model = get_embed_model()
    query_embedding = model.encode([query]).tolist()

    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({"text": doc, "source": meta.get("source", "unknown"), "distance": dist})
    return hits


def build_prompt(query: str, context_chunks: list[dict]) -> str:
    context_block = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in context_chunks
    )
    return (
        "You are a helpful assistant that answers questions using ONLY the "
        "context provided below. If the answer isn't in the context, say you "
        "don't know rather than guessing.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )


def generate_answer(query: str, context_chunks: list[dict]) -> str:
    """Call the local Ollama server to generate an answer grounded in context."""
    prompt = build_prompt(query, context_chunks)
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def answer_question(query: str, top_k: int = 3) -> dict:
    """Full pipeline: retrieve + generate. Returns answer and sources used."""
    hits = retrieve(query, top_k=top_k)
    if not hits:
        return {"answer": "No documents are indexed yet. Add files to data/ and re-index.", "sources": []}
    answer = generate_answer(query, hits)
    return {
        "answer": answer,
        "sources": [{"source": h["source"], "excerpt": h["text"][:200]} for h in hits],
    }
