"""Configuration management for FINANCEAI."""

import os
from pathlib import Path

# Default paths
CONFIG_DIR = Path.home() / ".financeai"
LOOKUP_FILE = CONFIG_DIR / "lookup.json"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config() -> dict:
    """Get configuration from environment variables with sensible defaults."""
    return {
        # Scrambler LLM settings
        "scrambler_api_key": os.getenv("SCRAMBLER_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or "",
        "scrambler_base_url": os.getenv("SCRAMBLER_BASE_URL")
        or "https://api.openai.com/v1",
        "scrambler_model": os.getenv("SCRAMBLER_MODEL") or "gpt-4o-mini",

        # Hermes settings
        "hermes_cmd": os.getenv("HERMES_CMD") or "hermes",

        # Behaviour
        "auto_unscramble": os.getenv("FINANCEAI_UNSCRAMBLE", "true").lower()
        in ("1", "true", "yes"),
        "show_warnings": os.getenv("FINANCEAI_SHOW_WARNINGS", "true").lower()
        in ("1", "true", "yes"),
    }


def check_config(cfg: dict) -> list[str]:
    """Check configuration and return list of issues."""
    issues = []
    if not cfg["scrambler_api_key"]:
        issues.append(
            "No API key found. Set SCRAMBLER_API_KEY or OPENAI_API_KEY."
        )
    return issues
