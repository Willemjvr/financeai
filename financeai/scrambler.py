"""LLM-based PII scrambling for FINANCEAI."""

import json
import sys

from financeai.artwork import info, warn, error, dim
from financeai.config import get_config
from financeai.lookup import add_mappings

# Try importing requests; give a helpful message if missing.
try:
    import requests
except ImportError:
    print(
        "ERROR: 'requests' is required. Install it with:  pip install requests",
        file=sys.stderr,
    )
    sys.exit(1)

# ──────────────────────────────────────────
# The scrambler system prompt
# ──────────────────────────────────────────

SCRAMBLER_SYSTEM_PROMPT = """You are a financial PII (Personally Identifiable Information) scrambler.

Your job: detect sensitive information in the user's query and replace every
instance with a short anonymised token. Return the result as JSON.

SCRAMBLE THESE TYPES:
- Person names → Client_A, Client_B, etc.
- ID / passport numbers → ID_001, ID_002, etc.
- Bank account numbers → ACCT_001, ACCT_002, etc.
- Phone numbers → PHONE_001, etc.
- Email addresses → EMAIL_001, etc.
- Physical / postal addresses → ADDR_001, etc.
- Company / entity names → COMPANY_001, etc.
- Tax numbers / VAT numbers → TAX_001, etc.

RULES:
1. Keep numbers that are NOT identifying (amounts, dates, invoice numbers,
   quantities, percentages) exactly as written — do NOT touch them.
2. Keep the structure, grammar, and query intent intact.
3. If nothing sensitive is found, return the original text unchanged with
   an empty mapping.

RESPONSE FORMAT — respond with ONLY this JSON, no other text:
{
  "scrambled": "the query with PII replaced by tokens",
  "mapping": {
    "Client_A": "original name or value",
    "ID_001": "original ID number"
  }
}

If nothing was scrambled, "mapping" is an empty object {}."""


def scramble(text: str, show_warnings: bool = True) -> tuple[str, dict]:
    """Send text to the scrambler LLM and return (scrambled_text, mapping).

    If the LLM call fails, returns (original_text, {}) with a warning.
    """
    cfg = get_config()

    if not cfg["scrambler_api_key"]:
        warn("No scrambler API key configured — passing query through unscrambled.")
        return text, {}

    headers = {
        "Authorization": f"Bearer {cfg['scrambler_api_key']}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": cfg["scrambler_model"],
        "messages": [
            {"role": "system", "content": SCRAMBLER_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "temperature": 0.0,
        "max_tokens": 1024,
    }

    if show_warnings:
        dim(f"Scrambling via {cfg['scrambler_model']} ...")

    try:
        resp = requests.post(
            f"{cfg['scrambler_base_url'].rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()

        raw = body["choices"][0]["message"]["content"].strip()

        # Strip markdown code fences if the LLM wraps it
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            raw = raw.rsplit("```", 1)[0].strip()

        result = json.loads(raw)
        scrambled = result.get("scrambled", text)
        mapping = result.get("mapping", {})

        # Save mapping to the persistent lookup table
        if mapping:
            add_mappings(mapping)
            if show_warnings:
                info(f"Scrambled {len(mapping)} sensitive item(s)")

        return scrambled, mapping

    except requests.exceptions.Timeout:
        error("Scrambler LLM timed out after 30s — passing through unscrambled.")
        return text, {}
    except requests.exceptions.ConnectionError:
        error(
            f"Could not connect to {cfg['scrambler_base_url']} "
            f"— passing through unscrambled."
        )
        return text, {}
    except requests.exceptions.HTTPError as e:
        error(f"Scrambler LLM returned HTTP {e.response.status_code} — passing through.")
        return text, {}
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        error(f"Could not parse scrambler response ({e}) — passing through.")
        if show_warnings:
            dim(f"Raw response: {raw[:300]}")
        return text, {}
