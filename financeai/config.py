"""Configuration for FINANCEAI."""

import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".financeai"
LOOKUP_FILE = CONFIG_DIR / "lookup.json"


def get_config() -> dict:
    return {
        "hermes_cmd": os.getenv("HERMES_CMD") or "hermes",
    }
