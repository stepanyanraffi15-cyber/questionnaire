# CLAUDE.md — Questionnaire Evidence & Review Workspace

Take-home assignment (Alternative C): a local workspace that drafts cited answers to buyer questionnaire questions
from fictional product documents, routes unresolved questions to a reviewer, and reuses only approved answers.
The assignment brief and the working plan are provided locally; local instructions say where.

## Non-negotiables (from the assignment and its exercise rules)

- Apply the four rules in `data/seed/domain.md` exactly. Never add, soften or reinterpret a rule silently; if a rule
  is unclear, state the ambiguity and record a decision in `docs/decisions/`.
- Expected results (the answer key) are derived by reading the passages and metadata, stored in `reference/`, and
  never produced from application output. The grader must not import application code.
- Keep document text separate from application instructions.
- Keep model-generated suggestions separate from approved answers; only approved answers are reused.
- Save real model responses and the prompt/model configuration; replay must work without an API key; label live,
  replayed and simulated results.
- Report failed checks honestly; label simulations; state limitations.
- Never read, print or commit `.env`. Variable names go in `.env.example`.
- Never force-add ignored files. Local-only material stays out of git and is never linked from public files.
- Required functionality before optional enhancements.

## Clean code

Readable over clever. Small single-purpose functions, clear names, type hints, docstrings that explain *why*,
no dead or commented-out code, no duplicated logic, explicit and visible errors, `ruff` format + lint clean, tests
that check behaviour. If a piece is hard to explain in two sentences, simplify it.

## Protected paths (enforced by `.claude/hooks/protect_paths.py`)

| Path | Rule |
|---|---|
| `starter-pack/**` | Never edit — unchanged copy of the supplied material. |
| `data/seed/**` | Never edit — copy of the supplied `tasks/evidence/`. |
| `reference/**` | Edit only when the human starts the session with `QA_ALLOW_REFERENCE_EDIT=1`. |
| `.env` | Never read or write. |

## Where things go

| What | Where |
|---|---|
| Decisions (incl. ambiguity resolutions) | `docs/decisions/NNN-title.md` (template in that folder) |
| Research notes and bibliography | `docs/research/` |
| Data additions + how they were made | `data/additions/`, `data/changes/`, `data/GENERATION.md` |
| Answer key + grader | `reference/` (protected) |
| Saved real model responses | `runs/` (committed) |
| AI configuration record | `ai-workflow/` (templates until completed and renamed) |

The layout of application code is decided during implementation; record it in a decision and in the README.

## Tools in this repo

- `uv` (`uv sync`, `uv run …`). Dependencies in `pyproject.toml` are placeholders from planning — change them if the
  design needs to and update `uv.lock`.
- Subagents: `researcher` (read-only research → `docs/research/`), `verifier` (independent review, no edits).
- Skill: `.claude/skills/generate-assignment-data/` from the starter pack (its `tasks/<task>/` = `data/seed/` here).
- Record which of these were actually used — the submission must mark used / not-used honestly.
