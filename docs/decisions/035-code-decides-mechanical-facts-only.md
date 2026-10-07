# 035 · Code decides mechanical facts; meaning is decided by recorded model reasoning and people

- Status: accepted
- Requirements: the assignment brief's description of the model's role, "Synthesize answers across documents,
  recognize missing or conflicting evidence, and reuse corrections that a person has reviewed."; its requirement
  "Check that references and excerpts exist and that the cited content supports the answer."; its instruction "Verify
  expected results by calculation or source inspection before evaluating the application."; `data/seed/domain.md:18`
  "Do not silently add domain rules."

## Context

The brief asks for two kinds of check in one sentence: that "references and excerpts exist", which is a fact about IDs
and strings, and that "the cited content supports the answer", which is a fact about meaning. An earlier draft of this
design used code for both (option 1 below). Two places judged meaning with fixed lists of words or string patterns:

- the app: a list of strengthening words decided `unsupported_claim` and blocked approvals (decisions 006 and 016);
- the answer key: required-fact and forbidden-claim patterns graded answers (decision 027).

Tried on sample sentences, these rules misjudged in both directions. Wrong answers passed: "Team members can invite
account owners." (Q6: it contains "account owners" and no "only"); "Free-plan users can export CSV; this is not
limited to paid plans." (Q1: it contains "not" and "paid"). Correct answers failed: "Email support is available Monday
to Friday, 9am to 5pm UTC." (Q3: "9am" did not match the time pattern); "No passage mentions JSON export, so it needs
review." (Q2: it starts with "No"); "Email support is available every weekday, 09:00 to 17:00 UTC." (flagged for
"every"). A list of words or patterns cannot tell what a sentence claims.

## Options considered

1. **Code decides meaning with word lists and regular expressions, as the earlier draft did.** Deterministic and
   cheap, but it misjudges in both directions, as above. Rejected.
2. **The model decides everything, including authority and reuse.** Following the rules (only supersedes replaces;
   only approved answers are reused; a version change forces review) would depend on the model obeying instructions.
   Rejected.
3. **Split by kind of fact: code decides mechanical facts; meaning is decided by recorded model reasoning and by
   people; word lists and patterns only raise hints.**

## Decision

Option 3. The author set this principle after reviewing the earlier draft: code checks are useful, but they must not
replace a reasoning step about the documents.

- **Code decides only mechanical facts:** an ID exists; a quote or excerpt is verbatim in its passage (whitespace
  collapse only); a passage is current according to `supersedes`; a version changed; an owner is in the topic mapping;
  a question text matches exactly for reuse; status and reason values; counts.
- **Meaning is decided by recorded model reasoning and by people:** whether a passage supports a claim, whether a claim
  is stronger than its source, whether two passages conflict, whether a contradiction is about this question, and
  whether an answer states the expected facts. In the app this is the draft and the support check, each response
  saved and replayable, plus the reviewer, who can approve over a "not supported" verdict only with a recorded note. In
  grading it is a recorded judge plus the author's sign-off.
- **Word lists and patterns may only raise hints,** shown to the model or to a person. They never set a status, block
  an approval or grade a row.

## Consequences

- Decision 006: the strengthening-word list becomes a hint; the support check decides `unsupported_claim`.
- Decision 009: the model decides that a contradiction exists; code verifies only the quotes and the passage.
- Decision 016: approval hard blocks are mechanical; a strengthening word is a warning.
- Decision 027: the answer key states facts in plain words; meaning is graded by a recorded judge with the author's
  sign-off; pattern hits are hint columns only; a verdict that is not recorded or not signed off is PENDING, never
  PASS.
- Limitation: model judgements can be wrong, and the judge is the same model family as the app. Saved responses make
  every judgement inspectable, and a person's note or sign-off is the final check.

## Evidence

- `data/seed/seed.json:25`, `:38`, `:51` (the passages behind the examples).
- `data/seed/expected-seed-results.json:4`, `:16` (the supplied answers are paraphrases: "No, paid plans only.";
  "Monday to Friday, 09:00–17:00 UTC").
