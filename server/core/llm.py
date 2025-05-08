from langchain_ollama import OllamaLLM, OllamaEmbeddings
from .config import LLM_MODEL

llm = OllamaLLM(model=LLM_MODEL)
embedding = OllamaEmbeddings(model=LLM_MODEL)
