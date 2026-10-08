# 041 · The drafting model gets one read-only tool, search_passages, at most twice

- Status: accepted (changes "the model has no tools" in the README; everything that acts still happens in code)
- Requirements: RULE-1 ("An undocumented feature is unknown"); RULE-3 (only approved answers are reused); RULE-4
  (topic-to-reviewer routing); GEN-2 (record and replay).

## Context

With retrieval (decision 040) the first five passages may miss the one that answers. Letting the model search again
in its own words gives it a second try. A tool-using model is also a new risk: a passage could contain instructions,
and anything the model can trigger could be triggered by a passage.

## Options considered

1. **No loop.** Retrieval misses become "undocumented" with no second try.
2. **Native Gemini function calling.** Gemini 3 needs its thought signatures passed back on every turn, and
   structured output together with function calling is listed as a preview feature. Recording and replaying a
   multi-turn exchange would have to store and resend those signatures.
3. **The tool call as a structured-output action.** Each step is one ordinary request whose JSON reply either asks for
   `search_passages(query)` or gives the final draft. Code runs the search and sends a new, self-contained request
   with the passages found so far, the searches made and `searches_left`. Every step records and replays exactly like
   any other call. Chosen.

## Decision

Option 3, in `src/qa/drafting.py` (`_search_loop`) and `prompts/draft_answer.md`:

- The reply schema has `action`: `"search_passages"` or `"answer"`, and nothing else; a test checks that. The search
  is the same hybrid retrieval, over current passages only, and it changes nothing.
- At most `max_searches = 2` searches (`config/retrieval.toml`). Asking for a third is a visible error, `step_limit`.
  Small budgets are supported by evidence that more tool calls stop helping (Liu et al., *Budget-Aware Tool Use*,
  2025; McCleary and Ghawaly, LREC 2026).
- Code checks are unchanged and now also require that a cited or conflicting passage is one the model was shown
  (`invalid_citation` otherwise).
- Approving, reusing, routing, notes and stale marks stay in code that only the reviewer's actions or the scenario
  trigger. Once a model has read untrusted text it must not be able to cause consequential actions (Beurer-Kellner et
  al., *Design Patterns for Securing LLM Agents against Prompt Injections*, 2025); its only action here is a read.
- Every step is stored in the suggestion (`steps`: query, passages found, new passages, embedding labels) and shown
  in the UI's "Checks and raw draft" panel.

## Consequences

- An undocumented question now costs up to three draft calls instead of one; in the recorded run the model searched
  only on the eight undocumented or partial questions.
- ReAct-style loops (Yao et al., ICLR 2023; IRCoT, Trivedi et al., ACL 2023) are measured on multi-step questions.
  Questionnaire questions are mostly one step, so here the loop is mainly a second try after a retrieval miss.

## Evidence

- `tests/test_search_loop.py` (steps recorded, the step limit, unseen citations rejected, one tool only).
- `uv run qa inspect S1 R1/X9 --extended` shows the two searches the model made for X9.
- Yao et al., ReAct, https://arxiv.org/abs/2210.03629; Trivedi et al., IRCoT, https://arxiv.org/abs/2212.10509; Liu et
  al., https://arxiv.org/abs/2511.17006; McCleary and Ghawaly, https://arxiv.org/abs/2603.08877; Beurer-Kellner et al.,
  https://arxiv.org/abs/2506.08837.

## Update: did the tool help? (2026-10-08)

`qa report` now drafts every item the model searched on a second time with no searches allowed, and the grader
compares the two outcomes. In the extended run the model searched on 9 items (X2, X3, X6, X9, X15, X22, X25, X26,
X28), and the status and reason were the same with and without searching on all 9. On this data the tool changed
nothing. It stays, read-only and capped, because a retrieval miss on messier documents is exactly what it is for, but
that benefit is not shown here. When the first retrieval already covers every current passage, no search is offered.
