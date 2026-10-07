"""Model calls with record and replay (REQ-T2, GEN-2).

Every real response is saved under `runs/recordings/`, keyed by a fingerprint of the exact request and
model settings. Replay mode (the default) reads only those files, so a reviewer can rerun everything
without an API key. Results are labelled LIVE (a new call) or REPLAYED (a saved real response).
"""

from __future__ import annotations

import hashlib
import json
import os
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from qa.dataset import ROOT

RECORDINGS_DIR = ROOT / "runs" / "recordings"
SETTINGS_PATH = ROOT / "config" / "models.toml"
RECORDING_FORMAT = 1


class ModelCallError(Exception):
    """A model call that produced no usable reply; `reason` becomes the item's visible error reason."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class ModelSettings:
    provider: str
    model: str
    thinking_level: str
    timeout_ms: int
    retry_attempts: int


@dataclass(frozen=True)
class ModelRequest:
    """One call: instructions (from a prompt file) and data (JSON) travel in separate messages (REQ-T1)."""

    call_type: str
    prompt_file: str
    system: str
    user: str
    schema: dict


@dataclass(frozen=True)
class ModelReply:
    text: str
    label: str
    fingerprint: str
    model: str
    recorded_at: str


class ModelClient(Protocol):
    """Anything that answers a model request: the replay and record clients here, a simulated one in tests."""

    def call(self, request: ModelRequest) -> ModelReply: ...


def load_settings(path: Path = SETTINGS_PATH) -> ModelSettings:
    return ModelSettings(**tomllib.loads(path.read_text()))


def fingerprint(request: ModelRequest, settings: ModelSettings) -> str:
    """Same request and model settings give the same fingerprint, so a repeat replays the saved reply."""
    key = {
        "call_type": request.call_type,
        "provider": settings.provider,
        "model": settings.model,
        "thinking_level": settings.thinking_level,
        "system": request.system,
        "user": request.user,
        "schema": request.schema,
    }
    return hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()


class ReplayClient:
    """Serves saved real responses only. It never reads `.env` and never imports the provider SDK."""

    def __init__(self, settings: ModelSettings | None = None, recordings_dir: Path = RECORDINGS_DIR) -> None:
        self.settings = settings or load_settings()
        self.recordings_dir = recordings_dir

    def call(self, request: ModelRequest) -> ModelReply:
        path = self._path(request)
        if not path.exists():
            raise ModelCallError(
                "no_recording", "No saved response for this exact request; run with QA_MODE=record"
            )
        return _reply_from(json.loads(path.read_text()), "REPLAYED")

    def _path(self, request: ModelRequest) -> Path:
        fp = fingerprint(request, self.settings)
        return self.recordings_dir / f"{request.call_type}-{fp[:16]}.json"


class RecordingClient(ReplayClient):
    """Replays when a recording exists; otherwise calls Gemini once and saves the response, valid or not."""

    def __init__(self, settings: ModelSettings | None = None, recordings_dir: Path = RECORDINGS_DIR) -> None:
        super().__init__(settings, recordings_dir)
        self._client = _gemini_client(self.settings)

    def call(self, request: ModelRequest) -> ModelReply:
        path = self._path(request)
        if path.exists():
            return _reply_from(json.loads(path.read_text()), "REPLAYED")
        record = self._record(request)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        return _reply_from(record, "LIVE")

    def _record(self, request: ModelRequest) -> dict:
        from google.genai import errors, types
        from httpx import HTTPError

        config = types.GenerateContentConfig(
            system_instruction=request.system,
            response_mime_type="application/json",
            response_json_schema=request.schema,
            thinking_config=types.ThinkingConfig(thinking_level=self.settings.thinking_level),
        )
        try:
            response = self._client.models.generate_content(
                model=self.settings.model, contents=request.user, config=config
            )
        except (errors.APIError, HTTPError) as exc:
            raise ModelCallError("api_failure", f"Gemini call failed: {exc}") from exc
        return _recording(request, self.settings, response)


def make_client(mode: str | None = None) -> ReplayClient:
    """QA_MODE=replay (default) or QA_MODE=record."""
    mode = mode or os.environ.get("QA_MODE") or "replay"
    if mode == "record":
        return RecordingClient()
    if mode == "replay":
        return ReplayClient()
    raise ValueError(f"QA_MODE must be 'replay' or 'record', not {mode!r}")


def _gemini_client(settings: ModelSettings):
    """Built only in record mode; the key comes from the environment (or .env), never printed or saved."""
    from dotenv import load_dotenv
    from google import genai
    from google.genai import types

    load_dotenv(ROOT / ".env")
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        raise RuntimeError(
            "Record mode needs GOOGLE_API_KEY (or GEMINI_API_KEY) in the environment or in .env"
        )
    options = types.HttpOptions(
        timeout=settings.timeout_ms, retry_options=types.HttpRetryOptions(attempts=settings.retry_attempts)
    )
    return genai.Client(http_options=options)


def _recording(request: ModelRequest, settings: ModelSettings, response) -> dict:
    """Only these fields are saved: no headers, no key, no local paths."""
    candidate = response.candidates[0] if response.candidates else None
    finish = getattr(candidate.finish_reason, "name", str(candidate.finish_reason)) if candidate else "NONE"
    usage = response.usage_metadata
    system_sha = hashlib.sha256(request.system.encode()).hexdigest()
    return {
        "format": RECORDING_FORMAT,
        "fingerprint": fingerprint(request, settings),
        "call_type": request.call_type,
        "provider": settings.provider,
        "model": settings.model,
        "thinking_level": settings.thinking_level,
        "prompt_file": request.prompt_file,
        "prompt_sha256": system_sha,
        "request": {"system": request.system, "user": request.user, "schema": request.schema},
        "response": {
            "text": response.text or "",
            "finish_reason": finish,
            "model_version": response.model_version,
            "response_id": response.response_id,
            "usage": {
                "prompt_token_count": usage.prompt_token_count if usage else None,
                "candidates_token_count": usage.candidates_token_count if usage else None,
                "thoughts_token_count": usage.thoughts_token_count if usage else None,
            },
        },
        "recorded_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def _reply_from(record: dict, label: str) -> ModelReply:
    """A reply that did not finish normally is an error, also when replayed, so real failures reproduce."""
    finish = record["response"]["finish_reason"]
    if finish != "STOP":
        raise ModelCallError("invalid_model_output", f"The model stopped with finish reason {finish}")
    return ModelReply(
        record["response"]["text"], label, record["fingerprint"], record["model"], record["recorded_at"]
    )
