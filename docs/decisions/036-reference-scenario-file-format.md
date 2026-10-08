# 036 · The reference scenario file holds timed reviewer actions, not expected results

- Status: accepted
- Requirements: the assignment brief's "Let a reviewer edit and approve a supported answer, or leave it unresolved with
  a note. Show the correction and its reuse on a subsequent request; preserve this state after a reload."; its "Commit
  the final fictional inputs, generation method, and random seed if used."; its "Check five cases against the passages
  and authority metadata, recording expected answers or review states separately from application results."; the
  starter-pack skill's "Keep expected results in a separate file, with each result linked to its input and the rule
  that determines it."

## Context

The reference scenario has eleven steps (decision 026): five runs of the questionnaire, the reviewer's edits, note,
approval and re-approval with fixed texts (decision 025), two reloads, and one change file applied at S7 (decision
024). The scenario runner must execute these steps without guessing, a person must be able to read them top to bottom,
and every run must be reproducible. Step S2 holds three reviewer actions (two edits and a note), and later steps act on
items of earlier requests, such as R1/Q1.

## Options considered

Where the expected results go:
1. Beside each step in the scenario file. Inputs and expectations would be read together, but the answer key would
   then live inside an input file. Rejected.
2. **Only in the answer key under `reference/`; the scenario file holds inputs.**

How a step is written:
1. One action per step. S2 would have to be split into sub-steps, which changes the step numbering used everywhere
   else. Rejected.
2. **A step has an ID, a fixed time and a list of actions; each action has a type and only the fields that type
   needs.**

How the reviewer texts are written:
1. Once, in a table of named texts (W, E3, N) that the steps refer to by name. One place to change a text, but a field
   that holds a name instead of the text is easy to misread, and every step has to be read beside the table.
2. **In full, in each action that uses them.** Each step reads on its own; W appears three times (saved at S2,
   approved at S4, re-approved at S10).

How requests are named:
1. Numbered by the application as it runs them. Steps that act on an item, such as R1/Q1, would depend on that
   numbering without stating it.
2. **Named in the file, R1 to R5 in run order,** so every item reference points at a request the file itself starts.

## Decision

Option 2 in each case. `data/scenario/min-demo.json` is labelled SCRIPTED REVIEWER INPUT and has:

- `_purpose`, `label`, `dataset` (`data/seed/seed.json`, the only data loaded at the start) and `steps`.
- For each step: `id` (S1, S2, … in order), `at` (UTC; `2026-10-08T09:00:00Z` for S1, then one minute per step, shared
  by every action in the step) and `actions`.
- These action types, each with exactly these fields:

| Type | Fields | Meaning |
|---|---|---|
| `run_questionnaire` | `request` | Run the whole questionnaire (Q1–Q8, eight items) as a new request (decision 022) |
| `save_edit` | `item`, `text` | Save an edit; it stays a draft until approved |
| `add_note` | `item`, `text` | Leave a note on the item |
| `approve` | `item`, `text`, `sources`, `approver`, `note` | Approve the text with the chosen source passages; on an item that already has an approval it is a re-approval (decision 011) |
| `reload` | — | Read the saved state from disk again |
| `apply_change` | `file` | Apply a change file from `data/changes/` (decision 024) |

- Items are named `request/question`, such as R1/Q1.
- No expected status, answer or count appears in the file.

### As built (2026-10-08)

`tests/test_data_inputs.py` and the drill file were removed in the lean build (decision 037). The scenario file is now checked end to end: `tests/test_scenario.py` runs every step and the independent grader checks the results against the answer key.

## Consequences

- `tests/test_data_inputs.py` checks the file with the standard library: each action has exactly its fields, steps and
  requests are numbered in order, times are one minute apart from the fixed start, every item names an earlier request
  and a supplied question, approval sources are supplied passages, at least one edit is never approved, and the only
  data the scenario loads is the supplied seed and the source change, never the drill.
- Changing W means editing three actions. The answer key's reuse checks then fail until the key is updated by hand,
  which is intended.
- The file does not say who saved an edit or a note: no supplied example or earlier decision names that person. If
  edits and notes are to record an author, `save_edit` and `add_note` gain a field for it.

## Evidence

- `data/seed/expected-seed-results.json:21`, `:25` (the `approval-reuse` and `source-change` steps).
- `.claude/skills/generate-assignment-data/SKILL.md:14`.
- Decisions 011, 022, 024, 025, 026.
