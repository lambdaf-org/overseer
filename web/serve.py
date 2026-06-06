#!/usr/bin/env python3
"""
Overseer — the expression layer (a thin local viewer + remote control).

This server adds ZERO intelligence. It does exactly three things:
  1. SERVE raw brain/ files for display (read-only).
  2. WRITE dropped notes/files into inbox/.
  3. SPAWN headless `claude -p` — the real engine — and stream its output back.

It never computes a ranking, score, status, urgency, or insight. brain/ is the only
source of truth; this whole directory (web/) is deletable with zero loss. If you ever
find a function here named compute/rank/score/infer/diff/warmth/urgency, it has
regressed into the rejected v1 architecture — delete it.

stdlib only. No pip, no Node, no build step.  Run:  python3 web/serve.py
"""
import json
import os
import re
import secrets
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ── paths (everything is relative to the overseer root, one level up from web/) ──
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # the overseer/ folder
BRAIN = os.path.join(ROOT, "brain")
NODES = os.path.join(BRAIN, "nodes")
INBOX = os.path.join(ROOT, "inbox")
PENDING = os.path.join(INBOX, ".pending")
INDEX_HTML = os.path.join(HERE, "index.html")

HOST = "127.0.0.1"
PORT = int(os.environ.get("OVERSEER_PORT", "8787"))
CSRF = secrets.token_urlsafe(32)                  # minted once per launch

MAX_UPLOAD = 5 * 1024 * 1024                       # 5 MB per dropped file
MAX_INBOX_FILES = 1000                             # refuse to fill the disk
MAX_PENDING_FILES = 200                            # bound the staged-request fallback too
RUN_TIMEOUT = 1800                                 # hard cap on one claude run (s)
GRAPH_CAP = 60                                     # "too big to draw — narrow focus"

RUN_LOCK = threading.Lock()                        # single-flight: one claude at a time

# The ONLY mode→prompt mapping. The client never sends a prompt template; for `ask`
# we pass the user's raw question with NO brain context prepended (Claude forms its own
# read plan per OVERSEER.md — prepending context would defeat the token-economy law).
PROMPTS = {
    "fold": "fold",
    "focus": "Give me the standing-watch briefing — given everything, what should I "
             "focus on this week? Follow the ASK ritual in OVERSEER.md.",
}


# ── path safety ──────────────────────────────────────────────────────────────
def safe_join(base, rel):
    """Resolve rel under base, or raise. Defeats ../, symlinks, NUL, abs paths."""
    if "\x00" in rel:
        raise ValueError("nul byte")
    target = os.path.realpath(os.path.join(base, rel))
    base_r = os.path.realpath(base)
    if target != base_r and not target.startswith(base_r + os.sep):
        raise ValueError("path escapes base")
    return target


# ── dumb, local tokenizers (presentation only — never infer state) ───────────
CARD_RE = re.compile(r"^###\s+([a-z]+:[a-z0-9-]+)\s*(?:·\s*(.+))?$")
LINK_RE = re.compile(r"^\s*-\s*([a-z][a-z-]*)\s*→\s*([a-z]+:[a-z0-9-]+)")
PROV_RE = re.compile(r"(corpus/[^\s\"']+|shard:[a-z0-9-]+|https?://[^\s\"']+)")


def card_type(node_id):
    return node_id.split(":", 1)[0] if ":" in node_id else "node"


def iter_node_files():
    for dirpath, _, files in os.walk(NODES):
        for f in sorted(files):
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)


def slice_card(node_id):
    """Return the raw markdown of ONE `### <id> · <type>` block, or None."""
    for path in iter_node_files():
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
        for i, line in enumerate(lines):
            m = CARD_RE.match(line.strip())
            if m and m.group(1) == node_id:
                block = [line]
                for nxt in lines[i + 1:]:
                    if nxt.startswith("### "):
                        break
                    block.append(nxt)
                return "".join(block).strip()
    return None


