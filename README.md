# Questionnaire Evidence & Review Workspace

Take-home assignment, Alternative C. A local workspace that drafts cited answers to buyer questionnaire questions from
fictional product documents, checks the evidence, routes unresolved questions to the right reviewer, and reuses only
answers a person has approved.

## Setup and run

Requires [uv](https://docs.astral.sh/uv/); Python 3.12 is pinned (`.python-version`) and installed by uv.

```bash
uv sync --locked
uv run streamlit run src/qa/ui.py      # the review workspace (replay mode, no API key needed)
uv run qa report                       # replay the scripted scenario S1–S11 -> runs/report/observed.json
uv run python reference/grade.py       # grade it against the answer key -> docs/RESULTS.md
uv run pytest                          # tests (offline; the network is blocked in tests)
uv run qa check-data                   # load the data and list any reference problems
uv run qa export R1                    # print a workspace request (made in the UI) as a completed questionnaire
uv run qa inspect S1 R1/Q1             # one item with the saved request and raw model response behind it
```

**Making new model calls.** Copy `.env.example` to `.env` and set `GOOGLE_API_KEY`, then run with `QA_MODE=record`
(for example `QA_MODE=record uv run qa report`). Record mode replays any request that already has a saved response
and calls Gemini only for new ones, saving each response under `runs/recordings/`. `uv run python reference/judge.py`
records the grader's judge verdicts the same way.

## Replaying saved real responses without an API key

Replay is the default (`QA_MODE=replay`). Every real response was saved with its request, prompt file, model settings
and token usage, keyed by a fingerprint of the exact request. Replay never builds the provider client and never reads
`.env`. A request with no saved response becomes a visible `no_recording` error. Two keyless replays reproduce
`runs/report/observed.json` byte for byte. Labels: **LIVE** (a new call), **REPLAYED** (a saved real response),
**REUSED APPROVAL** (no model call), and **SIMULATED** (hand-written replies, used only in tests).
`runs/report/observed-live.json` is the original recording run, with the calls that were live labelled LIVE.

## Architecture

```
data/seed/seed.json (+ data/changes/*.json) -> dataset: load, validate IDs, authority from supersedes
request (Q1–Q8) -> review.process_request, per question:
   newest approval for the exact question text, not stale? -> reuse it (no model call)
   else drafting.draft_item: Gemini draft (JSON: answer, citations, excerpts)
        -> code checks: cited IDs exist, passage is current, excerpt verbatim
        -> recorded Gemini support check: does the cited text support every claim?
        -> status answered / unresolved (with reason) / error; owner from the topic map
reviewer (ui.py): edit, approve (guard + support check + version snapshot), leave unresolved with a note
state/workspace.json (append-only records) <-> ui.py;  version change -> sticky "needs review" mark
scenario.py -> runs/report/observed.json -> reference/grade.py (independent) -> docs/RESULTS.md
```

Modules are listed in decision 032. **Who decides what (decision 035):** code decides only mechanical facts: which
documents are current (from `supersedes`), whether a cited ID exists, whether an excerpt is verbatim, whether a
version changed, the owner, exact question matching, statuses and counts. Meaning is decided by recorded model
reasoning (the draft and the support check) and by the reviewer; a strengthening-word list ("only", "every", …) is
shown as a hint and never decides.

**Documents are data, not instructions.** The prompts hold only instructions; passages are sent as a JSON data
message. Only current passages are sent, and dates, versions and status are not sent at all. The model has no tools,
so approval, reuse and routing happen only through code paths the reviewer triggers.

## Model configuration

Gemini `gemini-3.8-flash` (checked as stable on Google's model list on 2026-10-08), thinking level medium, default
temperature, top-p and top-k, 3 retries, 60 s timeout: `config/models.toml`. Prompts: `prompts/draft_answer.md`,
`prompts/check_support.md`; the grader's judge prompt: `reference/judge_prompt.md`. Model access: the author's own
Gemini API key. No access was arranged with the hiring team, and none is claimed. The recorded run used about 8.6k
input, 1.1k output and 2.3k thinking tokens for 16 application calls.

## Data and assumptions

The data is the supplied seed, unchanged; nothing was added (decision 033). Beside it: the scripted reviewer input
for the scenario and one change file that bumps EXPORT-v2 from version 2 to 3. How and why: `data/GENERATION.md`.

Ambiguity decisions (full records in `docs/decisions/`):

| Question | Decision |
|---|---|
| `status: superseded` vs the `supersedes` field | Only `supersedes` gives or removes authority; a disagreeing status is a warning (001, 034) |
| A newer date or higher version without `supersedes` | Grants no authority; disagreeing current passages stay unresolved for review (002) |
| A documented "not offered" vs no documentation | "Live chat is not offered." answers Q4 "No"; silence is unknown (005) |
| "can" vs "only" | Answers are never stronger than the passage; the support check decides, the word list only hints (006) |
| What to cite when a passage holds two facts | Passage ID plus one verbatim sentence (008) |
| What counts as a version change | The document's `version` differs from the approved one, or it is now replaced or missing (010) |
| A version that changes back | The mark stays until a person re-approves (011) |
| Exact question matching | Same text after Unicode NFC and whitespace collapse; case and wording must match (014) |
| "Asked again" | A later request of the same questionnaire; earlier items never change (015) |
| What blocks an approval | Mechanical problems block; a failed or unavailable support check needs a note and is stored as an override (016) |
| Who approves | A free-text approver is recorded; there is no login (019) |
| Statuses and counts | answered, unresolved, approved, needs_review, error; disjoint per request (020) |
| Bad references in the data | Reported with the ID, the item left out, the rest loads; no default owner (021) |
| Scope | Only what the assignment requires, plus export and revision history (037) |

## Reference cases and check results

The answer key (`reference/expected.json`) has five reference cases, one per minimum check, plus extra rows. It was
derived from the passages and metadata, drafted with AI assistance, checked by a separate AI review agent, approved
by the author, and never taken from application output (`reference/README.md`). Results from the recorded run
(`docs/RESULTS.md`):

| Check | Result |
|---|---|
| MIN-1 Q3 answered from SUPPORT-v1:p1, excerpt verbatim | Mechanical PASS; meaning PENDING (judge PASS, awaiting the author's sign-off) |
| MIN-2 Q2 unresolved, Product reviewer, no invented answer | PASS |
| MIN-3 Q1 cites EXPORT-v2:p1 and shows EXPORT-v1:p1 as replaced | Mechanical PASS; **meaning FAIL** (below) |
| MIN-4 approved correction reused; unapproved edits not reused | PASS |
| MIN-5 reload keeps state; version change → needs review | PASS |
| Counts at every step | PASS |

**The failure.** For Q1 Gemini answered "No, free-plan users cannot export CSV." The recorded judge found that it
does not state the key's second fact, "CSV export is for paid plans only" (the seed's answer is "No, paid plans
only."). The answer is correct but incomplete against the key. It is not hidden and the key was not changed. The
fix is either the author signing it off as acceptable or a prompt change followed by re-recording; that choice is
the author's.

Small fixed sets like this are limited evidence of how the system behaves on other data.

## Time spent

To be filled in by the author.

## Known limitations

- The judge is the same model family as the drafter, so it may favour similar wording; the author's sign-off is the
  final say on meaning.
- A conflict that metadata does not resolve is shown only in a test, because the supplied seed has none.
- No question needs facts from two documents, so synthesis across documents is not demonstrated.
- A text change without a version change, or a new contradicting document, does not mark an approval for review
  (the rule names version changes only; decisions 010, 012).
- In replay mode, a reviewer's own new wording has no saved support check, so approving it needs a note and is
  labelled an override; in record mode the check runs live.
- Code checks that a contradiction's quotes are real, but cannot judge whether it is about the same question.
- Two browser tabs writing at once: the last write wins (the file is never corrupted).

## Requirement IDs used in code and records

Docstrings and decision records cite the assignment's requirements by short IDs: **RULE-1…4** are the four rules
in `data/seed/domain.md`; **MIN-1…5** the minimum checks; **REQ-D1/D2** data processing, **REQ-A1/A2/A3** drafting,
conflicts and counts/reuse, **REQ-U1/U2** the workspace, **REQ-T1/T2** technical implementation; **REF-2** expected
results kept apart from application output; **GEN-2** saved real responses and replay; **HIRE-2** simple local
storage; **OPT-1** export and **OPT-3** revision history. Decision records also carry the ambiguity numbers used
during planning (AMB-1…36); each record restates its question in full, so the number is only a cross-reference.

## Repository map

| Path | What |
|---|---|
| `src/qa/` | The application (modules in decision 032) |
| `prompts/`, `config/models.toml` | Model instructions and settings |
| `data/seed/` | Supplied seed, unchanged (protected); `data/scenario/`, `data/changes/` are the added inputs |
| `reference/` | Answer key, grader, judge prompt, sign-offs (protected) |
| `runs/` | Saved real model responses, judge verdicts, the observed report |
| `docs/` | Decisions, results table, LLM usage note, walkthrough, research notes |
| `tests/` | Offline tests, one per rule or requirement |
| `ai-workflow/` | AI configuration record |
| `.claude/`, `CLAUDE.md`, `AGENTS.md` | Assistant settings, protect-paths hook, subagents, starter-pack skill |
| `starter-pack/` | Supplied material, unchanged (protected) |
