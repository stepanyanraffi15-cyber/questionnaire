# reference/ — hand-written answer key

Protected by `.claude/hooks/protect_paths.py`: the coding agent may edit this folder only when the human starts the
session with `QA_ALLOW_REFERENCE_EDIT=1`.

Rules (from the brief and the starter-pack skill)
- Expected results are derived **by reading the passages**, never from application output.
- `grade.py` must not import anything from `src/qa/`.
- Each expectation records: status, allowed source passages, required facts, forbidden claims, and the passage
  quote it was derived from.
- Seed expectations for Q1–Q3 must agree with `data/seed/expected-seed-results.json`.

Planned files: `expected.json`, `grade.py`, tests for the grader.
