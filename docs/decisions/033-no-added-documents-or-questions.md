# 033 · The main dataset is the supplied seed; no documents, passages, topics or questions are added

- Status: accepted; its "add nothing" part is superseded by 039
- Requirements: the assignment brief's "Use the five fictional documents and eight-question questionnaire in
  tasks/evidence/" and "Add questions or short passages only if needed for the checks."; its "Keep the provided seed
  cases and their expected results. Extend them with AI, a script, or handwritten examples while following the
  supplied rules. If a rule is unclear, state the ambiguity instead of inventing an industry policy."; its notes to the
  hiring team, "Prior industry knowledge, extra data, or polished mock documents should not improve the score.";
  `data/seed/domain.md:16` "Keep the seeded policies and their authority metadata. Add questions and short passages
  consistent with those rules. Include supported, unsupported, conflicting-source, approved-reuse, and changed-source
  scenarios." Ambiguity AMB-25.

## Context

The two instructions about extending the data read differently. `domain.md` says "Add questions and short passages
consistent with those rules"; the brief says "Add questions or short passages only if needed for the checks". The
brief also says the five reference cases "may combine supplied cases and your additions", so additions are allowed but
not required.

The seed already covers three of the five scenario kinds that `domain.md` lists: supported (Q3, and Q4–Q8),
unsupported (Q2, JSON export), and conflicting source (Q1, where EXPORT-v2 explicitly supersedes EXPORT-v1). The other
two, approved reuse and changed source, are reviewer actions and a version change, not new documents; the supplied
expected results describe them as steps (`approval-reuse`, `source-change`). One branch of the brief has no input in
the seed: a conflict that metadata does not resolve ("otherwise leave the question for review").

An earlier draft of this design added documents and questions to the main data (option 1 below). The author then set
one constraint for all data work: stay inside the supplied data's logic, and do not invent documents, features,
topics or facts that the seed does not contain.

## Options considered

1. **Add documents and questions to the main data,** as the earlier draft did: a refund-policy pair with different day
   counts plus a refund question, and a second, separately numbered copy of Q1 to ask it again (another candidate was
   a second billing document stating another currency). Shows the unresolved-conflict branch in the demonstration, but
   invents product facts and questions the supplied data never contains, and "extra data" should not improve the
   score. Rejected.
2. **Add only the scenario inputs that the supplied reference steps ask for, and test rule cases the seed cannot show
   with labelled fixtures built from variants of the supplied documents.**
3. **Add nothing at all, not even scenario inputs.** The approved-reuse and changed-source scenarios required by
   `domain.md` and the supplied expected results could not run. Rejected.

## Decision

Option 2.

- The main dataset is `data/seed/` unchanged: five documents, Q1–Q8 and the topic-to-owner map. No document, passage,
  topic, question or product fact is added.
- Inputs added outside `data/seed/`, none of which adds a fact: `data/scenario/min-demo.json`, the scripted reviewer
  inputs (decision 025); `data/changes/export-v2-version-3.json`, the source change (decision 024);
  `data/changes/drill-exports-owner.json`, a drill that maps exports to an existing owner and is never used by the
  scenario (decision 024).
- Test fixtures live under `tests/fixtures/`, each with a `_purpose` field and a label, and are never loaded with the
  main data: the unresolved-conflict fixtures FX-1 and FX-1b (decision 023), authority corpora, deliberate invalid
  data, planted drafts, simulated failures and an injection fixture. Each is a variant of the supplied documents or
  questions with no new product facts.
- How the five scenario kinds are covered: supported Q3–Q8; unsupported Q2; conflicting source Q1, resolved by
  supersedes; approved reuse R3/Q1 and R5/Q1; changed source, the EXPORT-v2 version change at step S7. The unresolved
  conflict is covered only by FX-1.
- Reading of the two instructions, recorded as an ambiguity: `domain.md`'s "Add questions and short passages" is read
  together with the brief's "only if needed for the checks". The checks needed no new passage or question except the
  unresolved-conflict branch, and a fixture covers that branch without new facts.

## Consequences

- The README and `data/GENERATION.md` say plainly that no passages or questions were added, and why.
- Limitation of the supplied data, stated in the README: the "otherwise leave the question for review" branch is shown
  by a test fixture, not in the demonstration.
- The supplied expected results and seed totals apply unchanged; no total has to be recalculated.
- A reviewer runs the same checks on the same data that was supplied.

## Evidence

- `data/seed/domain.md:16`, `:18`.
- `data/seed/seed.json` (five documents, eight questions, four owners).
- `data/seed/expected-seed-results.json:21`, `:25` (the `approval-reuse` and `source-change` steps).

## Update (decision 037)

The lean build did not create `tests/fixtures/` or `data/changes/drill-exports-owner.json`. The same rules are tested
with small inline variants of the seed in `tests/`, and the unresolved conflict (FX-1) is one of those inline tests.
The rest of this decision stands: nothing was added to the main data.

## Update (decision 039)

At the author's request, a second dataset was added beside the seed: `data/additions/extended.json`, with its own
questionnaire (X1–X35) and its own scenario. The seed, the seed scenario and their expected results are unchanged, so
everything above about the seed still holds. The unresolved conflict that the seed cannot show is now in the extended
data (X5, X11, X18, X24) as well as in the test.
