import streamlit as st
import tempfile
import os
from typing import TypedDict, List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# -- New LangGraph Imports --
from langgraph.graph import StateGraph, START, END

# ==========================================
# 1. DEFINE THE GRAPH STATE
# ==========================================
class RAGState(TypedDict):
    """The state of our graph that passes between nodes."""
    question: str
    context: List[Document]
    answer: str

# -- Page Configuration --
st.set_page_config(page_title="LangGraph Local RAG", page_icon="🤖")
st.title("🤖 LangGraph Local RAG Chatbot")

# -- Initialize Session State --
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

# -- Sidebar: Document Upload and Processing --
with st.sidebar:
    st.header("1. Upload Knowledge Base")
    uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
    
    if st.button("Process Document") and uploaded_file:
        with st.spinner("Processing document..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            loader = PyPDFLoader(tmp_path)
            docs = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vector_store = FAISS.from_documents(splits, embeddings)
            st.session_state.vector_store = vector_store
            
            os.remove(tmp_path)
            st.success("Document successfully indexed!")

# ==========================================
# 2. DEFINE THE GRAPH NODES
# ==========================================
def retrieve_node(state: RAGState):
    """Retrieves relevant documents from FAISS based on the question."""
    retriever = st.session_state.vector_store.as_retriever(search_kwargs={"k": 3})
    documents = retriever.invoke(state["question"])
    return {"context": documents} # Updates the 'context' key in the state

def generate_node(state: RAGState):
    """Generates an answer using the local LLM and the retrieved context."""
    #llm = ChatOllama(model="qwen3.5:4b", temperature=0, num_gpu=0)
    llm = ChatOllama(model="qwen3.5:4b", temperature=0, num_ctx=2048)
    
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you don't know. "
        "Use three sentences maximum and keep the answer concise.\n\n"
        "Context: {context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}"),
    ])
    
    # Format the context documents into a single string
    context_text = "\n\n".join([doc.page_content for doc in state["context"]])
    
    # Create a simple runnable sequence
    chain = prompt | llm
    response = chain.invoke({"question": state["question"], "context": context_text})
    
    return {"answer": response.content} # Updates the 'answer' key in the state

# ==========================================
# 3. BUILD AND COMPILE THE GRAPH
# ==========================================
workflow = StateGraph(RAGState)

# Add our nodes to the graph
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

# Define the flow: START -> retrieve -> generate -> END
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Compile it into an executable app
rag_app = workflow.compile()

# -- Main Chat Interface --
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your document..."):
    if st.session_state.vector_store is None:
        st.error("Please upload and process a document first.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Navigating LangGraph..."):
                # Run the LangGraph application
                inputs = {"question": prompt}
                final_state = rag_app.invoke(inputs)
                
                answer = final_state["answer"]
                st.markdown(answer)
                
                with st.expander("View Source Context"):
                    for i, doc in enumerate(final_state["context"]):
                        st.write(f"**Chunk {i+1}:**")
                        st.write(doc.page_content)
        
        st.session_state.messages.append({"role": "assistant", "content": answer})