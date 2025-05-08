# core/memory/semantic_memory.py

import os
import re
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from core.llm import llm
from core.embedding import embedding

# Setup paths
CHROMA_DIR = "server_data/rag_memory_ds"
os.makedirs(CHROMA_DIR, exist_ok=True)

# Initialize ChromaDB
vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# RAG Prompt for Retrieval
rag_prompt = PromptTemplate.from_template("""
You are Tess, a helpful personal assistant.

Use the following memory to answer the user's question:

Memory:
{context}

User: {question}
Tess:""")

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": rag_prompt}
)

# Memory Summarizer Prompt (to extract facts)
memory_prompt = PromptTemplate.from_template("""
You are a Memory Assistant. Extract enduring facts from the user's message and output them as a JSON array of objects.
Each object must have:
- "category": one of ["name", "project", "preference", "relationship", "achievement", "alias", "other"]
- "detail": a short human-readable sentence stating the fact.

If no storable facts, output exactly: []

Input:
\"\"\"{message}\"\"\"

Output:
""")

summarizer = memory_prompt | llm

# === Helper Functions ===

def strip_think_blocks(text: str) -> str:
    """Remove all <think>...</think> blocks."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def save_to_semantic_memory(text: str):
    """Save a clean text into ChromaDB."""
    vectorstore.add_texts([text])
    # vectorstore.persist()
    print(f"💾 [Semantic Memory Saved] {text}")

def summarize_and_store_if_needed(message: str):
    """Extract and store important memories if needed."""
    clean_input = strip_think_blocks(message)
    raw_summary = summarizer.invoke({"message": clean_input}).strip()
    summary = strip_think_blocks(raw_summary).strip()

    # Skip bad summaries
    if summary.strip() in ["[]", "SKIP", ""]:
        print("⏭️ No important memory to store.")
        return

    # Heuristic filters for junk outputs
    skip_keywords = [
        "assistant", "you said", "user asked", "Tess is", 
        "message contains information about the assistant"
    ]
    if any(kw.lower() in summary.lower() for kw in skip_keywords):
        print("🧹 Filtered: Low-value or generic memory detected.")
        return

    # Store valid memory
    save_to_semantic_memory(summary)

def search_semantic_memory(query: str):
    """Search ChromaDB for related memories."""
    results = retriever.get_relevant_documents(query)
    return [r.page_content for r in results]
