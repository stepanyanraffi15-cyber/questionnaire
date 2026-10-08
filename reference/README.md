# reference/ — the answer key and the grader

Protected by `.claude/hooks/protect_paths.py`: the coding agent may edit this folder only when the human starts the
session with `QA_ALLOW_REFERENCE_EDIT=1`. A key change needs its own commit and a decision note, and is never made to
make a check pass.

## How the key was made

Every expected value in `expected.json` was derived by reading the passages and authority metadata in
`data/seed/seed.json` and the rules in `data/seed/domain.md`. The rows were drafted with AI assistance, checked
against the passages by a separate AI review agent, and approved row by row by the author. None was taken from
application output: the rows were drafted and approved during planning, before implementation, and the key
is committed before the application code. The seed's own expected results for Q1–Q3
(`data/seed/expected-seed-results.json`) agree with RC-1 to RC-3.

Each row records what it covers, the rules and decision records it rests on, the passage quotes and authority
metadata it was derived from (`derived_from`), the gold passages (`gold_passages`: the current passages that answer
the question), the mechanical checks, and the meaning checks.

**The extended questionnaire** (X1–X26 over the seed plus `data/additions/extended.json`) has its own key in the
`extended` block, with its own texts, rows and step counts. It was written from the passages and metadata before the
application ran on that data, and a separate AI agent re-derived every row blind, without the application's code or
output; it agreed on every status, reason, owner, gold passage and count (decision 042). Adding `gold_passages` to
the seed rows changed no seed expectation.

## How it is graded

`uv run python reference/grade.py` reads `runs/report/observed.json` and `runs/report/observed-extended.json` and
writes `docs/RESULTS.md`. It uses only the Python standard library and imports nothing from `src/`; it re-reads the
passages from `data/` itself.

- **Mechanical checks** (code): IDs and citations within the allowed set, excerpts verbatim (whitespace collapse
  only), status, reason and owner values, approval sources with versions, stale reasons as fields, exact reused
  text, state unchanged by a reload, and the counts at every step.
- **Meaning checks** (expected facts and forbidden claims, in plain words): a Gemini judge with its own prompt
  (`judge_prompt.md`) gives a verdict per fact and claim, quoting the answer; code checks only that the quotes are
  really in the answer. `uv run python reference/judge.py` records the verdicts into `runs/judge/verdicts.json`
  (live calls, needs a key); the grader replays them. The author then signs off each one in `signoff.json`.
  Only the author's sign-off makes a meaning check PASS: unsigned, a judge PASS (or a missing verdict) is
  **PENDING** and a judge FAIL is **FAIL**. The judge is the same model family as
  the application, which is a stated limitation.
- **Retrieval recall@k** (a measurement, not a check): for each row with `gold_passages`, the share found in the
  first retrieval for the question, and the share shown to the model by the end of its own searches. n/a when the
  row has no gold passage or the item was not drafted.

Exit code: 0 everything passes, 1 any FAIL, 3 no FAIL but something PENDING, 2 the grader crashed.
`test_grade.py` checks the grader's independence, the key's arithmetic, that every quote and authority entry matches
the data, that gold passages are current, the recall arithmetic, and that planted wrong observations fail.

## observed.json contract

`{"mode", "model", "contract_version", "scenario", "steps": {"S1"…"S11": {"counts": {request: {answered, unresolved,
approved, needs_review, error}}, "items": {"R1/Q1": item view}, "action_problems": []}}}`. An item view holds the
question, owner, status, reason, presented answer and its source, citations with versions and excerpts, replaced and
conflicting passages shown, the approval (with sources, versions and stale reasons), whether it was reused, the
edit and note, a summary of the model suggestion (with its retrieval hits and search steps), and the model calls
with their labels. `observed-extended.json` has the same shape, with steps S1–S5 and items such as R1/X5.
