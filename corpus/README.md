# corpus/ — your raw material, untouched

This is the ground truth. Overseer reads it and never edits it. Everything in `brain/` is a re-derivable
index over what's here — if you lost `brain/`, a re-fold rebuilds it from this.

Drop anything readable: PDFs, docx, markdown, code repos, chat exports, notes. Three sub-folders are
**hints**, not rules — Overseer ignores which drawer a file landed in and follows the content:

- `self/` — structured data about you. Who you are, your situation, your values, where you're trying to
  go, your constraints. The more you put here, the less you ever have to re-explain.
- `network/` — the people around you, and **who is who**: declare your own handles and each person's
  aliases so chat exports resolve to one person. A simple way to start:

  ```
  me: sam, sam.rivera, @samr_design
  person:devon = devon_ux, "Devon Ash"   (role: freelance client)
  person:mara  = "Mara Okafor"           (role: thesis advisor)
  ```

  Chat exports work best as one message per line: `YYYY-MM-DD HH:MM | sender | message`.

- `work/` — the big pile. School, projects, code, documents — "seemingly large files about everything."
  This is what the token-economy machinery in `OVERSEER.md` exists to handle: it gets summarised into
  shards and only re-read on demand.

By default `corpus/` is git-ignored (it's private and can be huge). See `.gitignore`.
