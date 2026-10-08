# 029 · Record real model responses and replay them by exact fingerprint

- Status: accepted
- Requirements: the assignment brief's "Save real model responses and the prompt/model configuration.", "Label cached
  responses and simulated failures so the reviewer can distinguish them from new model calls." and "Handle invalid
  model output, missing references, and API failures visibly."; its submission item "Include a way to replay saved
  real responses without an API key." Ambiguity AMB-28 (replay after an input change).

## Context

A reviewer without an API key must be able to rerun the checks on saved real responses. If a prompt, schema, model or
input changes, an old recording no longer answers the new request; silently reusing a "near" recording would present
an answer to a different request as real.

## Options considered

1. **App-level recordings keyed by a fingerprint of the exact request; a miss is a visible error.**
2. **HTTP cassettes (e.g. vcrpy).** Store headers that can contain credentials; tied to transport details.
3. **Nearest-match replay.** Presents a different request's answer as real.

## Decision

Option 1. `fingerprint` = SHA-256 of canonical JSON over call type, provider, model, thinking level, system text, user
text and schema. Three clients:

- **Replay** (default): reads `runs/recordings/<call_type>-<fp16>.json`, labels results REPLAYED, never loads `.env`
  and never builds the SDK client. A miss gives `error / no_recording`.
- **Record** (`QA_MODE=record`): replays if a recording exists, otherwise calls the model, saves the file and labels
  the result LIVE. Every real response is saved, valid or not.
- **Simulated**: returns hand-written fixture replies labelled SIMULATED and never writes to `runs/`.

A recording holds only: format, fingerprint, call type, question, provider, model, thinking level, repo-relative
prompt file path and its SHA-256, the request (system, user, schema), the response (text, finish reason, model version,
response id, token usage) and the recording time. No headers, keys, absolute paths or email addresses.

### As built (2026-10-08)

The simulated client lives in the tests (`tests/conftest.py`), not in `llm.py`, so application code has no simulated path. Recordings do not store a separate `question` field; the question is inside the saved request.

## Consequences

- Reused approvals are labelled REUSED APPROVAL and make no call.
- An API failure is `error / api_failure`, never "undocumented".
- Any change to prompts, schema or settings needs re-recording; a replay snapshot test detects drift.
- The grader's judge (decision 027) keeps its own prompt and its own saved verdicts and reads them with its own code,
  because the grader must not import application code.

## Evidence

- `data/seed/domain.md` (rules the recorded outputs are checked against).
- `uv.lock` (the SDK version that fixes request and response field names).

## Update (decision 040)

Embeddings for retrieval are recorded the same way: one file per text, `runs/recordings/embed-<fingerprint>.json`,
keyed by the embedding model, its size, the task type and the text. Replay serves them with no key, and a missing one
is the same visible `no_recording` error.
