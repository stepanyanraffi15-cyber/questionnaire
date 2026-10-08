# 032 · Code layout: one package of plain functions with one-way imports

- Status: accepted
- Requirements: the assignment brief's "Connect document loading, model-generated drafts, evidence checks, review, and
  reuse of saved approved answers. Local JSON files or SQLite are sufficient. Keep document text separate from
  application instructions."; the repository's clean-code rules (small single-purpose functions, explicit errors, no
  duplicated logic).

## Context

The application must be explainable module by module, keep rules testable without a model or a UI, and let the screen
and the report show exactly the same item state. Code decides only mechanical facts and leaves meaning to recorded
model calls and the reviewer (decision 035), so the modules that decide (authority, checks, review) must stay free of
model calls and I/O.

## Options considered

1. **One package `src/qa/` of small modules; rules as pure functions; I/O only at the edges.**
2. **Classes and a service layer.** More structure than the problem needs.

## Decision

Option 1, as built:

| Module | Job |
|---|---|
| `dataset.py` | Load the seed and change files; validate IDs and references (decision 021); the one questionnaire is the seed's question list (decision 022) |
| `authority.py` | Which documents are replaced, from `supersedes` only (decision 001) |
| `prompts.py` | The draft and support-check requests: a prompt file plus JSON data; the model output schemas |
| `llm.py` | Fingerprint; replay and record clients (decision 029) |
| `checks.py` | Mechanical evidence checks and the strengthening-word hint (decisions 006, 008, 009) |
| `drafting.py` | One item: draft, mechanical checks, support check, status |
| `staleness.py` | Version comparison and sticky stale marks (decisions 010, 011) |
| `review.py` | Process a request with exact-match reuse; edit, note, approve with the guard (decisions 014–016) |
| `views.py` | The item view, counts and revision history shared by the UI and the report (decision 020) |
| `store.py` | Atomic read and write of the JSON state file (decision 030) |
| `export.py` | A request exported as a completed questionnaire (optional enhancement) |
| `scenario.py` | The scripted reference scenario, steps S1–S11 (decision 026) → `runs/report/observed.json` |
| `cli.py` | `qa report`, `qa check-data`, `qa export`, `qa inspect` |
| `ui.py` | The Streamlit review workspace |

Imports flow one way: ui, cli, scenario → review → drafting, views → checks, staleness, prompts → dataset,
authority; `llm` and `store` are leaves. `views.item_view()` feeds both the UI and `observed.json`, so the screen and
the report cannot disagree. Instructions live in `prompts/*.md`; document text is only ever placed inside JSON data.

## Consequences

- The grader and its judge in `reference/` are a separate program and import none of this (decision 027).
- The README carries the same table.

## Evidence

- `CLAUDE.md` ("The layout of application code is decided during implementation; record it in a decision and in the
  README.").
