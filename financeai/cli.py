"""FINANCEAI CLI — Secure PII-scrambling interface for Hermes AI.

Usage:
    financeai ask "your question"      Single query (scramble + send + show)
    financeai interactive               REPL loop for multiple queries
    financeai lookup                    Show the PII lookup table
    financeai lookup clear              Clear the PII lookup table
    financeai version                   Show version info
"""

import sys
import argparse

from financeai import __version__, __app_name__
from financeai.artwork import (
    print_banner,
    print_interactive_header,
    success,
    warn,
    error,
    info,
    dim,
    section,
    C,
)
from financeai.config import get_config, check_config
from financeai.scrambler import scramble
from financeai.hermes_bridge import ask_hermes
from financeai.lookup import get_all, clear as clear_lookup


# ──────────────────────────────────────────
# Individual commands
# ──────────────────────────────────────────

def cmd_ask(query: str):
    """Scramble → Hermes → output."""
    print_banner()

    cfg = get_config()
    issues = check_config(cfg)
    for issue in issues:
        warn(issue)
    if issues:
        print()

    # Step 1: Scramble
    section("PII Scrambling")
    scrambled, mapping = scramble(
        query,
        show_warnings=cfg.get("show_warnings", True),
    )

    if mapping:
        info(f"Scrambled {len(mapping)} item(s)")
        for token, original in mapping.items():
            dim(f"  {token} ← {original}")

    if scrambled != query:
        success("Query scramled")
        dim(f"Scrambled: {scrambled}")
    else:
        warn("No PII detected — query sent as-is")
    print()

    # Step 2: Send to Hermes
    response = ask_hermes(
        scrambled,
        unscramble=cfg.get("auto_unscramble", True),
    )
    print()

    # Step 3: Show response
    section("Response")
    print(f"\n{C.DIM}────────────────────────────────────────{C.RESET}\n")
    print(response)
    print(f"\n{C.DIM}────────────────────────────────────────{C.RESET}\n")


def cmd_interactive():
    """REPL loop."""
    print_banner()
    print_interactive_header()

    cfg = get_config()
    issues = check_config(cfg)
    for issue in issues:
        warn(issue)
    if issues:
        info("Queries will pass through unscrambled until you set an API key.")
    print()

    print(
        "  Type your question and press Enter. "
        "Sensitive data gets scrambled before Hermes sees it."
    )
    print()

    history: list[str] = []

    while True:
        try:
            query = input(f"  {C.BOLD}{C.BRIGHT_CYAN}┃>{C.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            info("Goodbye.")
            break

        if not query:
            continue

        if query.lower() in ("exit", "quit", "q", "/exit"):
            info("Goodbye.")
            break

        if query.lower() in ("clear", "cls"):
            print("\n" * 40)
            print_interactive_header()
            continue

        history.append(query)

        # Scramble
        scrambled, mapping = scramble(
            query,
            show_warnings=cfg.get("show_warnings", True),
        )

        if mapping:
            for token, original in mapping.items():
                dim(f"  {token} ← {original}")

        print()

        # Send to Hermes
        response = ask_hermes(
            scrambled,
            unscramble=cfg.get("auto_unscramble", True),
        )
        print()

        # Show response
        print(f"  {C.BRIGHT_GREEN}━━━ Response ━━━{C.RESET}\n")
        print(response)
        print()
        print(f"  {C.DIM}━━━━━━━━━━━━━━━{C.RESET}\n")


def cmd_lookup():
    """Show or clear the lookup table."""
    data = get_all()
    if not data:
        info("Lookup table is empty.")
        return

    section("PII Lookup Table")
    for token, original in sorted(data.items()):
        print(f"  {C.BRIGHT_YELLOW}{token}{C.RESET} ← {original}")
    print()
    info(f"{len(data)} mapping(s) stored in ~/.financeai/lookup.json")


def cmd_lookup_clear():
    """Clear the lookup table."""
    clear_lookup()
    success("Lookup table cleared.")
    dim("File: ~/.financeai/lookup.json")


def cmd_version():
    """Show version."""
    print(f"{C.BOLD}{__app_name__}{C.RESET} v{__version__}")
    print(f"\n{C.DIM}Secure PII-scrambling CLI for Hermes AI{C.RESET}")


# ──────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="financeai",
        description="Secure PII-scrambling CLI for Hermes AI integration",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable coloured output",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ask
    ask_p = sub.add_parser("ask", help="Scramble a query and send it to Hermes")
    ask_p.add_argument("query", nargs="+", help="Your question")

    # interactive
    sub.add_parser("interactive", help="Start an interactive REPL session")

    # lookup
    lookup_p = sub.add_parser("lookup", help="Show or manage the PII lookup table")
    lookup_p.add_argument(
        "action",
        nargs="?",
        choices=["show", "clear"],
        default="show",
        help="'show' (default) or 'clear'",
    )

    # version
    sub.add_parser("version", help="Show version information")

    args = parser.parse_args()

    if args.no_color:
        # Handled by artwork.py's isatty check + future calls
        pass

    if args.command == "ask":
        query = " ".join(args.query)
        cmd_ask(query)

    elif args.command == "interactive":
        cmd_interactive()

    elif args.command == "lookup":
        if args.action == "clear":
            cmd_lookup_clear()
        else:
            cmd_lookup()

    elif args.command == "version":
        cmd_version()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
