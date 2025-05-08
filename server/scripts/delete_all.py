import sqlite3

DB_PATH = "server_data/file_memory.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Delete all structured memories
c.execute('DROP TABLE IF EXISTS structured_memory')
conn.commit()
conn.close()

print("✅ Structured memory wiped clean.")
