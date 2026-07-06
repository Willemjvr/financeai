"""PII scrambling for FINANCEAI — hybrid regex + LLM approach.

How it works:
1. Regex catches structured patterns (emails, SA IDs, phones, accounts) — deterministic, fast.
2. LLM catches names — asked only to LIST names found, not to rewrite text.
3. All replacement happens in Python code. Never depends on LLM output format.
"""

import json
import re
import sys

from financeai.artwork import info, warn, error, dim
from financeai.config import get_config
from financeai.lookup import add_mappings

try:
    import requests
except ImportError:
    print("ERROR: 'requests' required. Install: pip install requests", file=sys.stderr)
    sys.exit(1)

# ──────────────────────────────────────────
# Regex patterns — SA-focused
# ──────────────────────────────────────────

PATTERNS = [
    # SA ID: 13 digits — YYMMDD SSSS CAA  e.g. 880101 1234 081 (must be first,
    # otherwise phone pattern eats parts of it)
    ("ID", re.compile(r'\b(\d{6}[- ]?\d{4}[- ]?\d{3})\b')),
    # Email addresses
    ("EMAIL", re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')),
    # SA phone: 081 487 1584 or +27 81 487 1584
    ("PHONE", re.compile(r'(?:0[1-9]\d|(?:\+27)[- ]?[1-9]\d)[- ]?\d{3}[- ]?\d{4}')),
    # Bank account: 3-4 uppercase letters + dash + 4-12 digits
    ("ACCT", re.compile(r'\b[A-Z]{3,4}-\d{4,12}\b')),
]


def _replace_all(text: str, prefix: str, matches: list[str]) -> tuple[str, dict[str, str]]:
    """Replace multiple occurrences of `prefix` type and return (new_text, mapping)."""
    result = text
    mapping = {}
    for i, original in enumerate(matches, 1):
        token = f"{prefix}_{i:03d}"
        mapping[token] = original
        result = result.replace(original, token, 1)
    return result, mapping


def _regex_scramble(text: str) -> tuple[str, dict[str, str]]:
    """Run regex patterns, replace matches with tokens. Returns (text, mapping)."""
    result = text
    all_mapping = {}

    for prefix, pattern in PATTERNS:
        # Collect all matches first (avoids index shifting during replacement)
        matches = list(dict.fromkeys(pattern.findall(result)))  # dedup preserving order
        if matches:
            result, mapping = _replace_all(result, prefix, matches)
            all_mapping.update(mapping)

    return result, all_mapping


# ──────────────────────────────────────────
# LLM — name detection only
# ──────────────────────────────────────────

LLM_PROMPT = """List every person name and company name in the text below.

Return ONLY a JSON array. No explanations. No other text.
If no names found, return an empty array [].

Examples:
Input:  "Show me Thabo Mokoena's invoices for Overgrowth Pty Ltd"
Output: ["Thabo Mokoena", "Overgrowth Pty Ltd"]

Input:  "What were total sales for March"
Output: []

Text:
"""


def _llm_detect_names(text: str, cfg: dict) -> list[str]:
    """Ask the LLM to list person/company names. Returns [] on failure."""
    headers = {
        "Authorization": f"Bearer {cfg['scrambler_api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg["scrambler_model"],
        "messages": [
            {"role": "system", "content": LLM_PROMPT},
            {"role": "user", "content": text},
        ],
        "temperature": 0.0,
        "max_tokens": 256,
    }

    try:
        resp = requests.post(
            f"{cfg['scrambler_base_url'].rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            raw = raw.rsplit("```", 1)[0].strip()

        names = json.loads(raw)
        if isinstance(names, list):
            return names
        return []
    except Exception:
        return []


# ──────────────────────────────────────────
# Main entry
# ──────────────────────────────────────────

_WARNED = [False]


def scramble(text: str, show_warnings: bool = True) -> tuple[str, dict]:
    """Scramble PII. Returns (scrambled_text, {token: original})."""
    cfg = get_config()

    # ── Step 1: Regex — emails, phones, IDs, accounts ──
    partial, regex_map = _regex_scramble(text)

    # ── Step 2: LLM — name detection (on already-scrambled text) ──
    llm_map = {}
    if cfg["scrambler_api_key"]:
        names = _llm_detect_names(partial, cfg)
        if names:
            partial, llm_map = _replace_all(partial, "NAME", names)
            if show_warnings:
                info(f"Detected {len(names)} name(s): {', '.join(names)}")
    elif not _WARNED[0]:
        _WARNED[0] = True
        if show_warnings:
            warn("No scrambler API key — regex only (emails, phones, SA IDs, accounts)")

    # ── Merge and save ──
    all_mapping = {**regex_map, **llm_map}
    if all_mapping:
        add_mappings(all_mapping)
        if show_warnings:
            info(f"Scrambled {len(all_mapping)} item(s) total")

    return partial, all_mapping
