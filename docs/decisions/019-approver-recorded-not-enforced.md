# 019 · The approver is recorded, not enforced

- Status: proposed
- Requirements: Rule 4 of `data/seed/domain.md` ("Use the supplied topic-to-reviewer mapping."); the assignment
  brief's "Suggest an owner from the topic mapping instead of inventing one." and "When a question is repeated, reuse
  its approved answer and show its approval and sources."; its notes list authentication as optional ("Model
  frameworks, cloud deployment, authentication, fine-tuning, streaming, and multiple collaborating agents are
  optional."). Ambiguity AMB-16.

## Context

The owner mapping contains role names only (`"exports": "Product reviewer"`, …). The brief gives the mapping's purpose
as suggesting an owner. Neither the rules nor the brief says only the owner may approve.

## Options considered

1. **Record a free-text approver and time; show the suggested owner; no permission check.**
2. **Require the approver to equal the mapped owner.** Adds a permission rule that is not in the rules.
3. **Warn when the approver is not the owner.**

## Decision

Option 1. Every approval stores the approver and time. The approve form's approver field defaults to the suggested
owner. The owner is always computed as `owners[topic]` at display time and never taken from model output.

## Consequences

- An approval record is auditable without adding authentication.
- In the reference scenario the approver is "Product reviewer", the owner the mapping gives for exports (decision 025).

## Evidence

- `data/seed/domain.md:8`.
- `data/seed/seed.json:111-116`.
