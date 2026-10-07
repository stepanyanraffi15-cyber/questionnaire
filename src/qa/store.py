"""The workspace state: one JSON file of append-only records, written atomically (REQ-D2, HIRE-2).

Records are only ever appended, so suggestions, approvals and stale marks keep their history. Every record
gets a sequence number (`seq`), which decides what is "newer" even when two actions share a timestamp.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from qa.dataset import ROOT

RECORD_KINDS = ("requests", "suggestions", "reuses", "edits", "notes", "approvals", "stale_marks")


def state_path() -> Path:
    """QA_STATE_DIR picks the state directory (default `state/`, which git ignores)."""
    return Path(os.environ.get("QA_STATE_DIR") or ROOT / "state") / "workspace.json"


def new_state() -> dict:
    return {"seq": 0, "applied_changes": [], **{kind: [] for kind in RECORD_KINDS}}


def load_state(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else new_state()


def save_state(path: Path, state: dict) -> None:
    """Write to a temporary file, then rename: a crash never leaves a half-written state file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w") as handle:
        json.dump(state, handle, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def append(state: dict, kind: str, record: dict) -> dict:
    state["seq"] += 1
    record = {"seq": state["seq"], **record}
    state[kind].append(record)
    return record
