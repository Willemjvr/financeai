"""FINANCEAI CLI.

Usage:
    financeai ask "your question"     Single query
    financeai interactive              REPL loop
    financeai lookup                   Show PII lookup table
    financeai lookup clear             Clear lookup table
    financeai version                  Show version
"""

import sys
import argparse
import threading
import itertools
import time

from financeai import __version__, __app_name__
from financeai.artwork import print_banner, print_interactive_header, C
from financeai.scrambler import scramble
from financeai.hermes_bridge import ask_hermes
from financeai.lookup import get_all, clear as clear_lookup


# ──────────────────────────────────────────
# Spinner
# ──────────────────────────────────────────

class Spinner:
    """Simple CLI spinner that runs while Hermes processes."""

    def __enter__(self):
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *args):
        self._stop.set()
        self._thread.join()
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()

    def _spin(self):
        chars = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        while not self._stop.is_set():
            sys.stdout.write(f"\r  {C.DARK_RED3}{next(chars)}{C.RESET} Hermes processing...")
            sys.stdout.flush()
            time.sleep(0.08)


# ──────────────────────────────────────────
# Commands
# ──────────────────────────────────────────

def cmd_ask(query: str):
    print_banner()

    # Step 1: Scramble
    scrambled, mapping = scramble(query)

    show_query = f"  {C.BOLD}Query:{C.RESET} {query}"
    line_len = min(len(show_query) + 10, 72)
    print(f"  {C.DARK_RED2}▌{C.RESET} {show_query}")

    if mapping:
        types = set(k.split("_")[0] for k in mapping)
        print(f"  {C.DARK_RED2}▌{C.RESET} {C.DIM}Scrambled:{C.RESET} {len(mapping)} item(s) [{', '.join(sorted(types))}]")
    else:
        print(f"  {C.DARK_RED2}▌{C.RESET} {C.DIM}No sensitive data detected{C.RESET}")

    print()

    # Step 2: Hermes with spinner
    with Spinner():
        response = ask_hermes(scrambled, unscramble=True)

    print()

    # Step 3: Response
    print(f"  {C.BOLD}{C.DARK_RED3}━━━ Response ━━━{C.RESET}\n")
    print(f"  {response}")
    print(f"\n  {C.DIM}━━━━━━━━━━━━━━━{C.RESET}\n")


def cmd_interactive():
    print_banner()
    print_interactive_header()
    print(f"  {C.DIM}Type your query. Sensitive data scrambles before reaching Hermes.{C.RESET}")
    print(f"  {C.DIM}Type 'exit' or Ctrl+C to quit.{C.RESET}\n")

    while True:
        try:
            query = input(f"  {C.BOLD}{C.DARK_RED3}┃>{C.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print(f"  {C.DIM}Bye.{C.RESET}")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit", "q", "/exit"):
            print(f"  {C.DIM}Bye.{C.RESET}")
            break

        scrambled, mapping = scramble(query)
        if mapping:
            types = set(k.split("_")[0] for k in mapping)
            print(f"  {C.DIM}Scrambled: {len(mapping)} item(s) [{', '.join(sorted(types))}]{C.RESET}")

        print()

        with Spinner():
            response = ask_hermes(scrambled, unscramble=True)

        print()
        print(f"  {C.BOLD}{C.DARK_RED3}━━━ Response ━━━{C.RESET}\n")
        print(f"  {response}")
        print(f"\n  {C.DIM}━━━━━━━━━━━━━━━{C.RESET}\n")


def cmd_lookup():
    data = get_all()
    if not data:
        print(f"  {C.DIM}Lookup table is empty.{C.RESET}")
        return
    print(f"  {C.BOLD}PII Lookup Table{C.RESET}\n")
    for token, original in sorted(data.items()):
        print(f"    {C.DARK_RED3}{token}{C.RESET}  \u2190  {original}")
    print(f"\n  {C.DIM}{len(data)} mapping(s) stored.{C.RESET}")


def cmd_lookup_clear():
    clear_lookup()
    print(f"  {C.DARK_RED3}\u2713{C.RESET} Lookup table cleared.")


def cmd_version():
    print(f"{C.BOLD}{__app_name__}{C.RESET} v{__version__}")
    print(f"  {C.DIM}Secure PII-scrambling CLI for Hermes{C.RESET}")


# ──────────────────────────────────────────
# Main
# ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(prog="financeai", description="Secure PII-scrambling CLI for Hermes")
    sub = parser.add_subparsers(dest="command")

    p_ask = sub.add_parser("ask", help="Scramble a query and send to Hermes")
    p_ask.add_argument("query", nargs="+")

    sub.add_parser("interactive", help="REPL session")

    p_lk = sub.add_parser("lookup", help="Manage PII lookup table")
    p_lk.add_argument("action", nargs="?", choices=["show", "clear"], default="show")

    sub.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command == "ask":
        cmd_ask(" ".join(args.query))
    elif args.command == "interactive":
        cmd_interactive()
    elif args.command == "lookup":
        cmd_lookup_clear() if args.action == "clear" else cmd_lookup()
    elif args.command == "version":
        cmd_version()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
