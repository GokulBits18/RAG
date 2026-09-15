# 🤖 LangGraph Local RAG Chatbot

A completely local, privacy-first Retrieval-Augmented Generation (RAG) application. This project allows users to upload PDF documents and ask questions about their content. It uses **LangGraph** for orchestration, **Streamlit** for the frontend, **FAISS** for vector retrieval, and **Ollama** for local LLM inference.

Because the models run locally, no data is sent to external APIs (like OpenAI or Anthropic), ensuring complete data privacy and zero API costs.

## 🌟 Features
* **Document Processing:** Upload and parse PDF documents directly through the UI.
* **Local Embeddings:** Uses HuggingFace's lightweight `all-MiniLM-L6-v2` model for fast document vectorization.
* **In-Memory Vector Store:** Leverages FAISS for rapid similarity search.
* **Agentic Workflow:** Built with LangGraph's state graph architecture, allowing for future expansion (like web fallback or document grading).
* **Local LLM:** Powered by `qwen3.5:4b` running via Ollama.
* **Source Transparency:** Displays the exact text chunks retrieved from the document used to generate the answer.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
1. **Python 3.9+** 
2. **Ollama:** Download and install from [ollama.com](https://ollama.com/).

Once Ollama is installed, open your terminal and pull the LLM model we are using:
```bash
ollama pull qwen3.5:4b
💻 Usage
Start the Ollama background server (if it isn't already running).

Open your terminal, ensure your virtual environment is active, and run the Streamlit app:

Bash
streamlit run app.py
Open the provided localhost URL in your web browser.

Upload a PDF using the sidebar and click Process Document.

Start chatting with your document!

🧩 Architecture (LangGraph Flow)
The application uses a simple LangGraph setup passing a RAGState dictionary:

START

Retrieve Node: Takes the user's question, embeds it, and queries the FAISS vector database for the top 3 most relevant document chunks.

Generate Node: Combines the user's question and the retrieved context chunks, sending them to the local Qwen model to formulate a grounded answer.

END

