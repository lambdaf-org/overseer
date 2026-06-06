# Overseer

> A second brain you reason *with*. Drop in what you know about yourself, the people around you, and a
> huge body of work; it folds everything into one living graph — your roadmap and your network as one
> thing — and answers like a counsellor who has read all of it and is on your side.

Most "second brain" tools are filing cabinets with search. They hand back the note you already wrote and
leave the thinking to you. Overseer takes the opposite position: the notes are not the asset — the
**edges between them are**. This goal is gated by that person's review, which collides with that
deadline, which serves the same goal a third person could unblock. That web is where judgement lives, and
a folder of notes throws it away the moment you file things into separate drawers.

So there is **no application code**, and that is the design, not a missing feature. Overseer is plain
files plus one protocol (`OVERSEER.md`); Claude Code is the engine that reads your corpus, builds the
graph in `brain/`, and reasons over it. Nothing to deploy, no schema to migrate, no model grading its own
homework. The corpus is the only source of truth; `brain/` is a small, re-derivable index over it, kept
deliberately lossy so that one question never costs you your whole archive in tokens — the read scales
with what you asked, not with how much you've stored.

Four things it won't compromise on, because they are where these tools usually cheat:

- **It never stores status.** No `done: true`, no baked "11 days left" — those start lying the instant
  the world moves and you can't see it. It records dated events and works out the state when you ask. If
  nothing on record says you submitted, the honest answer is "I don't know — did you?"
- **Every claim shows its receipt.** A statement about a person or the world carries a quote and a
  pointer back to the source, or it doesn't get written down. No source, no claim.
- **No number it can't defend by counting.** A model that scores its own output is a horoscope with a
  JSON schema. It won't tell you a relationship is 0.71 healthy; it shows you what happened, with dates,
  and lets you judge.
- **It pushes back.** When what you say you want drifts from what your record actually shows, it says so.
  A second brain that only agrees with you is a diary.

It grew out of three earlier tools of mine — one that kept working memory in plain files, one that built
the people-graph and the evidence discipline, one that could ingest anything and ground every claim (with
Whisper as a sensor that just feeds raw capture in). This fuses the three into one, and adds what none of
them had alone: a standing model of *you* that gets sharper, and stays small, as it grows.

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
