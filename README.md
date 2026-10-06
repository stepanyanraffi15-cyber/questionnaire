# Questionnaire Evidence & Review Workspace

Take-home assignment — **Alternative C**. A local workspace that drafts cited answers to buyer questionnaire
questions from fictional product documents, checks the evidence, routes unresolved questions to the right
reviewer, and reuses only human-approved answers.

> Status: **implementation not started.** Every TODO below is filled in as the work lands.

## Setup and run
TODO — install, configure keys (`.env.example`), run the workspace, run the checks.

## Replaying saved real responses without an API key
TODO.

## Architecture
TODO — components, data flow, which decisions are made by code and which by the model (see `docs/decisions/`).

## Model configuration
TODO — providers, exact model IDs, parameters, prompts and where they live.

## Data and assumptions
TODO — seed vs additions, generation method, and every ambiguity decision.

## Reference cases and check results
TODO — the answer key in `reference/`, how it was derived, and the results table for the minimum demonstration.

## Time spent
TODO.

## Known limitations
TODO.

## Repository map

| Path | What |
|---|---|
| `CLAUDE.md`, `AGENTS.md` | Instructions for AI coding tools |
| `starter-pack/` | Unchanged supplied material (protected) |
| `data/seed/` | Task C seed files (protected); additions live beside it |
| `reference/` | Hand-written answer key and grader (protected) |
| `docs/decisions/` | Decision records, including ambiguity resolutions |
| `docs/research/` | Research notes and bibliography |
| `runs/` | Saved real model responses for replay |
| `ai-workflow/` | AI configuration manifest and README (templates until completed) |
| `.claude/` | Claude Code settings, protect-paths hook, subagents, starter-pack skill |
