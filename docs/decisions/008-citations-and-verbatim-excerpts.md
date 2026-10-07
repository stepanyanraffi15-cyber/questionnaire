# 008 · Citations are a passage ID plus a verbatim sentence

- Status: accepted
- Requirements: the assignment brief's "Use a model to draft concise answers with supporting passage references and
  short evidence excerpts." and "Check that references and excerpts exist and that the cited content supports the
  answer." Ambiguity AMB-9 (several facts in one passage); the excerpt part of AMB-23.

## Context

Three seed passages each answer two different questions: SUPPORT-v1:p1 (Q3 hours, Q4 live chat), ACCESS-v1:p1 (Q5
sign-in, Q6 invites) and BILLING-v1:p1 (Q7 frequency, Q8 invoices). A passage ID alone cannot show which fact is used.
The seed's expected Q3 answer, "Monday to Friday, 09:00–17:00 UTC", uses an en dash (U+2013) while the passage says
"09:00 to 17:00", so an excerpt copied from an answer's style would not be found in the passage.

The brief's sentence holds two different checks. "References and excerpts exist" is mechanical: code can decide it
exactly. "The cited content supports the answer" is about meaning and belongs to the support check and the reviewer
(decision 035). This record covers the first.

## Options considered

Citation form:
1. **Passage ID plus the verbatim sentence used, as the excerpt.**
2. **Passage ID only.**

Excerpt check:
1. **Exact substring of the cited passage's text after collapsing whitespace only.**
2. **Substring after Unicode and dash normalisation.** Would accept the en-dash excerpt, which is not what the passage
   says.
3. **Fuzzy matching.** Would accept made-up excerpts.

## Decision

Passage ID plus a verbatim excerpt, checked as a substring of the passage it cites (not of any passage, so attribution
to the wrong passage is caught) after whitespace collapse only. No dash, case or quote folding. Answers may paraphrase;
excerpts may not. Versions remain per document, so staleness is checked per document version (decision 010).

## Consequences

- An en-dash excerpt for Q3 fails as `invalid_excerpt` (planted draft P5); this is correct behaviour, not something to
  normalise away.
- The answer key grades the meaning of answers with plain-word facts, a recorded judge and a human sign-off, not with
  exact strings; it checks excerpts mechanically with its own code, the same way (decision 027).
- A change to SUPPORT-v1 made only for the live-chat fact would also mark an approved Q3 answer for review. This
  over-flags, which is safe and matches the document-level wording of Rule 3.

## Evidence

- `data/seed/seed.json:38`, `:51`, `:64`.
- `data/seed/expected-seed-results.json:16` Q3 `"answer": "Monday to Friday, 09:00–17:00 UTC"`.
