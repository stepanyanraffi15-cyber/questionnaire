#!/usr/bin/env python3
"""PreToolUse hook: the few protections that must never depend on the agent's judgement.

1. Supplied inputs (starter-pack/, data/seed/) are never edited by the agent.
2. The hand-written answer key (reference/) is edited only when the human starts the session with
   QA_ALLOW_REFERENCE_EDIT=1, so a failing check can't be "fixed" by changing the expected answers.
3. Secrets in .env are never read or written by the agent (.env.example is fine).
4. Local-only files (.private/, CLAUDE.local.md) are never staged or force-added to git.

Edit/Write tools are checked exactly by path. Shell commands are checked only for explicit writes into a
protected path (a redirect, tee, rm, mv, sed -i, truncate whose target is protected); reading is always allowed.
Anything subtler is caught by git: every protected file is tracked, so `git diff` shows changes.

Exit code 2 blocks the tool call; the message on stderr is shown to the agent.
"""

from __future__ import annotations

import json
import os
import re
import sys

ALWAYS = ("starter-pack/", "data/seed/")
KEY = "reference/"
PROTECTED_RE = r"(?:\./)?(?:starter-pack|data/seed|reference)/"
# A write whose *target* is a protected path. Redirects to /dev/null or to another stream (2>&1) never match.
SHELL_WRITE = re.compile(
    r"(?:>>?|\btee(?:\s+-a)?)\s*['\"]?"
    + PROTECTED_RE
    + r"|\b(?:rm|mv|truncate|sed\s+-i\S*)\b[^|;&]*?\s['\"]?"
    + PROTECTED_RE
)
ENV_FILE = re.compile(r"(?:^|[\s/'\"=<])\.env(?![\w.])")
GIT_ADD = re.compile(r"\bgit\s+add\b")


def block(msg: str) -> None:
    print(f"BLOCKED by .claude/hooks/protect_paths.py: {msg}", file=sys.stderr)
    sys.exit(2)


def relative(path: str, root: str) -> str:
    full = os.path.normpath(path if os.path.isabs(path) else os.path.join(root, path))
    root = os.path.normpath(root)
    return os.path.relpath(full, root).replace(os.sep, "/") if full.startswith(root) else full


def check_edit(path: str, root: str) -> None:
    rel = relative(path, root)
    if rel.startswith(ALWAYS):
        block(f"{path} is supplied input and is never edited")
    if rel.startswith(KEY) and os.environ.get("QA_ALLOW_REFERENCE_EDIT") != "1":
        block(
            f"{path} is the hand-written answer key; the human must start the session with QA_ALLOW_REFERENCE_EDIT=1"
        )


def check_shell(cmd: str) -> None:
    if ENV_FILE.search(cmd):
        block("shell commands must not touch .env (secrets); use .env.example for names")
    if GIT_ADD.search(cmd) and re.search(r"\s(?:-f|--force)\b|\.private|CLAUDE\.local\.md", cmd):
        block("local-only files must never be staged, and ignored files must never be force-added")
    match = SHELL_WRITE.search(cmd)
    if match:
        target_is_key = "reference/" in match.group(0)
        if not (target_is_key and os.environ.get("QA_ALLOW_REFERENCE_EDIT") == "1"):
            block(f"command writes into a protected path: {match.group(0).strip()!r}")


def main() -> None:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    inp = data.get("tool_input") or {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()

    if tool in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = inp.get("file_path") or inp.get("notebook_path") or ""
        if os.path.basename(path) == ".env":
            block(".env holds secrets; use .env.example for variable names")
        if path and tool != "Read":
            check_edit(path, root)
    elif tool == "Bash":
        check_shell(inp.get("command", ""))


if __name__ == "__main__":
    main()
