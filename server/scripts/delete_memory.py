import os
from langchain_chroma import Chroma

# Dummy embedding function (same as used when saving)
class DummyEmbedding:
    def embed_documents(self, texts):
        return [[0.0] * 1536 for _ in texts]
    def embed_query(self, text):
        return [0.0] * 1536

embedding = DummyEmbedding()

CHROMA_DIR = "C:/Users/prpatel/Documents/Programming/TessAI/TessAI/server/server_data/rag_memory_ds"

if not os.path.exists(CHROMA_DIR):
    print(f"❌ Memory directory not found at {CHROMA_DIR}")
    exit()

try:
    vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)

    # Get all document IDs
    ids = vectorstore.get()["ids"]

    if not ids:
        print("📭 No documents found to delete.")
    else:
        print(f"🗑️ Deleting {len(ids)} memory entries...")
        vectorstore.delete(ids=ids)
        print("✅ Memory deleted successfully.")

except Exception as e:
    print("❌ Error during deletion:", e)
