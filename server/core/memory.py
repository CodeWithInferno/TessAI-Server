import os
import re
from core.llm import llm, embedding
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Vector DB path
CHROMA_DIR = "server_data/rag_memory_ds"
CHROMA_PATH = os.path.join(CHROMA_DIR, "chroma.sqlite3")
os.makedirs(CHROMA_DIR, exist_ok=True)

# Initialize Chroma vector store
vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# RAG Prompt
rag_prompt = PromptTemplate.from_template("""You are Tess, a helpful terminal-based personal assistant.

Use the memory below to answer the user's question.

Memory:
{context}

User: {question}
Tess:""")

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": rag_prompt}
)

# Memory summarizer prompt
# new schema prompt
memory_prompt = PromptTemplate.from_template("""
You are a Memory Assistant.  Extract every enduring fact from the user’s message and output as a JSON array of objects.  
Each object must have:
- “category”: one of [“name”, “project”, “preference”, “relationship”, “achievement”, “alias”, “other”]
- “detail”: a short human-readable sentence stating the fact.

Output ONLY the JSON array.  
If there are no storable facts, output exactly: []
  
Input:
\"\"\"{message}\"\"\"

Output:
""")



summarizer = memory_prompt | llm


def strip_think_blocks(text: str) -> str:
    """Remove all <think>...</think> blocks (non-greedy)."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def summarize_and_store_if_needed(message: str):
    # Step 1: Remove <think> from original message
    clean_input = strip_think_blocks(message)

    # Step 2: Summarize cleaned message
    raw_summary = summarizer.invoke({"message": clean_input}).strip()

    # Step 3: Remove <think> from summary too
    summary = strip_think_blocks(raw_summary).strip()

    # Step 4: Skip bad summaries
    if summary.upper() == "SKIP" or len(summary.split()) < 5:
        print("⏭️ SKIP detected, not storing.")
        return

    # Step 5: Heuristically reject junk responses
    skip_keywords = [
        "you are asking", 
        "the user is asking", 
        "your name is", 
        "you said", 
        "the assistant is", 
        "Tess is", 
        "message contains information about the assistant", 
        "your personal assistant"
    ]
    if any(kw.lower() in summary.lower() for kw in skip_keywords):
        print("🧹 Filtered: Low-value or generic memory detected.")
        return

    # Step 6: Store
    print(f"💾 Storing to memory: {summary}")
    vectorstore.add_texts([summary])

