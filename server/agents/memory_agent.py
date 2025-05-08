import sqlite3
import os
import datetime

class MemoryAgent:
    def __init__(self, db_path="./server_data/memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    memory TEXT
                )
            ''')
            conn.commit()

    def save_memory(self, memory: str):
        timestamp = datetime.datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('INSERT INTO memories (timestamp, memory) VALUES (?, ?)', (timestamp, memory))
            conn.commit()
        print(f"💾 [Memory Saved]: {memory}")

    def get_recent_memories(self, limit=5):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT memory FROM memories ORDER BY id DESC LIMIT ?', (limit,))
            return [row[0] for row in cursor.fetchall()]
