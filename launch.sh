#!/usr/bin/env bash
# Overseer — there is no engine to run; Claude Code is the engine. This prepares the
# memory, optionally opens the webview, and points you at the protocol.
set -euo pipefail
cd "$(dirname "$0")"

# brain/ is versioned: git diff is how Overseer knows what changed. Initialise it once.
if [ ! -d .git ]; then
  git init -q
  git add -A
  git commit -q -m "overseer: seed brain" || true
  echo "Initialised git (brain/ is now under version control — 'what changed' = git diff)."
fi

# `./launch.sh web` opens the expression layer (a local viewer + remote control for
# headless Claude Code). It is optional — everything works from a plain Claude Code
# session in this folder too.
if [ "${1:-}" = "web" ]; then
  exec python3 web/serve.py
fi

cat <<'EOF'

Overseer is ready. Two ways in:

  • The webview (simplest):   ./launch.sh web    → open http://127.0.0.1:8787
      a dashboard of the brain + ask/fold/focus buttons + drop-to-inbox.

  • A Claude Code session in this folder (the raw engine):
      1. Put material in corpus/ (self/ network/ work/) or drop files in inbox/.
         For live capture, append `ts | speaker | text` lines to inbox/.
      2. Say "fold"        -> it reads what's new and updates brain/.
         Then ask anything -> it answers as your second brain.

Read OVERSEER.md once. It is the whole program.
Try: "given everything, what should I focus on this week?"
EOF
