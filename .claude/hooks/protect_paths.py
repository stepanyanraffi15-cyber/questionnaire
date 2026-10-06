#!/usr/bin/env python3
"""PreToolUse hook: protect the supplied material and the hand-written answer key.

Why: the coding agent must never "fix" a failing check by editing the inputs or the expected answers.

Rules
- starter-pack/** and data/seed/**  -> never writable by the agent.
- reference/**                      -> writable only if the human started the session with
                                       QA_ALLOW_REFERENCE_EDIT=1.
- .env (not .env.example)           -> never read or written by the agent.
- .private/ and CLAUDE.local.md      -> local-only; never staged, force-added or committed.

Exit code 2 blocks the tool call; the message on stderr is shown to the agent.
The Bash check is a heuristic (it looks for write-like commands that mention a protected path);
it is a guard rail, not a sandbox. Reviewed by a human before enabling.
"""
from __future__ import annotations

import json
import os
import re
import sys

ALWAYS = ("starter-pack/", "data/seed/")
KEY = ("reference/",)
ENV_RE = re.compile(r"(^|[\s/'\"=])\.env(?!\.example)(\b|$)")


def rel(path: str, root: str) -> str:
    p = os.path.normpath(os.path.join(root, path)) if not os.path.isabs(path) else os.path.normpath(path)
    r = os.path.normpath(root)
    return os.path.relpath(p, r).replace(os.sep, "/") if p.startswith(r) else p


def protected(relpath: str) -> str | None:
    rp = relpath.lstrip("./") if relpath.startswith("./") else relpath
    if any(rp == a.rstrip("/") or rp.startswith(a) for a in ALWAYS):
        return "is supplied material and must never be edited"
    if any(rp == k.rstrip("/") or rp.startswith(k) for k in KEY) and os.environ.get("QA_ALLOW_REFERENCE_EDIT") != "1":
        return "is the hand-written answer key; edit only when the human sets QA_ALLOW_REFERENCE_EDIT=1"
    return None


def is_env(path: str) -> bool:
    base = os.path.basename(path)
    return base == ".env" or (base.startswith(".env.") and base != ".env.example")


def block(msg: str) -> None:
    print(f"BLOCKED by .claude/hooks/protect_paths.py: {msg}", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()

    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit", "Read"):
        path = inp.get("file_path") or inp.get("notebook_path") or ""
        if path and is_env(path):
            block(f"{path} holds secrets; use .env.example for variable names")
        if tool != "Read" and path:
            reason = protected(rel(path, root))
            if reason:
                block(f"{path} {reason}")
        return

    if tool == "Bash":
        cmd = inp.get("command", "")
        if ENV_RE.search(cmd):
            block("shell commands must not touch .env (secrets)")
        if re.search(r"\bgit\s+add\b", cmd) and (
            re.search(r"\s(-f|--force)\b", cmd) or ".private" in cmd or "CLAUDE.local.md" in cmd
        ):
            block("local-only files (.private/, CLAUDE.local.md) must never be staged; do not force-add ignored files")
        writes = re.search(r"(>>?|\btee\b|\brm\b|\bmv\b|\bcp\b|\bsed\s+-i|\btruncate\b|\bchmod\b|\bgit\s+(checkout|restore)\b|\bunlink\b|\bln\b)", cmd)
        if writes:
            for prefix in ALWAYS + KEY:
                if re.search(r"(^|[\s'\"=/])(\./)?" + re.escape(prefix), cmd):
                    reason = protected(prefix)
                    if reason:
                        block(f"command writes near protected path {prefix} ({reason})")
        return


if __name__ == "__main__":
    main()
