"""Bridge to Hermes — sends scrambled queries to the Hermes CLI."""

import subprocess
from financeai.artwork import info, dim, error, section

from financeai.config import get_config
from financeai.lookup import resolve_text


def ask_hermes(scrambled_query: str, unscramble: bool = True) -> str:
    """Send a (scrambled) query to Hermes and return the response.

    If unscramble is True, known tokens in the response are replaced
    with their original values.
    """
    cfg = get_config()
    hermes = cfg["hermes_cmd"]

    section("Hermes AI")

    try:
        if cfg.get("show_warnings", True):
            dim(f"Running: {hermes} chat -q \"{scrambled_query[:80]}{'...' if len(scrambled_query) > 80 else ''}\"")

        # Use list args to avoid shell quoting issues on Windows
        result = subprocess.run(
            [hermes, "chat", "-q", scrambled_query],
            capture_output=True,
            text=True,
            timeout=300,  # 5 min timeout for Hermes
        )

        if result.returncode != 0:
            stderr = result.stderr.strip() or "No error output"
            error(f"Hermes returned exit code {result.returncode}")
            if stderr:
                dim(f"stderr: {stderr[:500]}")
            return f"[Hermes error: {stderr[:200]}]"

        response = result.stdout.strip()

        # Unscramble if requested
        if unscramble and response:
            resolved = resolve_text(response)
            if resolved != response:
                info("Unscrambled tokens in Hermes response")
                response = resolved

        return response

    except subprocess.TimeoutExpired:
        error("Hermes did not respond within 5 minutes.")
        return "[Hermes timed out]"
    except FileNotFoundError:
        error(
            f"'{hermes}' command not found. "
            "Is Hermes installed? Set HERMES_CMD env var if it's a different path."
        )
        return "[Hermes not found]"
    except Exception as e:
        error(f"Failed to call Hermes: {e}")
        return f"[Bridge error: {e}]"
