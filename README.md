<<<<<<< HEAD
# Local RAG Chatbot

A fully local Retrieval-Augmented Generation (RAG) chatbot. No API keys, no
cloud calls — embeddings run on your CPU and generation runs through a local
[Ollama](https://ollama.com) model. Chat UI built with Streamlit.

## Architecture

```
 data/*.md,*.txt,*.pdf
        │
        ▼
 [1] Ingestion  (app/ingest.py)   — load files
        │
        ▼
 [2] Preprocessing                — clean whitespace/control chars
        │
        ▼
 [3] Chunking                     — overlapping ~800-char chunks
        │
        ▼
 [4] Embeddings  (app/rag.py)     — sentence-transformers (all-MiniLM-L6-v2)
        │
        ▼
 [5] Vector Store                 — ChromaDB (persisted to ./chroma_db)
        │
        ▼
 [6] Retrieval    ◄── user query embedded, top-k similarity search
        │
        ▼
 [7] Generation                   — prompt + context sent to local Ollama model
        │
        ▼
 [8] Chat Interface  (streamlit_app.py) — Streamlit chat UI
```

**Stack**
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (runs on CPU, ~80MB)
- Vector store: ChromaDB (local, file-based, no server to run)
- LLM: Ollama, default model `gemma3:4b`
- Interface: Streamlit

## Prerequisites

1. **Python 3.10+**
2. **[Ollama](https://ollama.com/download)** installed and running locally
3. Pull the model once:
   ```bash
   ollama pull gemma3:4b
   ```
   (Any Ollama model works — see [Changing the model](#changing-the-model) below.)

## Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd rag-chatbot

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

## Environment Variables

None are required by default. Optional overrides:

| Variable       | Default                  | Purpose                          |
|----------------|---------------------------|-----------------------------------|
| `OLLAMA_HOST`  | `http://localhost:11434`  | URL of your Ollama server         |
| `OLLAMA_MODEL` | `gemma3:4b`                | Which local model to use for generation |

Set them before running, e.g. on Windows:
```bash
set OLLAMA_MODEL=llama3.2:3b
```

## Adding Your Own Documents

Drop `.txt`, `.md`, or `.pdf` files into the `data/` folder. A sample
`data/sample_knowledge.md` (a mock company handbook) is included so the
project runs out of the box.

Documents are indexed automatically the first time the app runs. After
adding new files, click **"🔄 Re-index documents"** in the sidebar — no
restart needed.

## Running

Make sure Ollama is running in the background (it usually starts automatically
after install; otherwise run `ollama serve`).

```bash
streamlit run streamlit_app.py
```

This opens the chat UI in your browser (usually `http://localhost:8501`).

## Usage

Type a question in the chat box. The app retrieves the most relevant chunks
from your documents, sends them to the local model as context, and shows the
answer along with an expandable **Sources** section citing which document(s)
it used.

Sidebar controls:
- **Chunks to retrieve** — how many context chunks to pull per question
- **Re-index documents** — pick up newly added files
- **Rebuild index from scratch** — wipe and re-embed everything

## Example Questions to Test

Using the included sample handbook:
1. "What are the standard working hours?"
2. "How many remote work days are allowed per week?"
3. "What happens if I take more than 3 days of sick leave?"
4. "Can unused leave be carried over to next year?"
5. "What is the capital of France?" — *(out-of-scope question; the bot should say it doesn't know rather than guessing, since this isn't in the knowledge base)*

## Changing the Model

Any Ollama-supported model works. Pull it and set `OLLAMA_MODEL`:
```bash
ollama pull llama3.2:3b
set OLLAMA_MODEL=llama3.2:3b   # Windows
```
Smaller models (1B–4B params) are recommended on machines with limited RAM.

## Project Structure

```
rag-chatbot/
├── app/
│   ├── ingest.py       # document loading, cleaning, chunking
│   └── rag.py          # embeddings, vector store, retrieval, generation
├── data/               # your knowledge source documents
├── chroma_db/          # persisted vector store (auto-created, gitignored)
├── streamlit_app.py    # Streamlit chat UI
├── requirements.txt
└── README.md
```

## Notes

- No API keys or secrets are used anywhere in this project — everything runs
  locally through Ollama.
- The vector store (`chroma_db/`) is gitignored since it's regenerated from
  `data/` automatically on first run.
=======
#
>>>>>>> d4cb099f8578e30acf82c2661e0f200050a91095
