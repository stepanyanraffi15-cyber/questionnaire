# 005 · A documented negative is an answered "No"; silence is unknown

- Status: accepted
- Requirements: Rule 1 of `data/seed/domain.md` ("An undocumented feature is unknown, not automatically supported or
  unsupported."); the assignment brief's minimum demonstrations "A supported question receives a draft answer whose
  cited passages exist and support its claims." and "The unsupported question stays unresolved and offers an
  appropriate review route without inventing a product capability." Ambiguity AMB-4.

## Context

The seed holds two explicit negatives: "Free-plan users cannot export CSV." (EXPORT-v2:p1) and "Live chat is not
offered." (SUPPORT-v1:p1). It also holds a question with no evidence at all: "Is JSON export available?" (Q2). Rule 1
makes only undocumented features unknown. The opposite mistake matters as much: answering Q2 "No" from the fact that
only CSV is mentioned is a closed-world inference and breaks Rule 1 just as "Yes" would.

## Options considered

1. **An explicit negation in an authoritative passage is an answered "No" with a citation; unknown applies only when
   no authoritative passage covers the point.** Matches the seed's Q1 expectation "No, paid plans only."
2. **Every negative goes to review.** Contradicts the supplied Q1 expected answer.

## Decision

Option 1. Q4 ("Is live chat offered?") is answered "No" from SUPPORT-v1:p1. A negative implied by explicit exclusivity
("paid plans only") follows from the text. A negative inferred from silence is unknown: Q2 is unresolved with reason
`undocumented`. The draft prompt says "Never infer yes or no from silence" and "An explicit 'not offered' is a
documented 'No'". Reading whether a passage states a negative is meaning, so the model does it and the support check
and the reviewer can catch a mistake; code checks only the citation and the excerpt (decision 035). The answer key
states Q2's forbidden claims in plain words: that JSON export is available, that it is not available or not
supported, or that the CSV paid-plan rule covers it (decision 027).

## Consequences

- Q4 counts as answered; Q2 as unresolved. The first run on the seed gives answered 7, unresolved 1, approved 0.
- A planted draft "No, JSON export is not supported." with no citation is caught mechanically (`no_citation`).
- A planted draft "No, only CSV export is offered." citing EXPORT-v2:p1 passes every mechanical check; only the
  support check, which judges meaning, catches it. This is why the support check is required (decision 016).

## Evidence

- `data/seed/domain.md:5`, `:12` ("JSON export is undocumented and needs review.").
- `data/seed/seed.json:25`, `:38`, `:78`, `:88`.
- `data/seed/expected-seed-results.json:4` Q1 `"answer": "No, paid plans only."`; `:10`, `:12` Q2
  `"status": "unresolved"`, `"reason": "JSON export is undocumented"`.
