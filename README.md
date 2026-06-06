# Overseer

> A second brain you reason *with*. Drop in what you know about yourself, the people around you, and a
> huge body of work; it folds everything into one living graph — your roadmap and your network as one
> thing — and answers like a counsellor who has read all of it and is on your side.

It is plain files plus one protocol, `OVERSEER.md`. **There is no application code.** Claude Code is the
engine: it reads your corpus, builds and maintains the graph in `brain/`, and reasons over it. The whole
design exists to keep that cheap as the corpus grows — you don't pay for your whole life to ask one
question.

This is the merge of three tools, fused not bolted: **the Factory** (a working memory in files, taken
past a flat pile of notes), **auspex** (provenance, what-changed, the people-graph, the refusals — kept
as discipline, not as its old Rust pipeline), and **synthesis** (ingest anything, ground every claim,
Whisper as a sensor that just feeds the data). The thing none of them had alone: a standing model of
*you* that gets smarter and stays small as it grows.

## Start

Two ways in — the same brain underneath.

```bash
# A) the webview — a dashboard you don't have to manage a terminal for:
./launch.sh web                  # → open http://127.0.0.1:8787
#   see the digest + journal, click through the graph, and ask / fold / focus / drop — all in one page.

# B) a Claude Code session in this folder — the raw engine:
./launch.sh                      # git-inits brain/, then tells you what to do
# 1. put files in corpus/  (self/  network/  your usernames+who's who  work/  the big pile)
# 2. for live capture, have any Whisper tool write `ts | speaker | text` lines into inbox/
# 3. say:  "fold"        → it builds the brain
#    then: ask it anything → it answers as your second brain
```

Try the test the seed ships with: **"given everything, what should I focus on this week?"** Then replace
the synthetic seed in `brain/` with your own life and ask it again.

The webview is the **expression layer** (`web/`): a thin local viewer + remote control that *shows* the
brain, *writes* to `inbox/`, and *runs* headless Claude Code for you. It adds no intelligence — deleting
`web/` loses nothing. See `web/README.md`.

## What's where

```
OVERSEER.md   the operating manual — read it; it is the entire program
brain/        your second self: index.md (router + digest) · nodes/ (one graph) · journal.md · shards/
corpus/       your raw material, untouched (self/ network/ work/ are just intake hints)
inbox/        new material to fold; the place Whisper drops transcripts
```

## Honest trust model

Your files stay on disk, but folding them puts them into Claude's context, and web enrichment sends
*generic* queries out (never your names, handles, or secrets — see `OVERSEER.md`). This is not an
airgapped tool; it is a private one that is careful about what leaves. Credentials are stripped before
anything is recorded. `brain/` is yours to keep local or commit.

MIT.
