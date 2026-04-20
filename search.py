"""
Build fact-check search URL with site operators and open the default browser.
"""

from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from urllib.parse import quote_plus

from logger import log_transaction

factcheck_operators = [
    "verafiles.org",
    "rappler.com",
    "tsek.ph",
    "mindanews.com",
    "pressone.ph",
    "news.abs-cbn.com",
    "philstar.com",
]

def _open_url(url: str) -> None:
    if webbrowser.open(url):
        return
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", url], check=False)
        elif sys.platform.startswith("win"):
            os.startfile(url)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", url], check=False)
    except OSError:
        pass

def execute_search(sanitized_user_input: str) -> str | None:
    """
    Concatenate site: operators into a single search query, open Google search in the browser,
    then log the final query string. Returns log error message if logging failed, else None.
    """
    user_part = sanitized_user_input.strip()
    operator_parts = " OR ".join(f"site:{op}" for op in factcheck_operators)
    final_query = f"({operator_parts}) {user_part}".strip()
    url = "https://www.google.com/search?q=" + quote_plus(final_query)
    _open_url(url)
    return log_transaction(final_query)