def parse_card(node_id, raw):
    links, aliases, provs = [], [], []
    for line in raw.splitlines():
        lm = LINK_RE.match(line)
        if lm:
            links.append({"pred": lm.group(1), "to": lm.group(2)})
        s = line.strip()
        if s.lower().startswith("aliases:"):
            aliases += [a.strip().strip('"') for a in s[8:].split(",") if a.strip()]
        if s.lower().startswith("provenance:"):
            provs += PROV_RE.findall(s)
    return {"id": node_id, "type": card_type(node_id), "raw": raw,
            "links": links, "aliases": aliases, "provenance": provs}


def seeds_from_index():
    """Default graph seeds = the node ids literally named in index.md (heads + circle)."""
    try:
        with open(os.path.join(BRAIN, "index.md"), encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return []
    seen, out = set(), []
    for m in re.finditer(r"\b([a-z]+:[a-z0-9-]+)\b", text):
        nid = m.group(1)
        # ignore false positives like http: by requiring the id resolves to a card
        if nid not in seen and ":" in nid and not nid.startswith(("http", "shard")):
            seen.add(nid)
            out.append(nid)
    return out


def walk_subgraph(seed_ids, depth):
    """BFS the touched subgraph, reading one card at a time. No globbing everything,
    no metrics — just collect the nodes and labelled edges actually reached."""
    nodes, edges, seen = {}, [], set()
    frontier = [s for s in seed_ids if s]
    for s in frontier:
        seen.add(s)
    for _ in range(max(0, depth)):
        nxt = []
        for nid in frontier:
            if len(nodes) > GRAPH_CAP:
                break
            raw = slice_card(nid)
            if raw is None:
                nodes.setdefault(nid, {"id": nid, "type": card_type(nid), "missing": True})
                continue
            nodes[nid] = {"id": nid, "type": card_type(nid)}
            for ln in parse_card(nid, raw)["links"]:
                edges.append({"from": nid, "pred": ln["pred"], "to": ln["to"]})
                if ln["to"] not in seen:
                    seen.add(ln["to"])
                    nxt.append(ln["to"])
        frontier = nxt
        if not frontier:
            break
    # include endpoints that were referenced but not expanded
    for e in edges:
        nodes.setdefault(e["to"], {"id": e["to"], "type": card_type(e["to"])})
    return {"nodes": list(nodes.values()), "edges": edges,
            "capped": len(nodes) > GRAPH_CAP}


def all_node_ids():
    ids = []
    for path in iter_node_files():
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                m = CARD_RE.match(line.strip())
                if m:
                    ids.append(m.group(1))
    return ids


# ── headless claude (the engine) ─────────────────────────────────────────────
def stage_pending(prompt):
    os.makedirs(PENDING, exist_ok=True)
    try:
        if len(os.listdir(PENDING)) >= MAX_PENDING_FILES:
            return "(staging area full — clear inbox/.pending/)"
    except OSError:
        pass
    name = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + secrets.token_hex(3) + ".txt"
    dest = safe_join(PENDING, name)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(prompt + "\n")
    return os.path.relpath(dest, ROOT)


def sse(wfile, obj):
    wfile.write(b"data: " + json.dumps(obj).encode("utf-8") + b"\n\n")
    wfile.flush()


def run_claude(prompt, wfile):
    """Spawn `claude -p PROMPT` (argv list, shell=False) and SSE-stream its text.
    The prompt is a single argv element, so shell metacharacters are inert."""
    if shutil.which("claude") is None:
        rel = stage_pending(prompt)
        sse(wfile, {"type": "staged", "path": rel,
                    "text": "`claude` CLI not found on PATH. I staged this request to "
                            + rel + " — run it from a Claude Code session in this folder."})
        sse(wfile, {"type": "done", "ok": False})
        return

    cmd = ["claude", "-p", prompt,
           "--output-format", "stream-json", "--verbose", "--include-partial-messages"]
    proc = subprocess.Popen(
        cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, start_new_session=True)  # own process group → killable

    def killpg(sig):
        try:
            os.killpg(os.getpgid(proc.pid), sig)
        except (ProcessLookupError, PermissionError):
            pass

    # Hard cap that fires even when claude is SILENT (readline() would block forever
    # otherwise). Killing the group makes readline() return EOF, so the loop exits, the
    # RUN_LOCK is released, and no orphaned engine is left alive.
    timed_out = {"v": False}
    watchdog = threading.Timer(RUN_TIMEOUT, lambda: (timed_out.__setitem__("v", True), killpg(signal.SIGKILL)))
    watchdog.daemon = True
    watchdog.start()

    got_text = False
    assert proc.stdout is not None
    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            txt = _text_delta(ev)
            if txt:
                got_text = True
                sse(wfile, {"type": "token", "text": txt})
            elif ev.get("type") == "result" and not got_text:
                # no streamed deltas (older CLI) — emit the final result text once
                r = ev.get("result") or ""
                if r:
                    got_text = True
                    sse(wfile, {"type": "token", "text": r})
        proc.wait(timeout=10)
    except (BrokenPipeError, ConnectionResetError):
        killpg(signal.SIGTERM)        # browser navigated away → reap the engine
    except subprocess.TimeoutExpired:
        killpg(signal.SIGKILL)
    finally:
        watchdog.cancel()
        if proc.poll() is None:
            killpg(signal.SIGTERM)
    # always tell the client we're done, so it never hangs on "thinking…"
    try:
        if timed_out["v"]:
            sse(wfile, {"type": "error", "text": "run exceeded the time limit and was stopped."})
        elif proc.returncode not in (0, None) and not got_text:
            rel = stage_pending(prompt)
            sse(wfile, {"type": "error",
                        "text": "claude exited with an error and produced no output (auth? "
                                "permissions?). Staged the request to " + rel + "."})
        sse(wfile, {"type": "done", "ok": got_text})
    except (BrokenPipeError, ConnectionResetError):
        pass


def _text_delta(ev):
    """Extract a streamed text token from a stream-json event. With
    --include-partial-messages the engine streams the full reply as text_delta events;
    we deliberately do NOT also read the final `assistant` message block (that would
    re-emit the whole answer and render it twice). The `result` fallback above covers
    older CLIs that don't stream deltas at all."""
    if ev.get("type") == "stream_event":
        delta = (ev.get("event") or {}).get("delta") or {}
        if delta.get("type") == "text_delta":
            return delta.get("text") or ""
    return ""


# ── HTTP ─────────────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    server_version = "Overseer/expression"

    def log_message(self, format, *args):  # quiet
        return

    # -- guards --
    def _host_ok(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost")

    def _post_ok(self):
        if not self._host_ok():
            return False
        origin = self.headers.get("Origin") or self.headers.get("Referer") or ""
        if origin:
            netloc = urllib.parse.urlparse(origin).hostname
            if netloc not in ("127.0.0.1", "localhost"):
                return False
        return self.headers.get("X-CSRF-Token") == CSRF

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    # -- GET --
    def do_GET(self):
        if not self._host_ok():
            return self._send(403, {"error": "bad host"})
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        try:
            if u.path == "/":
                return self._serve_index()
            if u.path == "/api/file":
                return self._api_file(q.get("path", [""])[0])
            if u.path.startswith("/api/node/"):
                return self._api_node(urllib.parse.unquote(u.path[len("/api/node/"):]))
            if u.path == "/api/graph":
                return self._api_graph(q)
            return self._send(404, {"error": "not found"})
        except ValueError as e:
            return self._send(400, {"error": str(e)})
        except Exception as e:  # never leak a path/stack trace to the browser
            sys.stderr.write("overseer: GET error: %s\n" % e)
            return self._send(500, {"error": "server error"})

    def _serve_index(self):
        with open(INDEX_HTML, encoding="utf-8") as fh:
            page = fh.read().replace("__CSRF_TOKEN__", CSRF)
        self._send(200, page, "text/html; charset=utf-8")

    def _api_file(self, rel):
        # rel already came url-decoded from parse_qs; do NOT decode again (avoids the
        # %252e double-encode trick). safe_join is the real confinement either way.
        if not rel.endswith(".md"):
            raise ValueError("only .md files")
        path = safe_join(BRAIN, rel)             # whitelisted to brain/ ONLY
        if not os.path.isfile(path):
            return self._send(404, {"error": "no such file"})
        with open(path, encoding="utf-8") as fh:
            self._send(200, fh.read(), "text/markdown; charset=utf-8")

    def _api_node(self, node_id):
        if not CARD_RE.match("### " + node_id):
            raise ValueError("bad id")
        raw = slice_card(node_id)
        if raw is None:
            return self._send(404, {"error": "no such node", "id": node_id})
        self._send(200, parse_card(node_id, raw))

    def _api_graph(self, q):
        focus = q.get("focus", [""])[0]
        depth = max(1, min(4, int(q.get("depth", ["2"])[0] or 2)))
        if focus == "all":
            ids = all_node_ids()
            if len(ids) > GRAPH_CAP:
                return self._send(200, {"nodes": [], "edges": [], "capped": True,
                                        "count": len(ids)})
            return self._send(200, walk_subgraph(ids, 1))
        seeds = [s for s in focus.split(",") if s] or seeds_from_index()
        self._send(200, walk_subgraph(seeds, depth))

    # -- POST --
    def do_POST(self):
        if not self._post_ok():
            return self._send(403, {"error": "forbidden (host/origin/csrf)"})
        u = urllib.parse.urlparse(self.path)
        try:
            if u.path == "/api/inbox":
                return self._api_inbox()
            if u.path == "/api/run":
                return self._api_run()
            return self._send(404, {"error": "not found"})
        except ValueError as e:
            return self._send(400, {"error": str(e)})

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_UPLOAD:
            raise ValueError("payload too large")
        return self.rfile.read(n)

    def _api_inbox(self):
        os.makedirs(INBOX, exist_ok=True)
        if len([f for f in os.listdir(INBOX) if not f.startswith(".")]) >= MAX_INBOX_FILES:
            raise ValueError("inbox is full — fold and clear it first")
        raw = self._body()
        ctype = self.headers.get("Content-Type", "")
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        # We accept either a JSON note {text,label} or a raw file upload. We DISCARD any
        # client filename and generate the name ourselves. No classification/typing.
        if ctype.startswith("application/json"):
            data = json.loads(raw or b"{}")
            text = (data.get("text") or "").strip()
            if not text:
                raise ValueError("empty note")
            label = re.sub(r"[^a-z0-9-]+", "-", (data.get("label") or "note").lower())[:32]
            name = f"{ts}-{label or 'note'}.md"
            content = text.encode("utf-8")
        else:
            label = re.sub(r"[^a-z0-9-]+", "-",
                           (self.headers.get("X-Filename-Label") or "drop").lower())[:32]
            name = f"{ts}-{label or 'drop'}.txt"
            content = raw
        dest = safe_join(INBOX, name)            # realpath under inbox/ ONLY
        with open(dest, "wb") as fh:
            fh.write(content)
        self._send(200, {"written": os.path.relpath(dest, ROOT)})

    def _api_run(self):
        data = json.loads(self._body() or b"{}")
        mode = data.get("mode")
        if mode in PROMPTS:
            prompt = PROMPTS[mode]
        elif mode == "ask":
            prompt = (data.get("question") or "").strip()
            if not prompt:
                raise ValueError("empty question")
        else:
            raise ValueError("bad mode")
        if not RUN_LOCK.acquire(blocking=False):
            return self._send(409, {"error": "a run is already in progress"})
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            run_claude(prompt, self.wfile)
        finally:
            RUN_LOCK.release()


def main():
    if not os.path.isdir(BRAIN):
        sys.exit("No brain/ found next to web/. Run from inside the overseer/ folder.")
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)   # 127.0.0.1 ONLY, never ''
    url = f"http://{HOST}:{PORT}/"
    print(f"\n  Overseer is looking at you.  →  {url}")
    print("  (the brain is the truth; this window is just a window. Ctrl-C to close it.)\n")
    if shutil.which("claude") is None:
        print("  note: `claude` CLI not on PATH — Fold/Ask will stage requests instead of running.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  closed.\n")


if __name__ == "__main__":
    main()
