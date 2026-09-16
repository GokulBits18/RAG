<<<<<<< HEAD
"""
Streamlit chat interface for the local RAG chatbot.

Run with:
    streamlit run streamlit_app.py
"""

import streamlit as st
from app.rag import index_documents, answer_question, OLLAMA_MODEL

st.set_page_config(page_title="Local RAG Chatbot", page_icon="📚")

st.title("📚 Local RAG Chatbot")
st.caption(f"Running fully local — embeddings on CPU, generation via Ollama (`{OLLAMA_MODEL}`)")

# Index documents once per session (cheap no-op if already indexed)
if "indexed" not in st.session_state:
    with st.spinner("Indexing documents from data/ ..."):
        added = index_documents()
    st.session_state.indexed = True
    if added:
        st.toast(f"Indexed {added} new chunk(s).")

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Chunks to retrieve", min_value=1, max_value=6, value=3)

    if st.button("🔄 Re-index documents"):
        with st.spinner("Re-indexing..."):
            added = index_documents()
        st.success(f"Indexed {added} new chunk(s).")

    if st.button("🗑️ Rebuild index from scratch"):
        with st.spinner("Rebuilding index..."):
            added = index_documents(force=True)
        st.success(f"Rebuilt index with {added} chunk(s).")

    st.markdown("---")
    st.caption("Drop `.txt`, `.md`, or `.pdf` files into the `data/` folder, "
               "then click Re-index.")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for s in msg["sources"]:
                    st.markdown(f"**{s['source']}**")
                    st.caption(s["excerpt"])

# Chat input
if question := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking... (local model, may take a moment)"):
            try:
                result = answer_question(question, top_k=top_k)
                st.write(result["answer"])
                if result["sources"]:
                    with st.expander("Sources"):
                        for s in result["sources"]:
                            st.markdown(f"**{s['source']}**")
                            st.caption(s["excerpt"])
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                })
            except Exception as e:
                error_msg = f"Error: {e}\n\nIs Ollama running? Try `ollama serve` in a terminal."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
=======
""" g """
>>>>>>> d4cb099f8578e30acf82c2661e0f200050a91095
