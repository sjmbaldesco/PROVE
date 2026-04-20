"""
Load blocklist / UGC CSV datasets and persist user-flagged domains.
"""

from __future__ import annotations
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BLOCKLIST_PATH = DATA_DIR / "blocklist.csv"
UGC_PATH = DATA_DIR / "ugc_platforms.csv"

blocklist_set: set[str] = set()
ugc_platforms_set: set[str] = set()
last_load_error: str | None = None

def normalize_domain(netloc: str) -> str:
    host = netloc.lower().strip()
    if host.startswith("www."):
        host = host[4:]
    if "@" in host:
        host = host.split("@")[-1]
    if ":" in host:
        host = host.split(":")[0]
    return host


def _read_csv_domains(path: Path) -> set[str]:
    out: set[str] = set()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():
                out.add(normalize_domain(row[0].strip()))
    return out

def load_datasets() -> None:
    """
    Populate blocklist_set and ugc_platforms_set from CSV files.
    Missing files yield empty sets and last_load_error is set for the GUI.
    """
    global last_load_error

    errors: list[str] = []
    bl: set[str] = set()
    ugc: set[str] = set()

    try:
        bl = _read_csv_domains(BLOCKLIST_PATH)
    except FileNotFoundError:
        errors.append(f"Missing dataset: {BLOCKLIST_PATH.name}")
    except OSError as e:
        errors.append(f"Could not read {BLOCKLIST_PATH.name}: {e}")

    try:
        ugc = _read_csv_domains(UGC_PATH)
    except FileNotFoundError:
        errors.append(f"Missing dataset: {UGC_PATH.name}")
    except OSError as e:
        errors.append(f"Could not read {UGC_PATH.name}: {e}")

    # Mutate sets in place so modules that imported `blocklist_set` / `ugc_platforms_set`
    # keep the same object references after reload (rebinding would strand stale empty sets).
    blocklist_set.clear()
    blocklist_set.update(bl)
    ugc_platforms_set.clear()
    ugc_platforms_set.update(ugc)
    last_load_error = "; ".join(errors) if errors else None

def append_to_blocklist(domain: str) -> None:
    """Append a normalized root domain to blocklist.csv (newline after row)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    normalized = normalize_domain(domain.strip())
    if not normalized:
        raise ValueError("Empty domain")
    with open(BLOCKLIST_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([normalized])

def flag_new_source(parent) -> tuple[bool, str]:
    """
    Prompt for a domain, append to blocklist.csv, reload sets.
    Returns (success, message) for GUI confirmation or error text.
    """
    from tkinter import messagebox, simpledialog

    raw = simpledialog.askstring(
        "Flag new source",
        "Enter root domain to add to the blocklist (e.g. example.com):",
        parent=parent,
    )
    if raw is None:
        return False, ""
    raw = raw.strip()
    if not raw:
        return False, ""

    try:
        append_to_blocklist(raw)
        load_datasets()
    except OSError as e:
        return False, str(e)
    except ValueError as e:
        return False, str(e)

    confirmed = normalize_domain(raw)
    messagebox.showinfo(
        "Source flagged",
        f"Added “{confirmed}” to blocklist.csv and reloaded datasets.",
        parent=parent,
    )
    return True, confirmed

if __name__ == "__main__":
    load_datasets()
    print("blocklist:", len(blocklist_set), blocklist_set)
    print("ugc:", len(ugc_platforms_set), ugc_platforms_set)
    print("error:", last_load_error)