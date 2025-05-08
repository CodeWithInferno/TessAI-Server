import sqlite3
import os
import datetime

class CollectedMemoryAgent:
    def __init__(self, db_path="./server_data/collected_memories.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    memory TEXT,
                    importance REAL
                )
            ''')
            conn.commit()

    def _score_importance(self, memory: str) -> float:
        memory_lower = memory.lower()
        # Very basic importance logic for now (can upgrade later easily)
        if any(word in memory_lower for word in ["project", "installed", "started", "created", "opened", "major", "deadline", "presentation"]):
            return 0.9  # Very important
        elif any(word in memory_lower for word in ["run", "open", "command", "chat", "talked"]):
            return 0.6  # Medium important
        else:
            return 0.3  # Casual memory

    def save_memory(self, memory: str):
        timestamp = datetime.datetime.now().isoformat()
        importance = self._score_importance(memory)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('INSERT INTO memories (timestamp, memory, importance) VALUES (?, ?, ?)', 
                         (timestamp, memory, importance))
            conn.commit()
        print(f"💾 [Collected Memory Saved]: {memory} (Importance: {importance:.2f})")

    def get_recent_memories(self, limit=5):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT memory FROM memories ORDER BY id DESC LIMIT ?', (limit,))
            return [row[0] for row in cursor.fetchall()]
