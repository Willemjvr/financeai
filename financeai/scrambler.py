"""PII scrambling — regex-based, zero external dependencies.

Catches: SA ID numbers, emails, phone numbers, bank account numbers.
Names intentionally left alone — out of scope for this tool.
"""

import re

from financeai.lookup import add_mappings


PATTERNS = [
    ("ID",    re.compile(r'\b(\d{6}[- ]?\d{4}[- ]?\d{3})\b')),
    ("EMAIL", re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')),
    ("PHONE", re.compile(r'(?:0[1-9]\d|(?:\+27)[- ]?[1-9]\d)[- ]?\d{3}[- ]?\d{4}')),
    ("ACCT",  re.compile(r'\b[A-Z]{3,4}-\d{4,12}\b')),
]


def scramble(text: str, **_kw) -> tuple[str, dict]:
    """Scramble PII in text. Returns (scrambled_text, {token: original})."""
    result = text
    mapping = {}
    counters = {}

    for prefix, pattern in PATTERNS:
        matches = list(dict.fromkeys(pattern.findall(result)))
        for orig in matches:
            counters[prefix] = counters.get(prefix, 0) + 1
            token = f"{prefix}_{counters[prefix]:03d}"
            mapping[token] = orig
            result = result.replace(orig, token, 1)

    if mapping:
        add_mappings(mapping)

    return result, mapping
