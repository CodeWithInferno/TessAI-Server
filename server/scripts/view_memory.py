import os
from langchain_chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings  # ✅ updated

CHROMA_DIR = "C:/Users/prpatel/Documents/Programming/TessAI/TessAI/server/server_data/rag_memory_ds"  # ✅ fixed path

# Dummy embedder if you’re not using real embeddings
class DummyEmbedding:
    def embed_documents(self, texts):
        return [[0.0] * 1536 for _ in texts]
    def embed_query(self, text):
        return [0.0] * 1536

embedding = DummyEmbedding()

if not os.path.exists(CHROMA_DIR):
    print(f"❌ Memory directory not found at {CHROMA_DIR}")
    exit()

try:
    vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)
    results = vectorstore.get()
    docs = results.get("documents", [])

    if not docs:
        print("📭 No documents stored.")
    else:
        print(f"🧠 Memory contents from {CHROMA_DIR}:/n")
        for i, doc in enumerate(docs, 1):
            print(f"{i}. {doc}")
            print("-" * 40)

except Exception as e:
    print("❌ Failed to load memory:", e)
