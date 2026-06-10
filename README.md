# Overseer

> A second brain you reason *with*: drop in your life and work, and it folds everything into one graph, then answers like a counsellor who has read all of it.

![Built on Claude Code](https://img.shields.io/badge/engine-Claude%20Code-8A2BE2)
![Python](https://img.shields.io/badge/viewer-Python-3776AB)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

Overseer has **no application code**, and that is the design. It is plain files plus one protocol (`OVERSEER.md`), and Claude Code is the engine that reads your corpus, builds a graph in `brain/`, and reasons over it. Your notes are not the asset. The **edges between them are**: this goal is gated by that review, which collides with that deadline, which serves a goal a third person could unblock. That web is where judgement lives.

## Quickstart

```bash
git clone https://github.com/lambdaf-org/overseer
cd overseer

# A) the webview: a dashboard, no terminal to manage
./launch.sh web                  # then open http://127.0.0.1:8787

# B) a Claude Code session in this folder: the raw engine
./launch.sh                      # git-inits brain/, then tells you what to do
```

Then:

1. Put files in `corpus/` (`self/`, `network/`, `work/` are intake hints).
2. For live capture, have any Whisper tool append `ts | speaker | text` lines into `inbox/`.
3. Say **"fold"** to build the brain, then ask it anything.

Ships with a synthetic seed. Try the acceptance test: **"given everything, what should I focus on this week?"** Then replace the seed in `brain/` with your own life and ask again.

## Features

- **One node space.** People, goals, projects, facts, events, and themes are all the same shape and live in one graph, so traversal crosses domains without switching modes.
- **Status is inferred, never stored.** It records dated events and works out the current state when you ask. No record that you submitted means the honest answer is "I don't know, did you?"
- **Every claim shows its receipt.** A statement about a person or the world carries a verbatim quote and a pointer to the source. No source, no claim.
- **No number it cannot defend by counting.** It shows the tally with dates so you can recompute it, and skips self-scored confidence, urgency, and warmth values.
- **It pushes back.** When what you say you want drifts from what your record shows, it says so, falsifiably, with the evidence.
- **Cost scales with the question.** A read plan loads the compass and the few cards a question touches, walking tension edges to the conflict. It never reads `brain/` end to end.
- **Lossy on purpose.** `corpus/` is the only ground truth; `brain/` is a small, re-derivable index over it, re-compressed each fold so a register grows like the log of the corpus.
- **History for free.** `brain/` is under git, so "what changed since last week?" is `git log` over `brain/`.

## How it works

Two rituals run everything:

- **FOLD** turns new material into brain. It reads `inbox/` and any `corpus/` source with no shard yet, strips secrets, summarizes each heavy source into a pointer-dense shard, mints nodes, and (the real work) links them with mirrored edges. It can enrich from the web with **generic** queries, then appends dated events to the journal and commits `brain/`.
- **ASK** is the counsellor. It reads the index first, forms a read plan, traverses the touched subgraph, threads at least two families (your goals, the people, what it blocks, a fresh web fact), grounds every claim with a locator, and writes any decision back so advice compounds.

The webview (`web/`) is the **expression layer**: a Python stdlib server with no build step that *shows* `brain/`, *writes* to `inbox/`, and *runs* headless `claude -p` for the ask / fold / focus / drop buttons. It adds no intelligence, and deleting `web/` loses nothing. See `web/README.md`.

## What's where

```
OVERSEER.md   the operating manual; it is the entire program
brain/        index.md (router + digest) · nodes/ (one graph) · journal.md · shards/
corpus/       your raw material, untouched (self/ network/ work/ are intake hints)
inbox/        new material to fold; where Whisper drops transcripts
web/          the optional local viewer + remote control
```

## Trust model

Your files stay on disk, but folding puts them into Claude's context, and web enrichment sends *generic* queries out (never your names, handles, or secrets). This is a private tool that is careful about what leaves, and it is not airgapped. Credentials are stripped before anything is recorded. `brain/` is yours to keep local or commit. The webview binds `127.0.0.1`, checks the Host header, and requires a per-launch CSRF token for any action that changes state.

## Contributing

Lambdaforge is open source and contributions are welcome. Start with the [contributor guide](https://github.com/lambdaf-org/contributing), and see the org-wide [CONTRIBUTING](https://github.com/lambdaf-org/.github/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/lambdaf-org/.github/blob/main/CODE_OF_CONDUCT.md).

## License

MIT. See [LICENSE](./LICENSE).
