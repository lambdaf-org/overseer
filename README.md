# Overseer

> A file-based second brain that Claude Code reasons over. It folds a corpus of notes, people, and work into one node graph and answers like a counsellor who has read all of it, with `./launch.sh web` for a local dashboard.

![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)

Overseer has no application code, and that is the design. It is plain files plus one protocol document (`OVERSEER.md`), and Claude Code is the engine that reads the corpus, builds a graph in `brain/`, and reasons over it. The corpus is the only source of truth. `brain/` is a small, re-derivable index over it (a router file, a single node space, a journal, and pointer-dense shards), kept deliberately lossy so that one question reads only the subgraph it touches rather than the whole archive.

The graph keeps people, goals, projects, dated events, and world-facts in one node space, where the edges between them carry the counsel: a goal gated by a deadline, a project that threatens it, a person on its critical path. Four rules hold the discipline. Status is inferred from dated events and never stored. Every claim about a person or the world carries a quote and a locator. No number is emitted that cannot be defended by counting. The brain pushes back when stated priorities drift from what the record shows. An optional webview in `web/` is a thin local viewer and remote control that shows `brain/`, writes to `inbox/`, and runs headless `claude -p`. It adds no intelligence, and deleting it loses nothing.

## Quickstart

```bash
git clone https://github.com/lambdaf-org/overseer
cd overseer

# A) the webview: a local dashboard, no terminal to manage
./launch.sh web                  # then open http://127.0.0.1:8787

# B) a Claude Code session in this folder: the raw engine
./launch.sh                      # git-inits brain/, then prints what to do
#   1. put files in corpus/ (self/ network/ work/) or drop files in inbox/
#   2. say "fold"   -> it reads what is new and updates brain/
#   3. ask anything -> it answers as the second brain
```

The repo ships a synthetic "Sam Rivera" seed in `brain/`, so it answers immediately. The acceptance test it is built around: "given everything, what should I focus on this week?" After that, the seed can be replaced with real material and asked again. The webview needs only Python 3 from the standard library (no pip, no Node, no build step). The `fold` and `ask` actions need the `claude` CLI on PATH. Without it, the webview stages requests into `inbox/.pending/` instead of running them.

### Configuration

| Variable | Required | Purpose |
| --- | --- | --- |
| `OVERSEER_PORT` | No | Port for the webview (default `8787`). |

## Features

- **One node space**: people, goals, projects, facts, events, and themes share an identical card shape with stable kebab-case ids, grouped by domain so traversal crosses types without switching modes.
- **Status by event, never stored**: it records immutable dated events and infers current state at read time, computing any days-left from today against an absolute date, and says "I do not know" when no event answers the question.
- **Evidence over assertion**: a claim about a person or the world is written only with a verbatim quote and a locator back into `corpus/` or a fetched URL. With no source, it becomes a question instead.
- **Bounded read cost**: a read plan plus edge traversal keeps token cost scaling with the question rather than the corpus, and each fold re-compresses touched registers so they grow like the log of the corpus.
- **Git-backed memory**: `brain/` is versioned, so "what changed since last week" is a `git diff` instead of a hand-maintained change log, while `corpus/` and `inbox/` stay git-ignored and private.
- **Whisper as a sensor**: any speech-to-text tool can append `ts | speaker | text` lines into `inbox/`, and a fold turns them into events, nodes, and edges like any other source.
- **Local webview**: a single-screen dashboard (`web/serve.py`, standard library only) that renders the digest, the journal, and the node graph verbatim, binds to `127.0.0.1` with a per-launch CSRF token, and shells out to `claude -p` for fold, ask, and focus.

## How it works

The whole program is `OVERSEER.md`, the operating manual a Claude Code session reads before acting. Everything Overseer does is one of two rituals. FOLD turns new material into brain: it scopes what is unfolded (everything in `inbox/`, plus any `corpus/` source with no shard yet), strips secrets, summarizes each heavy source into a pointer-dense shard, mints nodes and the edges between them, enriches with generic web facts that never name a person, appends dated events and cross-domain tensions to the journal, then re-compresses and commits. ASK is the counsellor: read the index first, form a read plan, traverse the tension and structure edges, thread at least two families of nodes into one grounded answer, show the tally behind any ranking, and write back any decision worth remembering.

The webview is the expression layer and adds no reasoning. Its server only serves `brain/` files read-only, writes uploads into `inbox/`, and spawns `claude -p`, streaming the engine's output back over server-sent events. It never assembles context for the model. An `ask` sends the raw question with nothing prepended, so the engine forms its own read plan and cost still scales with the question. The headless engine runs under `.claude/settings.json`, which lets it read, search the web, edit `brain/`, and run git, while it denies file deletion, network shell tools, and any write to `OVERSEER.md` or `.claude/`.

This is a private tool. It is not airgapped. Files stay on disk, but folding puts them into Claude's context and web enrichment sends generic queries out (never names, handles, or secrets). Credentials are stripped before anything is recorded, and `brain/` can be kept local or committed.

## Contributing

See [lambdaf-org/contributing](https://github.com/lambdaf-org/contributing).

## License

MIT, per the `LICENSE` file.
