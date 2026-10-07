# 031 · Keep both .env.example files, identical

- Status: proposed
- Requirements: the assignment brief's "Include only the relevant parts of user-level configuration. Replace secrets
  with placeholders and list environment variable names in .env.example" and its submission item asking for the AI
  configuration with "relevant versions, and sanitized environment examples"; the repository rule "Never read, print or
  commit `.env`. Variable names go in `.env.example`." Ambiguity AMB-30.

## Context

The repository has a root `.env.example` and `ai-workflow/.env.example` from the starter material. The latter says
"Remove this example if no variables were used." Variables are used: the app reads an API key in record mode, a mode
switch and a state directory. The Google SDK also reads `GEMINI_API_KEY` on its own, in addition to `GOOGLE_API_KEY`.
A developer-only variable, `QA_ALLOW_REFERENCE_EDIT`, is read by the path-protection hook, not by the app.

## Options considered

1. **Delete `ai-workflow/.env.example`.** Goes against the file's own instruction, since variables are used.
2. **Keep both files, identical, enforced by a test.**

## Decision

Option 2. Both files contain: an app section (`GOOGLE_API_KEY=`, `QA_MODE=replay`, `QA_STATE_DIR=state`, plus
`ANTHROPIC_API_KEY` only if that adapter is built); a commented note naming the variables the SDK reads by itself and
which one wins when both are set; and a commented developer-only section for `QA_ALLOW_REFERENCE_EDIT`, set in the
shell, never in `.env`, never read by the app. The template's `MODEL_API_KEY` is replaced.

## Consequences

- A hygiene test checks the two files are identical and list exactly the variables the app reads.
- Offline tests remove every key and routing variable the code or SDK reads.

## Evidence

- `ai-workflow/.env.example:2` ("Remove this example if no variables were used.").
- `.env.example`.
