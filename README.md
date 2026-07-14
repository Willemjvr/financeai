# FINANCEAI
note , This is pretty useless and doesnt work (when you ask it to look at csv files or pdfs ) heremes still looks at the real names and sends it to their server ,you will need to change all the names on the csv file itself if you want this to work , this was just to test hermes coding capibility without really thinking ,it basicly only works if you give the context yourself but you might aswell just scramble them yourself otherwise it just scrables the names ,hermes looks through your files and doesnt recognize anything , FLOP

**Secure PII-scrambling CLI for financial data analysis with Hermes AI.**

```
    ███████╗██╗███╗   ██╗ █████╗ ███╗   ██╗ ██████╗███████╗ █████╗ ██╗
    ██╔════╝██║████╗  ██║██╔══██╗████╗  ██║██╔════╝██╔════╝██╔══██╗██║
    █████╗  ██║██╔██╗ ██║███████║██╔██╗ ██║██║     █████╗  ███████║██║
    ██╔══╝  ██║██║╚██╗██║██╔══██║██║╚██╗██║██║     ██╔══╝  ██╔══██║██║
    ██║     ██║██║ ╚████║██║  ██║██║ ╚████║╚██████╗███████╗██║  ██║██║
    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝╚═╝
```

FINANCEAI sits between you and Hermes. You type a query that contains sensitive
information (client names, ID numbers, bank accounts). FINANCEAI sends it to a
separate LLM that detects and replaces all PII with anonymous tokens **before**
the query ever reaches Hermes. Hermes sees only scrambled data. The response
can be unscrambled back to real names on output.

## How it works

```
  You: "show me Thabo Mokoena's invoices from March"
        │
        ▼
  ┌─── FINANCEAI ──────────────────────────────────────┐
  │  1. Sends your query to a "scrambler" LLM           │
  │  2. Scrambler returns: "show me Client_A's invoices │
  │     from March"  +  mapping {Client_A: Thabo Mokoena}│
  │  3. Lookup table saved to ~/.financeai/lookup.json  │
  └──────────────────────────────────────────────────────┘
        │
        ▼
  ┌─── Hermes AI (sees only scrambled data) ──────────┐
  │  "Client_A has 3 invoices in March..."              │
  └──────────────────────────────────────────────────────┘
        │
        ▼
  FINANCEAI unscrambles: "**Thabo Mokoena** has 3 invoices in March..."
```

## Setup

### 1. Install

```bash
# Clone the repo
git clone https://github.com/Willemjvr/financeai.git
cd financeai

# Install
pip install .
```

Or install in editable mode (so changes take effect immediately):

```bash
pip install -e .
```

### 2. Set API key for the scrambler

FINANCEAI uses a separate cheap LLM to detect and replace PII. You can use
any OpenAI-compatible API:

```bash
# Option A: OpenAI (requires an API key)
export SCRAMBLER_API_KEY="sk-..."

# Option B: OpenRouter (cheap models)
export SCRAMBLER_API_KEY="sk-or-..."
export SCRAMBLER_BASE_URL="https://openrouter.ai/api/v1"
export SCRAMBLER_MODEL="openai/gpt-4o-mini"

# Option C: Any local/self-hosted model
export SCRAMBLER_API_KEY="not-needed"
export SCRAMBLER_BASE_URL="http://localhost:1234/v1"
export SCRAMBLER_MODEL="local-model"
```

> **No API key?** FINANCEAI still works — it passes your query through to
> Hermes unscrambled with a warning. Set one when you're ready.

### 3. Verify it works

```bash
financeai version
```

You should see the banner and version info.

## Usage

### Single query

```bash
financeai ask "show me Thabo Mokoena's invoices from March"
```

FINANCEAI will:
1. Send the query to the scrambler LLM
2. Show you what was scrambled
3. Forward the scrambled query to Hermes
4. Display Hermes' response (unscrambled)

### Interactive mode

```bash
financeai interactive
```

Keep asking questions without re-running the command. The lookup table
persists across queries so Client_A stays Client_A all session.

### Manage the lookup table

```bash
# See current mappings
financeai lookup

# Clear all mappings
financeai lookup clear
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `SCRAMBLER_API_KEY` | `OPENAI_API_KEY` fallback | API key for the scrambler LLM |
| `SCRAMBLER_BASE_URL` | `https://api.openai.com/v1` | Base URL for the scrambler API |
| `SCRAMBLER_MODEL` | `gpt-4o-mini` | Model to use for scrambling |
| `HERMES_CMD` | `hermes` | Path to the Hermes CLI command |
| `FINANCEAI_UNSCRAMBLE` | `true` | Auto-unscramble Hermes responses |
| `FINANCEAI_SHOW_WARNINGS` | `true` | Show status messages during processing |

## Project structure

```
financeai/
├── README.md
├── pyproject.toml
└── financeai/
    ├── __init__.py       # Package metadata
    ├── __main__.py       # python -m financeai support
    ├── cli.py            # CLI entry point (ask, interactive, lookup)
    ├── artwork.py        # ASCII art, colours, formatting
    ├── config.py         # Environment-based configuration
    ├── lookup.py         # PII lookup table (JSON file)
    ├── scrambler.py      # LLM-based PII detection & scrambling
    └── hermes_bridge.py  # Routes scrambled queries to Hermes
```

## Security notes

- The scrambler LLM sees the **raw query** including PII — choose a trusted
  provider (local model, or a paid API that doesn't train on your data).
- The lookup table is stored **locally** on your machine at
  `~/.financeai/lookup.json` — it never leaves your computer.
- Hermes sees **only** scrambled tokens, never the real data.
- If the scrambler LLM is unreachable, FINANCEAI degrades gracefully and
  passes the query through with a warning.

## License

MIT
