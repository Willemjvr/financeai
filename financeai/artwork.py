"""ASCII art and CLI formatting for FINANCEAI."""

import sys
import shutil
from datetime import datetime

# ──────────────────────────────────────────
# Colour helpers (ANSI)
# ──────────────────────────────────────────

class C:
    """ANSI colour codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"

    # Foreground
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Bright
    BRIGHT_GREEN = "\033[92;1m"
    BRIGHT_CYAN = "\033[96;1m"
    BRIGHT_YELLOW = "\033[93;1m"
    BRIGHT_RED = "\033[91;1m"
    BRIGHT_BLUE = "\033[94;1m"
    BRIGHT_MAGENTA = "\033[95;1m"


def disable_colour():
    """Strip ANSI codes when output is piped."""
    for attr in dir(C):
        if not attr.startswith("_"):
            setattr(C, attr, "")


if not sys.stdout.isatty():
    disable_colour()


# ──────────────────────────────────────────
# Banner ASCII art
# ──────────────────────────────────────────

BANNER = f"""
{C.BRIGHT_MAGENTA}    ███████╗██╗███╗   ██╗ █████╗ ███╗   ██╗ ██████╗███████╗ █████╗ ██╗
{C.BRIGHT_CYAN}    ██╔════╝██║████╗  ██║██╔══██╗████╗  ██║██╔════╝██╔════╝██╔══██╗██║
{C.BRIGHT_MAGENTA}    █████╗  ██║██╔██╗ ██║███████║██╔██╗ ██║██║     █████╗  ███████║██║
{C.BRIGHT_CYAN}    ██╔══╝  ██║██║╚██╗██║██╔══██║██║╚██╗██║██║     ██╔══╝  ██╔══██║██║
{C.BRIGHT_MAGENTA}    ██║     ██║██║ ╚████║██║  ██║██║ ╚████║╚██████╗███████╗██║  ██║██║
{C.BRIGHT_CYAN}    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝╚═╝
{C.RESET}
{C.BOLD}{C.WHITE}    Secure PII Scrambling  •  Hermes AI Bridge  •  Financial Data Protection{C.RESET}
{C.DIM}    ─────────────────────────────────────────────────────────────{C.RESET}
{C.DIM}    v0.1.0  |  {datetime.now().strftime('%Y-%m-%d')}{C.RESET}
"""

INTERACTIVE_HEADER = f"""
{C.BRIGHT_GREEN}╔══════════════════════════════════════════════════════════════╗
║               {C.BRIGHT_CYAN}FINANCEAI Interactive Mode{C.BRIGHT_GREEN}               ║
║  {C.DIM}Type your queries. Sensitive data is scrambled before reaching AI{C.BRIGHT_GREEN}  ║
║  {C.DIM}Type 'exit' or Ctrl+C to quit{C.BRIGHT_GREEN}                                  ║
╚══════════════════════════════════════════════════════════════╝{C.RESET}
"""


def print_banner():
    """Print the app banner."""
    print(BANNER)


def print_interactive_header():
    """Print interactive mode header."""
    width = min(shutil.get_terminal_size().columns, 72)
    print()
    print(INTERACTIVE_HEADER)
    print()


def success(msg: str):
    """Print a success message."""
    print(f"  {C.BRIGHT_GREEN}✓{C.RESET} {msg}")


def warn(msg: str):
    """Print a warning message."""
    print(f"  {C.BRIGHT_YELLOW}⚠{C.RESET} {msg}")


def error(msg: str):
    """Print an error message."""
    print(f"  {C.BRIGHT_RED}✗{C.RESET} {msg}")


def info(msg: str):
    """Print an info message."""
    print(f"  {C.BRIGHT_BLUE}ℹ{C.RESET} {msg}")


def dim(msg: str):
    """Print dim text."""
    print(f"  {C.DIM}{msg}{C.RESET}")


def section(msg: str):
    """Print a section header."""
    print(f"\n  {C.BOLD}{C.BRIGHT_CYAN}▸ {msg}{C.RESET}")
    print(f"  {C.DIM}{'─' * min(len(msg) + 2, shutil.get_terminal_size().columns - 4)}{C.RESET}")
