import sqlite3
import os
import re
from pathlib import Path
from typing import List, Literal, Optional, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEVICE_DB_DIR = PROJECT_ROOT / "server_data" / "Device_Data"

# Common filler words you want to ignore
JUNK_WORDS = {"open", "file", "folder", "run", "start", "launch", "execute",
              "find", "search", "show", "list", "the", "a", "an", "pdf", "docx", "image", "picture", "directory"}

def load_files_from_device(device_id: str) -> List[Dict]:
    db_path = DEVICE_DB_DIR / f"{device_id}.db"
    if not db_path.exists():
        print(f"❌ No DB for {device_id}")
        return []

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT path, name, is_dir FROM files")
        return [
            {"path": row[0], "name": row[1], "is_dir": bool(row[2])}
            for row in cursor.fetchall()
        ]

def smart_find_filesystem(query: str, device_id: str, intent: Literal["folder", "file", "any"] = "any") -> List[str]:
    files = load_files_from_device(device_id)
    if not files:
        return []

    # 1. Preprocess query: meaningful keywords
    query_words = [
        word.lower() for word in re.findall(r'\w+', query)
        if word.lower() not in JUNK_WORDS and len(word) > 2
    ]
    if not query_words:
        return []

    print(f"[🧠 Important words]: {query_words}")

    candidates = []

    # 2. Match all keywords roughly
    for f in files:
        path = f["path"].lower()
        name = f["name"].lower()
        score = 0

        for keyword in query_words:
            if keyword in name:
                score += 50
            if keyword in path:
                score += 20
            if path.endswith(keyword):
                score += 100
        
        if intent == "folder" and f["is_dir"]:
            score += 30
        if intent == "file" and not f["is_dir"]:
            score += 30

        # Shorter paths = better
        score -= len(path) // 20

        if score > 0:
            candidates.append((score, f["path"]))

    # 3. Sort best score first
    candidates.sort(reverse=True)

    top_matches = [path for score, path in candidates]

    return top_matches
