# web/ — the expression layer

A face for the second brain, so you don't have to live in a terminal or open folders by hand. It is a
thin local viewer + a remote control for the engine — **it adds no intelligence.**

It does exactly three things:
1. **shows** `brain/` (the digest, the journal, and any card) — rendered verbatim, never recomputed.
2. **writes** what you drop into `inbox/`.
3. **runs** headless Claude Code (`claude -p`) for you — fold, ask, focus — and streams the answer.

`brain/` is still the only source of truth. **Deleting `web/` loses nothing** — that is the test every
line here passes: no server-side state, no cache of the brain, no computed score, status, or ranking.

## Run

```bash
./launch.sh web            # or:  python3 web/serve.py
# → open http://127.0.0.1:8787
```

The page is one screen: the **digest** (your `brain/index.md`) on the left, the **journal** ("what
changed", newest first) on the right, a persistent bar to **ask / fold / focus / drop**, and an opt-in
**graph** of the node space. Click any `type:slug` to open its card; click a card's links to traverse;
click a `shard:` to read the source summary.

The buttons shell out to `claude -p` in this folder — Claude Code is the engine, the same one your
terminal uses, driven by `OVERSEER.md`. If the `claude` CLI isn't on your PATH, Fold/Ask **stage** the
request into `inbox/.pending/` instead of running, and tell you so (they never pretend it ran).

## The bright lines (why this isn't a regression to the old engine)

- The server may only **serve `brain/` files**, **write `inbox/`**, and **spawn `claude -p`**. Nothing else.
- The only arithmetic anywhere in `web/` is force-graph coordinates. Every number, date, and status you
  see is a string the brain authored.
- The server never assembles context for the model: `ask` sends your raw question, with nothing
  prepended — Claude forms its own read plan, so cost still scales with the question, not the corpus.
- It writes to exactly one place: `inbox/`. It never edits `brain/`, `.claude/`, or `OVERSEER.md`.
  Folding `inbox → brain` is only ever `claude -p "fold"`.

## Security & trust

Localhost-only (binds `127.0.0.1`), Host-checked, and every action that changes anything requires a
per-launch CSRF token. The prompt is passed to `claude` as a single argument (no shell), uploads are
size-capped and renamed server-side, and file reads are locked to `brain/`. The headless engine runs
under `../.claude/settings.json` — it may edit `brain/` and search the web, but not delete files, run
network tools, or touch `OVERSEER.md`/`.claude/`.

Honest trust model (same as `OVERSEER.md`): this is **not airgapped**. Reading your corpus puts it into
Claude's context, and web enrichment sends *generic* queries out (never your names, handles, or secrets).
For stronger isolation, run the server (and thus `claude`) under an OS sandbox — see the note in
`OVERSEER.md`. The UI never claims more privacy than the engine actually has.
