import sqlite3
import os

# STEP 1: Clean the query to extract real target
def extract_target_from_query(query: str) -> str:
    fillers = ["open", "run", "launch", "start", "execute", "find", "search"]
    query_lower = query.lower()
    for filler in fillers:
        if query_lower.startswith(filler):
            query_lower = query_lower[len(filler):]
            break
    return query_lower.strip()

# STEP 2: Categorize based on extension and directory
def categorize_entry(name: str, is_dir: bool, extension: str) -> str:
    ext = (extension or "").lower()
    
    if is_dir:
        return "folder"
    if ext in [".app", ".exe", ".bat"]:
        return "app"
    if ext in [".py", ".sh", ".jar", ".java", ".rb", ".pl"]:
        return "script"
    if ext in [".txt", ".md", ".pdf", ".docx", ".xlsx", ".pptx"]:
        return "document"
    return "other"

# STEP 3: Smart filesystem search with scoring
def smart_find_filesystem(query: str, device_id: str, intent: str = "any"):
    db_path = f"C:/Users/prpatel/Documents/Programming/TessAI/TessAI/server/uploaded_dbs/{device_id}.db"

    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT path, name, is_dir, extension FROM files")
    results = cursor.fetchall()

    query_target = extract_target_from_query(query)
    query_words = query_target.lower().split()

    matches = []

    for path, name, is_dir, extension in results:
        score = 0
        name_lower = name.lower()

        if query_target == name_lower:
            score += 100
        elif all(word in name_lower for word in query_words):
            score += 70
        elif any(word in name_lower for word in query_words):
            score += 40

        if extension:
            ext = extension.lower()
            if ext in [".app", ".exe", ".bat"]:
                score += 20  # Apps are high value
            if ext in [".py", ".sh", ".jar", ".java"]:
                score += 10  # Scripts also valuable

        # Prefer shallow paths
        depth = path.count('/')
        score += max(0, 10 - depth)

        category = categorize_entry(name, is_dir, extension)
        
        matches.append({
            "score": score,
            "path": path,
            "name": name,
            "category": category
        })

    conn.close()

    # Sort by highest score
    matches.sort(key=lambda x: x["score"], reverse=True)

    # Only keep matches with good confidence
    strong_matches = [match for match in matches if match["score"] >= 60]

    return strong_matches
