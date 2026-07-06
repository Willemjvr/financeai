"""CLI formatting and banner for FINANCEAI."""

import sys
import shutil
from datetime import datetime


class C:
    """ANSI colour codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    DARK_RED1 = "\033[38;2;160;30;35m"
    DARK_RED2 = "\033[38;2;120;15;20m"
    DARK_RED3 = "\033[38;2;200;50;55m"


if not sys.stdout.isatty():
    for attr in dir(C):
        if not attr.startswith("_"):
            setattr(C, attr, "")


BANNER = f"""
{C.DARK_RED1}    ███████╗██╗███╗   ██╗ █████╗ ███╗   ██╗ ██████╗███████╗ █████╗ ██╗
{C.DARK_RED2}    ██╔════╝██║████╗  ██║██╔══██╗████╗  ██║██╔════╝██╔════╝██╔══██╗██║
{C.DARK_RED1}    █████╗  ██║██╔██╗ ██║███████║██╔██╗ ██║██║     █████╗  ███████║██║
{C.DARK_RED2}    ██╔══╝  ██║██║╚██╗██║██╔══██║██║╚██╗██║██║     ██╔══╝  ██╔══██║██║
{C.DARK_RED1}    ██║     ██║██║ ╚████║██║  ██║██║ ╚████║╚██████╗███████╗██║  ██║██║
{C.DARK_RED2}    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝╚═╝
{C.RESET}
{C.DIM}    ─────────────────────────────────────────────────────────────────────{C.RESET}
{C.DARK_RED3}    Secure PII Scrambling  |  Hermes AI Bridge  |  Financial Data Protection{C.RESET}
{C.DIM}    v0.1.0  |  {datetime.now().strftime('%Y-%m-%d')}{C.RESET}
"""

INTERACTIVE_HEADER = f"""
{C.DARK_RED2}╔══════════════════════════════════════════════════════════════╗
║               {C.DARK_RED3}FINANCEAI Interactive Mode{C.DARK_RED2}               ║
║  {C.DIM}Type queries. Sensitive data scrambles before reaching AI{C.DARK_RED2}  ║
║  {C.DIM}Type 'exit' or Ctrl+C to quit{C.DARK_RED2}                                  ║
╚══════════════════════════════════════════════════════════════╝{C.RESET}
"""


def print_banner():
    print(BANNER)


def print_interactive_header():
    print()
    print(INTERACTIVE_HEADER)
    print()
