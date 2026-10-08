# 004 · Code applies authority; replaced text and metadata stay out of model prompts

- Status: accepted
- Requirements: Rule 2 of `data/seed/domain.md` ("Keep replaced text available to reviewers."); the assignment brief's
  "Keep document text separate from application instructions." and "Use a model to draft concise answers with
  supporting passage references and short evidence excerpts."; its minimum demonstration "The outdated policy’s
  conflict is visible, and the answer uses the document that explicitly supersedes it." Ambiguity AMB-35.

## Context

If supersession is only described to the model, the Q1 outcome depends on the model following the instruction. Code
can compute authority exactly from the supersedes field (decision 001); that is a mechanical fact, so it stays in code
(decision 035). The question is what the model then sees. Sending replaced passages, dates or versions invites the
model to weigh them; leaving them out means the model cannot itself notice the old policy, but code can show it.

## Options considered

1. **Send only authoritative passages (ID and text) as JSON data; code shows replaced text to the reviewer.**
2. **Send all passages with labels such as "replaced", and also enforce authority in code.** The model sees more, but
   the labels and dates can still pull it toward the wrong passage, and code must reject such citations anyway.
3. **Send all passages and let the model decide authority.** Makes the required outcome depend on model behaviour.

## Decision

Option 1. The draft request contains the question and the authoritative passages only, sorted by ID, built with
`json.dumps` inside the user message; the instructions live in `prompts/*.md` as the system message. No dates,
versions, statuses or owners are sent. Code shows every replaced passage of a cited document's lineage as "Superseded
text", for example EXPORT-v1:p1 "replaced by EXPORT-v2 via its supersedes field". The model still decides everything
about meaning: wording, which current passages to cite, "not documented", conflicts among current passages, and the
support verdict.

## Consequences

- A support citation to a replaced passage cannot come from the prompt; if one appears it is rejected as
  `superseded_source`.
- In test fixture FX-1 (decision 023) no edge links the two EXPORT documents, so both passages are authoritative and
  both reach the model; that is how the model can notice that conflict.
- Limitation: no question in this data needs facts from two current documents, so cross-document synthesis is not
  demonstrated. This is stated in the README.
- Tests: replaced passages and metadata are absent from built prompts; in the injection fixture (a copy of
  SUPPORT-v1:p1 with an instruction-like sentence appended, labelled as a test fixture) the sentence appears only inside
  the JSON string.

## Evidence

- `data/seed/domain.md:6`.
- `data/seed/seed.json:12` "CSV exports are available on every plan." (the replaced passage shown by code).
