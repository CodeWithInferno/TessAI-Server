# core/llm/embedding.py


from langchain_community.embeddings import HuggingFaceEmbeddings


# You can change the model to a smaller one if you want super fast speed
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder="server_data/embedding_cache"
)
