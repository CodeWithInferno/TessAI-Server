# core/memory/extraction.py

import os
import re
import json
from core.memory.semantic_memory import save_to_semantic_memory
from core.memory.structured_memory import insert_fact
from core.llm import llm
from langchain.prompts import PromptTemplate


# ==== Memory Summarizer Prompt ====

memory_prompt = PromptTemplate.from_template("""
You are a memory extractor assistant. You must ONLY reply with a JSON array of memory facts.

Each fact must have:
- "category": one of ["name", "project", "preference", "relationship", "achievement", "alias", "other"]
- "detail": a short, human-readable sentence stating the fact.

❗ DO NOT add any commentary.
❗ DO NOT say anything outside the JSON array.
❗ Output only a clean valid JSON array.

Input:
\"\"\"{message}\"\"\"

Output:
""")

summarizer = memory_prompt | llm

# ==== Helpers ====

def strip_think_blocks(text: str) -> str:
    """Remove <think>...</think> blocks."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def clean_json_output(text: str) -> str:
    """Remove ```json ... ``` wrappers if present."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text

# ==== Main memory extraction ====

def summarize_and_store_if_needed(message: str):
    """Extract facts and store in structured or semantic memory."""
    clean_input = strip_think_blocks(message)
    raw_summary = summarizer.invoke({"message": clean_input}).strip()

    summary_text = clean_json_output(strip_think_blocks(raw_summary))

    # If nothing meaningful
    if summary_text.strip() == "[]" or summary_text.strip() == "":
        print("⏭️ No storable memories found.")
        return

    try:
        facts = json.loads(summary_text)
        if not isinstance(facts, list):
            print(f"⚠️ Invalid summary format: {summary_text}")
            return
    except Exception as e:
        print(f"⚠️ Error parsing JSON summary: {summary_text}")
        return

    # Process extracted facts
    for fact in facts:
        category = fact.get("category", "").lower()
        detail = fact.get("detail", "").strip()

        if not category or not detail:
            continue  # Skip bad entries

        if category in ["name", "project", "preference", "relationship", "achievement", "alias"]:
            print(f"📚 [Structured Memory] Saving: {category} → {detail}")
            insert_fact(category, detail)
        elif category == "other":
            print(f"🧠 [Semantic Memory] Saving: {detail}")
            save_to_semantic_memory(detail)
        else:
            print(f"⚠️ Unknown category: {category}, saving to semantic by default.")
            save_to_semantic_memory(detail)
