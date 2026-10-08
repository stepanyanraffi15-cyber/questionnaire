# 012 · A new contradicting document does not mark existing approvals for review

- Status: accepted
- Requirements: Rule 3 of `data/seed/domain.md` ("Mark an approved answer for review if a referenced document version
  changes."); the instruction "Record any unresolved ambiguity in your README. Do not silently add domain rules."
  (`data/seed/domain.md:18`). Ambiguity AMB-32.

## Context

Suppose Q7 is approved from BILLING-v1 version 1, and later a new billing document is loaded that contradicts
"monthly" without superseding BILLING-v1. No such document exists in this project's data; the case is hypothetical,
but the rule must say what happens. BILLING-v1's version has not changed and it is still authoritative, so under Rule 3
the approval stays fresh even though its fact is now contested by another current document.

## Options considered

1. **Literal Rule 3: not stale; documented limitation.**
2. **Re-run conflict detection for approved facts whenever documents are added.** Adds behaviour beyond Rule 3 and
   depends on a model judgement.
3. **Flag every approval when any document is added.** Over-flags; documents have no topic field to narrow it.

## Decision

Option 1. The README lists this as a known limitation. New requests for other questions still detect conflicts
normally.

## Consequences

- No hidden rule is added.
- Revisit if the rules gain a trigger based on new documents.

## Evidence

- `data/seed/domain.md:7` "Mark an approved answer for review if a referenced document version changes."
- `data/seed/domain.md:18`.
- `data/seed/seed.json:55-67` (BILLING-v1).
