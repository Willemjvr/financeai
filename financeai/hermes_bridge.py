"""Bridge to Hermes — sends scrambled query to Hermes CLI."""

import subprocess
from financeai.config import get_config
from financeai.lookup import resolve_text


def ask_hermes(scrambled_query: str, unscramble: bool = True) -> str:
    cfg = get_config()
    hermes = cfg["hermes_cmd"]

    try:
        result = subprocess.run(
            [hermes, "chat", "-q", scrambled_query],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip() or "no output"
            return f"[Hermes error: {stderr[:200]}]"

        response = result.stdout.strip()
        if unscramble and response:
            resolved = resolve_text(response)
            if resolved != response:
                response = resolved
        return response

    except subprocess.TimeoutExpired:
        return "[Hermes timed out after 5 min]"
    except FileNotFoundError:
        return f"[Hermes CLI not found. Is 'hermes' installed?]"
    except Exception as e:
        return f"[Error: {e}]"
