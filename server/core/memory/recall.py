# core/memory/recall.py

from core.memory.structured_memory import get_all_facts
from core.memory.semantic_memory import retriever

def fetch_structured_facts():
    """Fetch structured facts (name, project, preferences) from SQLite."""
    try:
        facts = get_all_facts()
        fact_strings = []
        for category, detail in facts:
            if category in ["name", "project", "preference", "relationship", "achievement", "alias"]:
                fact_strings.append(f"{detail}")
        return fact_strings
    except Exception as e:
        print(f"⚠️ Error fetching structured facts: {e}")
        return []

def fetch_recent_semantic_memories(query="about me", k=5):
    """Fetch recent/open-ended memories from ChromaDB."""
    try:
        docs = retriever.get_relevant_documents(query)
        return [doc.page_content for doc in docs][:k]
    except Exception as e:
        print(f"⚠️ Error fetching semantic memories: {e}")
        return []

def generate_memory_summary():
    """Combine structured facts + semantic memories into a preloadable text."""
    structured_facts = fetch_structured_facts()
    semantic_memories = fetch_recent_semantic_memories()

    memory_summary = ""

    if structured_facts:
        memory_summary += "**Known Facts:**\n" + "\n".join(f"- {fact}" for fact in structured_facts) + "\n\n"

    if semantic_memories:
        memory_summary += "**Past Memories:**\n" + "\n".join(f"- {memory}" for memory in semantic_memories)

    return memory_summary.strip()
