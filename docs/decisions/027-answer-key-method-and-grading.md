# 027 · How the answer key is made and how it is graded

- Status: accepted
- Requirements: the assignment brief's "Check five cases against the passages and authority metadata, recording
  expected answers or review states separately from application results."; "Verify expected results by calculation or
  source inspection before evaluating the application." and "Do not use the application's answers as the answer key.
  Label simulations and report failed checks."; "Include a results table or test report for these checks. Explain any
  failures you could not fix."; `reference/README.md` ("Expected results are derived **by reading the passages**, never
  from application output. `grade.py` must not import anything from `src/qa/`."). Ambiguities AMB-23 (comparing
  answers and excerpts) and AMB-31 (public wording of the method).

## Context

The supplied expected answers are paraphrases, not excerpts: the Q3 answer "Monday to Friday, 09:00–17:00 UTC" uses an
en dash, while the passage says "09:00 to 17:00 UTC", so an exact-string comparison would be wrong. Whether an observed
answer states the expected facts is a question of meaning (decision 035).

An earlier draft of the key graded meaning with string patterns (option 2 below). Tried on sample sentences, the
patterns misjudged in both directions. Wrong answers passed: "Team members can invite account owners." (Q6),
"Free-plan users can export CSV; this is not limited to paid plans." (Q1), "Account owners cannot download billing
invoices." (Q8). Correct answers failed: "Email support is available Monday to Friday, 9am to 5pm UTC." (Q3), "No
passage mentions JSON export, so it needs review." (Q2), "With email and password. The documents do not mention SSO."
(Q5).

The key must also be independent of the application, and a reader must be able to check that it was not fitted to
output. The current public wording "hand-written answer key" does not describe the real method, which used AI
assistance.

## Options considered

Grading meaning:
1. **Exact answer strings.** Fails correct paraphrases, including the seed's own answers. Rejected.
2. **Required-fact and forbidden-claim regular expressions (regexes), as in the earlier draft.** Misjudges in both
   directions, as above. Rejected as a grade; regex hits survive only as hint columns.
3. **A recorded model judge compares each observed answer with expected facts and forbidden claims written in plain
   words, and the author signs off every verdict.** Meaning is judged by reasoning that is saved and replayable, and a
   person has the last word.
4. **The author's sign-off alone.** Feasible for a set this small, but leaves no recorded reasoning behind each
   verdict.

Independence:
1. **Expected facts and forbidden claims written and committed before any application code or recording; a judge
   prompt of its own under `reference/`, separate from the app's prompts; grading code that never imports application
   code; the author's sign-off.**
2. **Reuse the app's support check as the judge.** The system would grade itself. Rejected.
3. **Write the key after some application code exists.** Weaker evidence. Rejected.

## Decision

Option 3 for grading meaning and option 1 for independence.

- **What each row states:** covers, rules, the decision records it rests on, `derived_from` (passage ID, verbatim
  quote, authority metadata), mechanical checks, and meaning checks written as expected facts and forbidden claims in
  plain words. Example, Q3: email support is available Monday to Friday (all five weekdays), from 09:00 to 17:00 ("9 am
  to 5 pm" is fine), in UTC; forbidden: weekend hours, another time zone, any claim that live chat is available. The
  key also states every item's expected status at every scenario step (S1–S11) and the counts.
- **Mechanical checks, graded by code:** IDs exist and citations fall inside the allowed set (`ids_subset_of` with
  `non_empty`, `ids_include`); excerpts are verbatim after whitespace collapse (`excerpts_verbatim`); status, reason and
  owner values (`equals`, `not_equals`); stale reasons compared as fields (document, version at approval, current
  version); reused text exactly equal to W (decision 025); state unchanged by a reload (`same_as`); count arithmetic.
- **Meaning checks, graded by a recorded judge and the author:** the judge is a Gemini model with its own prompt under
  `reference/`. It receives the question, the passage, the expected facts, the forbidden claims and the observed
  answer, and returns one verdict per fact and per forbidden claim, each with a quote from the observed answer; code
  checks only that each quote is verbatim. Judge verdicts are saved and replayed. They are recorded only in a live
  recording run that the author starts or allows; tests use SIMULATED verdicts. The author, Raffi, signs off each
  verdict, and the sign-off is stored where `grade.py` reads it. A meaning check with no recorded verdict, or with a
  verdict but no sign-off, shows as PENDING and is never counted as PASS. The patterns of option 2 and the
  strengthening-word list run only as hints, printed in hint columns; they never grade a row.
- **Calibration:** before its verdicts count, the judge runs on a calibration set with human labels: the seed's own
  answers ("No, paid plans only."; "Monday to Friday, 09:00–17:00 UTC") and the right and wrong sentences listed above.
  It must agree with every label, and the agreement is recorded.
- **Programs:** `reference/grade.py` uses only the standard library. It re-reads the data files, re-verifies excerpts
  itself, grades the mechanical checks, reads the saved judge verdicts and sign-offs, writes `docs/RESULTS.md`, and
  exits 0 (all pass), 1 (any failure) or 2 (crash); PENDING is not a pass. Failing rows are never dropped.
  `reference/test_grade.py` checks: no `qa` or `src` import, no `importlib` and no `sys.path` edits, read from the
  syntax tree; the key's arithmetic (counts sum to each request's items and match the per-item statuses); every ID and
  quote exists in the data files; planted wrong mechanical observations FAIL; SIMULATED judge verdicts drive the
  meaning rows to PASS, FAIL or PENDING as expected.
- **Public wording of the method:** "derived from the passages and metadata, drafted with AI assistance, independently
  reviewed, approved by the author; meaning graded by a recorded judge with the author's sign-off; never taken from application
  output".
- A later key change needs a human-run session, a decision note and its own commit, and is never made to pass a check.

## Consequences

- Independence rests on three things: expected facts written and committed before the application, a judge prompt
  separate from the app's prompts in grading code that never imports application code, and the author's sign-off.
- Limitation, stated in the README: the judge is the same model family (Gemini) as the app, so self-preference is
  possible; the calibration set and the sign-off are the checks against it.
- Until judge verdicts are recorded and signed off, the meaning rows show PENDING; the mechanical rows are graded
  already.
- A handful of reference cases is limited evidence of behaviour on other data.

## Evidence

- `data/seed/expected-seed-results.json:4`, `:16` (the supplied answers: "No, paid plans only."; "Monday to Friday,
  09:00–17:00 UTC").
- `data/seed/seed.json:38` "Email support is available Monday to Friday, 09:00 to 17:00 UTC. Live chat is not offered."
- `reference/README.md`.
- `.claude/skills/generate-assignment-data/SKILL.md:14` ("Keep expected results in a separate file, with each result
  linked to its input and the rule that determines it.") and `:16` ("Do not accept the application's output as the
  answer key.").
