# server/core/filesystem_manager.py
import sqlite3
import os
from typing import List, Dict, Optional
from pathlib import Path
from pydantic import BaseModel

DB_FOLDER = "server_data"

class FileEntry(BaseModel):
    device_id: str
    path: str
    name: str
    is_dir: bool
    extension: str
    size: int

class FileMemory:
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.db_path = os.path.join(DB_FOLDER, f"{device_id}.db")
        self._ensure_database()

    def _ensure_database(self):
        os.makedirs(DB_FOLDER, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
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
            conn.commit()

    def save_files(self, files: List[FileEntry]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT INTO files (path, name, is_dir, extension, size)
                VALUES (?, ?, ?, ?, ?)
            ''', [
                (f.path, f.name, f.is_dir, f.extension, f.size)
                for f in files
            ])
            conn.commit()

    def search(self, name_query: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT path, name, is_dir, extension, size FROM files
                WHERE name LIKE ?
            ''', (f"%{name_query}%",))
            rows = cursor.fetchall()

        return [
            {
                "path": row[0],
                "name": row[1],
                "is_dir": bool(row[2]),
                "extension": row[3],
                "size": row[4]
            } for row in rows
        ]

    def all_files(self, max_limit: Optional[int] = None) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = 'SELECT path, name, is_dir, extension, size FROM files'
            if max_limit:
                query += f' LIMIT {max_limit}'
            cursor.execute(query)
            rows = cursor.fetchall()

        return [
            {
                "path": row[0],
                "name": row[1],
                "is_dir": bool(row[2]),
                "extension": row[3],
                "size": row[4]
            } for row in rows
        ]
