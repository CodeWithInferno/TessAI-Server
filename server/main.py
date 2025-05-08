# server/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import sqlite3
import uvicorn
from fastapi import FastAPI, UploadFile, Form
import json

from agents.collected_memory_agent import CollectedMemoryAgent
from core import llm
from core.filesystem_manager import FileMemory, FileEntry
from core.file_resolver import resolve_file_path
from core.matcher import smart_find_filesystem
from core.memory.semantic_memory import rag_chain
from core.memory.extraction import summarize_and_store_if_needed
from langchain.prompts import PromptTemplate
from core.memory.structured_memory import create_structured_table
from core.memory.recall import generate_memory_summary
from agents.scheduler_agent.agent import handle_schedule_input
from agents.scheduler_agent.logic import get_agenda_for_day





collected_memory_agent = CollectedMemoryAgent()
app = FastAPI()
create_structured_table()



UPLOAD_DIR = "./uploaded_dbs"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-db")
async def upload_db(device_id: str = Form(...), file: UploadFile = None):
    if file is None:
        return {"error": "No file uploaded."}

    save_path = os.path.join(UPLOAD_DIR, f"{device_id}.db")
    
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"message": f"✅ Database uploaded successfully for {device_id}"}

DEVICE_DB_DIR = os.path.join("server_data", "Device_Data")
os.makedirs(DEVICE_DB_DIR, exist_ok=True)

memory_summary = generate_memory_summary()
print("[Memory Recall]:", memory_summary)
# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==== UPLOAD FILES ====
@app.post("/upload-files")
async def upload_files(files: List[FileEntry]):
    if not files:
        return {"error": "❌ No files received."}

    device_id = files[0].device_id
    save_path = os.path.join("server_data", "Device_Data", f"{device_id}.db")

    with sqlite3.connect(db_file_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT,
                name TEXT,
                is_dir BOOLEAN,
                extension TEXT,
                size INTEGER
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_path ON files(path)')
        cursor.executemany('''
            INSERT INTO files (path, name, is_dir, extension, size)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            (file.path, file.name, file.is_dir, file.extension, file.size)
            for file in files
        ])
        conn.commit()

    return {"message": f"✅ Stored {len(files)} entries for {device_id}."}


# ==== KEYWORD CLASSIFIER ====
def classify_query_type(query: str) -> str:
    q = query.lower()

    # Explicit calendar checks (must be BEFORE "schedule")
    calendar_check_keywords = [
        "what is my schedule", "do i have", "what's my day", "any meetings",
        "am i free", "is there anything", "agenda", "calendar", "what is my calendar", "free tomorrow", "busy"
    ]
    if any(kw in q for kw in calendar_check_keywords):
        return "calendar_check"

    # Shell/terminal/file commands
    command_keywords = [
        "run", "open", "launch", "start", "execute", "kill",
        "find", "search", "shutdown", "restart", "install",
        "delete", "remove", "close", "list", "show"
    ]
    if any(kw in q for kw in command_keywords):
        return "command"

    # Schedule/plan/add events
    schedule_keywords = [
        "remind", "schedule", "set", "make", "create", "plan", "book a meeting", "add"
    ]
    if any(kw in q for kw in schedule_keywords):
        return "schedule"

    return "chat"




# ==== PROMPTS ====
CHAT_PROMPT = PromptTemplate.from_template("""
You are Tess, a helpful terminal-based personal assistant.
Respond like a human assistant, be helpful and concise.

User: {query}
Tess:
""")

PLAN_PROMPT = PromptTemplate.from_template("""
You are Tess, an AI terminal assistant.

Device ID: "{device_id}"
User said: "{query}"
Resolved file path (if available): "{path}"

<think>
Generate ONLY a VALID JSON object with double quotes, NO explanations, NO extra text.
The JSON must have only a "run" key with the terminal command as value.
</think>

ONLY output:

{{"run": "command to execute"}}
""")





# ==== CHAT ENDPOINT ====
class Query(BaseModel):
    query: str
    device_id: str

@app.post("/chat")
async def chat(req: Query):
    try:
        intent = classify_query_type(req.query)
        print(f"[TESS] Device={req.device_id}, Intent={intent}, Query={req.query}")

        if intent == "command":
            matches = smart_find_filesystem(req.query, req.device_id, intent="any")
            print(f"[🔍 Smart matches] {matches}")

            if matches:
                top_match = matches[0]
                file_path = top_match["path"]

                if file_path.endswith(".app"):
                    command = f'open "{file_path}"'
                else:
                    command = f'open "{file_path}"'

                return {
                    "response": {"run": command},
                    "intent": intent
                }
            else:
                return {
                    "response": {"error": "no_file_found"},
                    "intent": intent
                }
        elif intent == "schedule":
            response = handle_schedule_input(req.query)
            return {"response": response, "intent": "schedule"}
        elif intent == "calendar_check":
            try:
                print(f"[🗓️ Calendar] Getting agenda for 'tomorrow'")
                response = get_agenda_for_day("tomorrow")
                return {"response": response, "intent": "calendar_check"}
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {"response": f"❌ Failed to get agenda: {str(e)}", "intent": "calendar_check"}

        
        elif intent == "chat":
            memory_summary = generate_memory_summary()
            memory_boost = f"Here’s what I know about you:\n{memory_summary}\n\n" if memory_summary else ""
            enhanced_query = memory_boost + req.query

            response = rag_chain.run(enhanced_query)

            summarize_and_store_if_needed(req.query)

            return {"response": response.strip(), "intent": intent}

        else:
            return {"response": "🤔 I couldn't understand your request.", "intent": intent}

    except Exception as e:
        return {"error": f"❌ Chat processing failed: {str(e)}"}


# ==== ROOT ====
@app.get("/")
def root():
    return {"status": "🧠 Tess AI Central Server running."}


# ==== Memory-Agent ====
@app.post("/add-memory")
async def add_memory(data: dict):
    memory_text = data.get("memory")
    if not memory_text:
        return {"error": "No memory provided."}
    collected_memory_agent.save_memory(memory_text)
    return {"message": "✅ Memory saved to collected memories."}

# ==== ENTRYPOINT ====
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
