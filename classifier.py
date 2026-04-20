"""
Classify user input as URL vs text and evaluate domain credibility.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from data_loader import blocklist_set, normalize_domain, ugc_platforms_set

def _host_in_set(host: str, domains: set[str]) -> bool:
    """True if host equals a listed domain or is a subdomain of one (e.g. m.twitter.com vs twitter.com)."""
    h = normalize_domain(host)
    if not h:
        return False
    if h in domains:
        return True
    for d in domains:
        if d and (h == d or h.endswith("." + d)):
            return True
    return False

_URL_SCHEME = re.compile(r"^https?://", re.IGNORECASE)
# First path segment looks like host.tld
_DOMAIN_LIKE = re.compile(
    r"^([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}",
    re.IGNORECASE,
)

def process_input(raw: str) -> tuple[str, str]:
    """
    Returns (input_type, parsed_value) where input_type is 'url' or 'text'.
    For URLs, parsed_value is the normalized root domain; for text, the stripped string.
    """
    s = raw.strip()
    if not s:
        return ("text", "")

    candidate = s
    if _URL_SCHEME.match(candidate):
        p = urlparse(candidate)
        netloc = p.netloc or ""
        if not netloc and p.path:
            # Rare: path-only; treat path's first segment as host if domain-like
            first = candidate.split("/", 3)[2] if candidate.count("/") >= 2 else ""
            netloc = first.split("/")[0] if first else ""
        domain = normalize_domain(netloc)
        return ("url", domain) if domain else ("text", s)

    # No scheme: if the first token looks like a domain, parse as URL
    first_token = s.split()[0]
    host_part = first_token.split("/")[0]
    if _DOMAIN_LIKE.match(host_part):
        p = urlparse(f"https://{first_token}")
        netloc = p.netloc or host_part
        domain = normalize_domain(netloc)
        return ("url", domain) if domain else ("text", s)

    return ("text", s)

def evaluate_credibility(input_type: str, parsed_value: str) -> str:
    """
    Returns 'FAKE', 'UGC', or 'UNKNOWN'.
    Plain text always UNKNOWN; URLs are checked against blocklist then UGC sets.
    """
    if input_type != "url" or not parsed_value:
        return "UNKNOWN"
    d = normalize_domain(parsed_value)
    if _host_in_set(d, blocklist_set):
        return "FAKE"
    if _host_in_set(d, ugc_platforms_set):
        return "UGC"
    return "UNKNOWN"