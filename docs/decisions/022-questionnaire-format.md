# 022 · One questionnaire: the seed's Q1–Q8 list, mapped in code

- Status: accepted
- Requirements: the assignment brief's "Load the documents and questionnaire, preserve their IDs, and check for
  missing or duplicate references." and "Use the five fictional documents and eight-question questionnaire in
  tasks/evidence/"; its core scope "one small questionnaire, local text documents, one review workspace, and
  exact-match reuse of approved answers"; `starter-pack/README.md:5`, which allows adapting file formats when the
  mapping is recorded. Ambiguity AMB-36.

## Context

`data/seed/seed.json` holds one flat list of questions (`id`, `topic`, `text`) and no notion of separate requests. The
reuse scenario needs a later request that repeats a question (decision 015), and the duplicate check needs a defined
scope. `data/seed/` must not be edited, and no questions are added (decision 033).

## Options considered

1. **The seed's list is the one questionnaire, mapped in code; a request is one run of it; items are keyed
   `request/question`.** No new file. The same question IDs appear in every request without clashing, because the
   item key includes the request.
2. **A question pool plus a questionnaire file naming lists of question IDs** (for example a full list and a separate
   one-question follow-up list with a new question ID). Needed only to hold added questions; with none added it is an
   extra format to explain. Rejected.
3. **A free-text "ask a question" box.** Needs no file but must be scripted for the reference checks; not required.

## Decision

Option 1.

- The loaded question list (Q1–Q8, in file order) is the questionnaire. The mapping is applied in code, so the seed
  stays untouched and no questionnaire file exists.
- A request is one run of that questionnaire against the currently loaded documents and applied change files.
  Requests are numbered R1, R2, …; each has eight items, such as R1/Q1.
- Duplicate question IDs are checked within the loaded question list (decision 021).

## Consequences

- `data/GENERATION.md` records the mapping: the flat list in `seed.json` is the one questionnaire, and a request is one
  run of it.
- The reference scenario runs it five times, R1 to R5 (decision 026).

## Evidence

- `data/seed/seed.json:69-110`.
- `starter-pack/README.md:5` ("Preserve the rules and supplied cases; you may adapt file formats or language when the
  brief allows it, recording the mapping.").
