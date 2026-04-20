"""
Append-only transaction log for fact-check queries.
"""

from __future__ import annotations
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
HISTORY_PATH = LOG_DIR / "history.txt"

def sanitize_for_log(text: str) -> str:
    return " ".join(text.replace("\t", " ").split())

def log_transaction(query: str) -> str | None:
    """
    Append ISO-8601 timestamp, TAB, sanitized query to history.txt.
    Returns an error message string on IOError, else None.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = datetime.now().isoformat() + "\t" + sanitize_for_log(query) + "\n"
    try:
        with open(HISTORY_PATH, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError as e:
        return f"Could not write log: {e}"
    return None

if __name__ == "__main__":
    err = log_transaction("test query")
    print("err:", err)