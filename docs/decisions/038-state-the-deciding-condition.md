# 038 · The draft prompt asks the answer to include the passage's limit (who or which plans)

- Status: accepted
- Requirements: the assignment's "Use a model to draft concise answers with supporting passage references"; the
  supplied expected result for Q1, "No, paid plans only."; reference case RC-3 (MIN-3).

## Context

In the first recorded run (commit e6b9fee), Gemini answered Q1 "Can free-plan users export CSV?" with "No, free-plan
users cannot export CSV." (`runs/recordings/draft-7d5bf79e9ed0f4b7.json`). Every mechanical check passed: it cited
EXPORT-v2:p1, the excerpt was verbatim and EXPORT-v1:p1 was shown as replaced. The recorded judge found that the
answer does not state the key's second expected fact, "CSV export is for paid plans only", which the supplied expected
result also gives, so the grader reported RC-3 as FAIL. The answer was correct but incomplete: a buyer learns that free
plans cannot export, but not which plans can.

## Options considered

1. **The author signs the answer off as acceptable.** Keeps the prompt, but accepts answers that drop the limit the
   passage gives.
2. **Change the answer key.** Not allowed: the key is never changed to make a check pass.
3. **Add a prompt rule asking for the passage's limit,** re-record, and regrade. The author approved this, with a
   fallback: if a second attempt still failed, stop retrying and take option 1.

## Decision

Option 3. Two attempts, both recorded:

- **Attempt 1** (rule 9: "When the passage answers with a condition … state that condition, not only "yes" or "no"").
  Gemini answered "No. Free-plan users cannot export CSV." (`draft-5c02bbad60090ccb.json`). Its own basis: the
  passage "directly states that free-plan users cannot export CSV", so it did not treat "paid plans only" as a
  condition on that answer. RC-3 still failed.
- **Attempt 2** (the rule now in `prompts/draft_answer.md`): "If a passage limits who or which plans something applies
  to, include that limit in the answer, even when another sentence already answers yes or no", with a worked example
  and "Use the passage's own limit; never add one it does not state" (which keeps decision 006). Gemini answered "No.
  CSV exports are available on paid plans only." (`draft-6ca64521e728946e.json`); the judge found every expected fact
  stated and no forbidden claim. RC-3 has no FAIL; like every meaning row, it awaits the author's sign-off.

## Consequences

- Each prompt change gives every draft request a new fingerprint, so each attempt was one live run. The responses of
  all three runs stay in `runs/recordings/` as evidence; replay uses the latest ones.
- The other answers kept their meaning; their counts at every step still match the answer key.
- The worked example in the prompt uses the Q1 passage itself. That makes the fix for Q1 more likely, and it means
  this result is weaker evidence for questions the prompt has not seen; stated as a limitation.
- This is the "one correction" example in `docs/LLM_USAGE.md`.

## Evidence

- `docs/RESULTS.md` at commit e6b9fee (RC-3 meaning FAIL) and now (no FAIL).
- `uv run qa inspect S1 R1/Q1` shows the current request and response.
