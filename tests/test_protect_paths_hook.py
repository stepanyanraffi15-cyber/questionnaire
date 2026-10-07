"""Tests for .claude/hooks/protect_paths.py: what it must block and what it must allow."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "protect_paths.py"


def run_hook(tool: str, tool_input: dict, unlock_key: bool = False) -> int:
    env = {k: v for k, v in os.environ.items() if k != "QA_ALLOW_REFERENCE_EDIT"}
    env["CLAUDE_PROJECT_DIR"] = str(ROOT)
    if unlock_key:
        env["QA_ALLOW_REFERENCE_EDIT"] = "1"
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input})
    return subprocess.run(
        [sys.executable, str(HOOK)], input=payload, text=True, env=env, capture_output=True, check=False
    ).returncode


BLOCKED, ALLOWED = 2, 0


@pytest.mark.parametrize(
    ("tool", "tool_input", "expected"),
    [
        # supplied inputs and answer key: edit tools
        ("Edit", {"file_path": "data/seed/seed.json"}, BLOCKED),
        ("Write", {"file_path": "starter-pack/README.md"}, BLOCKED),
        ("Write", {"file_path": "reference/expected.json"}, BLOCKED),
        ("Write", {"file_path": "src/qa/load.py"}, ALLOWED),
        ("Read", {"file_path": "data/seed/seed.json"}, ALLOWED),
        # secrets
        ("Read", {"file_path": ".env"}, BLOCKED),
        ("Read", {"file_path": ".env.example"}, ALLOWED),
        ("Bash", {"command": "cat .env"}, BLOCKED),
        ("Bash", {"command": "source .env && uv run pytest"}, BLOCKED),
        ("Bash", {"command": "diff .env.example ai-workflow/.env.example"}, ALLOWED),
        # reading protected paths from the shell is always fine
        ("Bash", {"command": "ls data/seed/ 2>&1"}, ALLOWED),
        ("Bash", {"command": "cat data/seed/domain.md 2>/dev/null"}, ALLOWED),
        ("Bash", {"command": "jq '.questions | length > 3' data/seed/seed.json"}, ALLOWED),
        ("Bash", {"command": "cp data/seed/seed.json /tmp/x.json"}, ALLOWED),
        ("Bash", {"command": "python3 -c \"print(ord('a')>127)\" data/seed/seed.json"}, ALLOWED),
        # explicit writes into protected paths
        ("Bash", {"command": "echo x > data/seed/domain.md"}, BLOCKED),
        ("Bash", {"command": "echo x >> reference/expected.json"}, BLOCKED),
        ("Bash", {"command": "echo x | tee starter-pack/README.md"}, BLOCKED),
        ("Bash", {"command": "sed -i s/no/yes/ reference/expected.json"}, BLOCKED),
        ("Bash", {"command": "rm data/seed/seed.json"}, BLOCKED),
        ("Bash", {"command": "mv data/seed/seed.json /tmp/"}, BLOCKED),
        # git: local-only files never staged
        ("Bash", {"command": "git add -f .private/PLAN.md"}, BLOCKED),
        ("Bash", {"command": "git add CLAUDE.local.md"}, BLOCKED),
        ("Bash", {"command": "git add --force docs"}, BLOCKED),
        ("Bash", {"command": "git add -A && git commit -m x"}, ALLOWED),
    ],
)
def test_hook_decisions(tool: str, tool_input: dict, expected: int) -> None:
    assert run_hook(tool, tool_input) == expected


def test_answer_key_unlocked_by_human_flag() -> None:
    assert run_hook("Write", {"file_path": "reference/expected.json"}, unlock_key=True) == ALLOWED
    assert run_hook("Bash", {"command": "echo x > reference/notes.md"}, unlock_key=True) == ALLOWED


def test_seed_stays_locked_even_with_flag() -> None:
    assert run_hook("Edit", {"file_path": "data/seed/seed.json"}, unlock_key=True) == BLOCKED
