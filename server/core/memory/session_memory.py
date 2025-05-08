from collections import deque

session_history = deque(maxlen=20)

def add_to_session(role, text):
    session_history.append({"role": role, "text": text})

def get_session_context():
    # format for prompt injection
    return "\n".join(f"{m['role']}: {m['text']}" for m in session_history)
