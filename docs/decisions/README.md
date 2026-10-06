# Decision records

One file per meaningful choice: `NNN-short-title.md` (e.g. `001-authority-signal.md`). Never rewrite history —
supersede a decision with a new file that links the old one. Ambiguity decisions live here too
and are summarised in the README.

## Template

```markdown
# NNN · Title

- Status: proposed | accepted | superseded by NNN
- Requirements: (the assignment requirement(s) this serves, quoted or named)

## Context
What problem, what the brief/domain rules say (quote), what we observed.

## Options considered
1. … — pros / cons / evidence
2. …

## Decision
What we chose and the rule it follows.

## Consequences
What this makes easier/harder; what to test; what would make us revisit it.

## Evidence
Links to research notes, sources (opened), experiments, test names, run records.
```
