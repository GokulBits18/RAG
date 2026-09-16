"""
Data ingestion + preprocessing + chunking.

Loads .txt, .md and .pdf files from the data/ folder, cleans them up,
and splits them into overlapping chunks ready for embedding.
"""

import os
import re
from pathlib import Path
from pypdf import PdfReader

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_documents(data_dir: Path = DATA_DIR) -> list[dict]:
    """Load all supported files from data_dir. Returns list of {source, text}."""
    docs = []
    for path in sorted(data_dir.glob("**/*")):
        if path.is_dir():
            continue
        if path.suffix.lower() in (".txt", ".md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            docs.append({"source": path.name, "text": text})
        elif path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            docs.append({"source": path.name, "text": text})
    return docs


def clean_text(text: str) -> str:
    """Basic cleanup: collapse whitespace, strip odd control chars."""
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """
    Split text into overlapping character-based chunks.
    Tries to break on paragraph/sentence boundaries where possible.
    """
    text = clean_text(text)
    if len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # try to break at a paragraph or sentence boundary near `end`
            boundary = text.rfind("\n\n", start, end)
            if boundary == -1 or boundary <= start:
                boundary = text.rfind(". ", start, end)
            if boundary != -1 and boundary > start:
                end = boundary + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(end - overlap, start + 1)
    return chunks


def build_chunks(data_dir: Path = DATA_DIR, chunk_size: int = 800, overlap: int = 120) -> list[dict]:
    """
    Full ingestion pipeline: load documents, clean, chunk.
    Returns list of {id, text, source} ready for embedding.
    """
    docs = load_documents(data_dir)
    all_chunks = []
    for doc in docs:
        pieces = chunk_text(doc["text"], chunk_size, overlap)
        for i, piece in enumerate(pieces):
            all_chunks.append({
                "id": f"{doc['source']}::chunk_{i}",
                "text": piece,
                "source": doc["source"],
            })
    return all_chunks


if __name__ == "__main__":
    chunks = build_chunks()
    print(f"Loaded {len(chunks)} chunks from {DATA_DIR}")
    for c in chunks[:3]:
        print("---")
        print(c["id"], "-", c["text"][:150], "...")
