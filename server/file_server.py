from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
import sqlite3
import os

app = FastAPI()

# Ensure the data directory exists
os.makedirs("server_data", exist_ok=True)
DB_PATH = os.path.join("server_data", "file_memory.db")

# Create table on startup if it doesn't exist
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            path TEXT,
            name TEXT,
            is_dir BOOLEAN,
            extension TEXT,
            size INTEGER
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_device_path ON files(device_id, path)')
    conn.commit()

# Model for each file entry
class FileEntry(BaseModel):
    device_id: str
    path: str
    name: str
    is_dir: bool
    extension: str
    size: int

# Route to receive bulk file entries
@app.post("/upload-files")
async def upload_files(files: List[FileEntry]):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO files (device_id, path, name, is_dir, extension, size)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [
            (file.device_id, file.path, file.name, file.is_dir, file.extension, file.size)
            for file in files
        ])
        conn.commit()

    return {"message": "✅ File entries stored."}

# Default test route
@app.get("/")
def root():
    return {"status": "Tess AI File Server is running."}
