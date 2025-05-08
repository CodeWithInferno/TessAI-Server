import sqlite3
import os
import re
from pathlib import Path
from difflib import get_close_matches

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEVICE_DB_DIR = PROJECT_ROOT / "server_data" / "Device_Data"

def extract_filename(query: str) -> str:
    match = re.search(r'\b[\w\-]+\.\w{2,5}\b', query)
    return match.group(0) if match else None

def find_best_path(filename: str, device_id: str) -> str | None:
    if not filename:
        return None

    db_path = DEVICE_DB_DIR / f"{device_id}.db"
    if not db_path.exists():
        print(f"❌ No DB found for device: {db_path}")
        return None

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT path FROM files WHERE is_dir = 0")
        rows = [row[0] for row in cursor.fetchall()]
        conn.close()

        matches = get_close_matches(filename.lower(), [Path(p).name.lower() for p in rows], n=1, cutoff=0.6)

        if matches:
            best_name = matches[0]
            for full_path in rows:
                if Path(full_path).name.lower() == best_name:
                    return full_path
        return None

    except Exception as e:
        print("❌ File resolution error:", e)
        return None

def resolve_file_path(query: str, device_id: str) -> str | None:
    filename = extract_filename(query)
    return find_best_path(filename, device_id)
