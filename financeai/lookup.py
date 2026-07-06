"""Lookup table management for FINANCEAI.

Maps anonymised tokens back to real PII values so responses can be
unscrambled for the user.
"""

import json
from pathlib import Path
from typing import Optional

from financeai.config import LOOKUP_FILE


def _ensure_dir():
    LOOKUP_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load() -> dict:
    """Load the full lookup table from disk."""
    _ensure_dir()
    if not LOOKUP_FILE.exists():
        return {}
    try:
        with open(LOOKUP_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict):
    """Save the full lookup table to disk."""
    _ensure_dir()
    with open(LOOKUP_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_mapping(token: str, original: str):
    """Add a single mapping."""
    data = _load()
    data[token] = original
    _save(data)


def add_mappings(mappings: dict[str, str]):
    """Add multiple mappings at once."""
    data = _load()
    data.update(mappings)
    _save(data)


def resolve(token: str) -> Optional[str]:
    """Look up the original value for a token."""
    return _load().get(token)


def resolve_text(text: str) -> str:
    """Replace all known tokens in a string with their original values."""
    data = _load()
    if not data:
        return text
    # Sort longest-first to avoid partial replacements
    for token in sorted(data, key=len, reverse=True):
        text = text.replace(token, data[token])
    return text


def get_all() -> dict:
    """Return the full lookup table."""
    return _load()


def clear():
    """Clear the lookup table."""
    _ensure_dir()
    _save({})
