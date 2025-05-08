import sqlite3
import os

DB_PATH = "C:/Users/prpatel/Documents/Programming/TessAI/TessAI/server/server_data/Device_Data/Darwin_Prathams-MacBook-Air.local_775abecf.db"  # Change if needed

if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at: {DB_PATH}")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT path, name, is_dir, extension, size FROM files LIMIT 5")
rows = cursor.fetchall()

print("📄 First 5 entries in the DB:/n")
for row in rows:
    print(f"Path: {row[0]}")
    print(f"Name: {row[1]}")
    print(f"Is Directory: {bool(row[2])}")
    print(f"Extension: {row[3]}")
    print(f"Size: {row[4]} bytes")
    print("-" * 40)

conn.close()
