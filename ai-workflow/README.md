# AI workflow used during this exercise

This folder records the AI configuration used to build the Questionnaire Evidence & Review Workspace and the
configuration the application itself uses. `manifest.json` lists every component with its purpose, path, version,
when it was used and its status (`used`, `not-used`, `default`, `redacted`, `not-exportable`). Active configuration
stays in its normal location (`.claude/`, `config/`, `prompts/`, `reference/`); this folder adds the record, the
sanitized workflow snapshots in `snapshots/` and the variable names in `.env.example`.

## Tools and models

### Development time

| Component | Version / ID | Settings | Used for |
|---|---|---|---|
| Claude Code (CLI) | 2.1.293 when this record was written; the version of each earlier session was not recorded | Project settings in `.claude/settings.json`; otherwise tool defaults | Planning, building, testing and review, 2026-10-06 to 2026-10-08 |
| Claude Opus 5.5 | `claude-opus-5-5` | Session model for the main session, workflow agents and subagents. The only changed setting is the per-step effort level inside the `qa-build` workflow (see its snapshot) | Same as above |
| Claude Code workflows (multi-agent orchestration scripts) | Part of Claude Code 2.1.293 | `snapshots/qa-deep-review.js`, `snapshots/qa-build.js` | Planning (`qa-deep-review`) and the first milestone, M0 (`qa-build`). Later milestones were built directly in the main session |
| Subagents | Inherit the session model | `verifier` (`.claude/agents/verifier.md`) and an ad-hoc UI builder with no definition file | UI builder: the Streamlit review page. `verifier`: the final verification pass |
| Plugins, connectors, MCP servers, IDE extensions | — | — | `not-used` (see below) |

The Claude Code session had connectors and plugins available (Slack, Google Drive, Claude Docs, Chrome, Telegram,
GitLab). None was used for this exercise. There is no project MCP configuration (`.mcp.json`) and no
`.claude/settings.local.json`.

### Inside the application

| Component | Value | Where it is set |
|---|---|---|
| Provider and SDK | Google Gemini through `google-genai` 2.28.0 | `pyproject.toml`, pinned in `uv.lock` |
| Model | `gemini-3.8-flash` | `config/models.toml` |
| Thinking level | `medium` (the documented default, set explicitly so it is recorded) | `config/models.toml` |
| Temperature, top_p, top_k | Not set: provider defaults | — |
| Output limit | Not set: provider default | — |
| Transport | timeout 60000 ms, 3 retry attempts (not part of a request's fingerprint) | `config/models.toml` |
| Prompts | `prompts/draft_answer.md` (draft a cited answer), `prompts/check_support.md` (check the answer against its citations) | — |
| Structured output | A JSON schema per call, stored in every recording | `src/qa/` |

The grader's meaning checks use a judge with the same model and thinking level, set in `reference/judge.py`, with
its own prompt `reference/judge_prompt.md`. The grader imports nothing from the application.

Saved real responses:

- `runs/recordings/*.json`: 35 application calls from three record runs (2026-10-07 21:29 UTC, then 2026-10-08
  05:45 and 10:20 UTC, one per prompt fix of decision 038); replay uses the latest. Each file stores the provider, model, thinking level, prompt file and its
  SHA-256, the full request (system text, user text, schema), the response and the recording time.
- `runs/judge/verdicts.json`: 7 judge verdicts, recorded 2026-10-07 21:31–21:32 UTC.

The prompt hashes stored in the recordings match the current prompt files (`7388b8c1…` for the draft prompt,
`bfbecc28…` for the support-check prompt).

## Configuration files

| What | Path | Status | Notes |
|---|---|---|---|
| Project instructions | `CLAUDE.md` | used | Non-negotiables, clean-code rules, protected paths, where files go |
| Instructions for other AI tools | `AGENTS.md` | not-used | Points other tools to `CLAUDE.md`; only Claude Code was used, and it reads `CLAUDE.md` |
| Exercise rules | `data/seed/domain.md` | used | The four supplied rules; copy of the starter pack, never edited |
| Subagent `verifier` | `.claude/agents/verifier.md` | used | Final verification pass; read-only, reports and never fixes |
| Subagent `researcher` | `.claude/agents/researcher.md` | not-used | The planning research was done by the main session and workflows; `docs/research/` holds only the planning bibliography |
| UI builder subagent | — | not-exportable | A one-off task prompt to a general-purpose subagent; no definition file exists |
| Skill `generate-assignment-data` | `.claude/skills/generate-assignment-data/SKILL.md` | used (checklist only) | Copied unchanged from `starter-pack/skills/`. Its checklist was followed when preparing the scenario inputs; no new documents were generated |
| Hook | `.claude/hooks/protect_paths.py` | used | Registered in `.claude/settings.json`; tests in `tests/test_protect_paths_hook.py` |
| Settings and permissions | `.claude/settings.json` | used | Hook registration, allow and deny lists (table below) |
| Workflow `qa-deep-review` | `ai-workflow/snapshots/qa-deep-review.js` | redacted | Sanitized snapshot; the original is local-only |
| Workflow `qa-build` | `ai-workflow/snapshots/qa-build.js` | redacted | Sanitized snapshot; the original is local-only |
| Application model settings | `config/models.toml` | used | |
| Application prompts | `prompts/draft_answer.md`, `prompts/check_support.md` | used | |
| Judge settings and prompt | `reference/judge.py`, `reference/judge_prompt.md` | used | |
| Environment variable names | `.env.example`, `ai-workflow/.env.example` | used | Names only |
| Local private instructions and planning notes | — | not-exportable | See "Redactions and omissions" |
| User-level global instruction file | — | redacted (omitted) | See "Redactions and omissions" |

### The hook: what it does and when it runs

`.claude/hooks/protect_paths.py` runs before every Claude Code `Edit`, `Write`, `MultiEdit`, `NotebookEdit`, `Bash`
and `Read` call (a `PreToolUse` hook in `.claude/settings.json`). It reads the tool call as JSON on stdin. Exit code
0 lets the call run; exit code 2 blocks it and shows the message to the agent. It enforces only the protections that
must never depend on the agent's judgement:

1. `starter-pack/` and `data/seed/` are supplied input and are never edited.
2. `reference/` (the hand-written answer key) is edited only when the human starts the session with
   `QA_ALLOW_REFERENCE_EDIT=1`, so a failing check can't be "fixed" by changing the expected answers.
3. `.env` is never read or written (`.env.example` is fine).
4. Local-only, git-ignored files are never staged, and nothing is force-added with `git add -f`.

Edit tools are checked by path. Shell commands are checked only for explicit writes into a protected path (a
redirect, `tee`, `rm`, `mv`, `sed -i` or `truncate` whose target is protected); reading is always allowed. Anything
subtler is caught by git, because every protected file is tracked. Read the script before enabling it: it is about
100 lines of standard-library Python.

Earlier version: the first hook (commit `24290b1`) blocked any shell command that mentioned a protected path and
contained a write-like word, which refused read-only commands such as `ls data/seed/ 2>&1`. Commit `59207ea`
narrowed it and added the tests. `git show 24290b1:.claude/hooks/protect_paths.py` prints the first version.

### Permissions in `.claude/settings.json`

| Rule | Kind | Why it exists |
|---|---|---|
| `Bash(uv sync)` | allow | Install the locked dependencies without a prompt |
| `Bash(uv run pytest:*)` | allow | Run the offline test suite; tests never call a live model |
| `Bash(uv run ruff:*)` | allow | Format and lint checks |
| `Bash(uv run qa:*)` | allow | Run the application CLI. Replay is the default; a live call needs `QA_MODE=record` and a key, which only the human sets |
| `Bash(git status)` | allow | Read-only: check what changed (and that nothing local-only is staged) |
| `Bash(git diff:*)` | allow | Read-only: review changes |
| `Bash(git log:*)` | allow | Read-only: inspect history, for example that `reference/` was not changed to pass a check |
| `Read(./.env)` | deny | Secrets are never read by the coding assistant (the hook enforces this too) |
| `Read(./.env.local)` | deny | Same, for a local override file |

Everything else asks for permission as usual. Commits and pushes are never pre-approved.

### Environment variable names

Listed without values in `ai-workflow/.env.example` and `.env.example`:

- `GOOGLE_API_KEY`: needed only for record mode and for `reference/judge.py`. The SDK also reads `GEMINI_API_KEY`;
  if both are set, `GOOGLE_API_KEY` wins.
- `QA_MODE`: `replay` (default) or `record`.
- `QA_STATE_DIR`: folder for the workspace state file (default `state/`, git-ignored).
- `QA_ALLOW_REFERENCE_EDIT`: developer only. Set in the shell for the session that writes the answer key; read only
  by the hook; never in `.env`.

## One workflow example

**Instruction.** Paraphrased from the setup session: "Add a hook that enforces the protected-paths table in
CLAUDE.md, so the coding agent can never fix a failing check by editing the inputs or the expected answers."

**Configuration that shaped it.** The protected-paths table in `CLAUDE.md`:

```text
| `starter-pack/**` | Never edit — unchanged copy of the supplied material. |
| `data/seed/**` | Never edit — copy of the supplied `tasks/evidence/`. |
| `reference/**` | Edit only when the human starts the session with `QA_ALLOW_REFERENCE_EDIT=1`. |
| `.env` | Never read or write. |
```

**First result and how it was checked.** The first hook (commit `24290b1`) treated any shell command that mentioned a
protected path and contained a write-like token as a write. During the planning review it blocked read-only
commands, for example `ls data/seed/ 2>&1` (the `>` of `2>&1` looked like a redirect).

**Correction.** Commit `59207ea` narrowed the hook to edits by path, shell writes whose *target* is protected, `.env`
access and staging of local-only files, and added `tests/test_protect_paths_hook.py`. The tests pin both sides, for
example:

```text
("Bash", {"command": "ls data/seed/ 2>&1"}, ALLOWED),
("Bash", {"command": "echo x > data/seed/domain.md"}, BLOCKED),
("Write", {"file_path": "reference/expected.json"}, BLOCKED),
```

and `test_answer_key_unlocked_by_human_flag` checks that `QA_ALLOW_REFERENCE_EDIT=1` unlocks `reference/` but never
`data/seed/`. `uv run pytest tests/test_protect_paths_hook.py` runs them.

## Reproduce or replay

Required tools: [uv](https://docs.astral.sh/uv/) (0.10.9 was used) and Python 3.12 (`.python-version`; uv installs
it if missing). No API key is needed.

```bash
uv sync --locked && uv run qa report && uv run python reference/grade.py
```

- `uv run qa report` runs the reference scenario from a clean state in replay mode (the default). Every model call is
  answered from `runs/recordings/` by an exact fingerprint of the request. It never loads `.env` and never builds the
  SDK client. A request with no recording is a visible error (`no_recording`), never a guess.
- `uv run python reference/grade.py` compares the result with the hand-written answer key and replays the judge
  verdicts from `runs/judge/verdicts.json`. It writes `docs/RESULTS.md`. Exit code 0: all pass; 1: any FAIL;
  3: no FAIL but something PENDING; 2: the grader crashed.

Checked on 2026-10-08 in a clean copy of the repository with no API key in the environment: the report ran and its
output was byte-identical to the committed `runs/report/observed.json`, and the grader reproduced the committed
`docs/RESULTS.md` (108 PASS, 0 FAIL, 7 PENDING the author's sign-off; exit code 3). The first run's Q1 FAIL and
its fix are described in `docs/LLM_USAGE.md`.

To record new responses (live calls, needs a key in a local `.env`): `QA_MODE=record uv run qa report`, then
`uv run python reference/judge.py` for missing verdicts. Any change to a prompt, schema or model setting changes the
fingerprint, so old recordings no longer match and must be re-recorded.

Where configuration belongs: Claude Code reads `CLAUDE.md`, `.claude/settings.json`, `.claude/hooks/`,
`.claude/agents/` and `.claude/skills/` from the repository, so cloning restores the development setup. The hook runs
with `python3` from `$CLAUDE_PROJECT_DIR`. The workflow snapshots are for reading; to run one, replace the
placeholders (for example `<PLAN_FILE>`) with real files through the script's `args`.

## Redactions and omissions

- **Local private instructions and planning notes** (`not-exportable`): personal working notes and private
  instructions; the rules that matter are restated in `CLAUDE.md` and the decision records in `docs/decisions/`.
  They are git-ignored, and their paths and contents are not reproduced here.
- **User-level global instruction file** (omitted): it holds one personal git rule (never merge into the integration
  branch; the human does every merge). It is not exercise-specific, so it is not copied (confirmed by
  the author).
- **Workflow scripts** (`redacted`): the originals live in a local-only folder. The snapshots replace the paths of
  local planning files with placeholders (`<PLAN_FILE>`, `<BRIEF_FILE>`, `<REVIEW_OUTPUT_DIR>`,
  `<IMPLEMENTATION_PLAN_FILE>`, `<PROGRESS_DIR>`), replace the author's first name with "the author", replace the
  names of the local instruction file and folder with neutral wording, and remove one step of `qa-build` that
  maintained the author's private study notes. The orchestration logic is otherwise unchanged; each snapshot's
  header lists what was removed.
- **API key**: the real key exists only in a local, git-ignored `.env`. The coding assistant never reads it (deny
  rule plus hook). Recordings store no headers, keys, absolute paths or email addresses.
- **UI builder subagent prompt** (`not-exportable`): a one-off task prompt inside a session, not saved configuration.
- **Per-session tool versions** (`not-exportable`): only the Claude Code version at the time of writing is known.

## Decisions and limitations

- **Why this setup.** One coding assistant with project instructions, one hard hook and a read-only verifier kept the
  rules that must not bend (inputs and answer key untouched, no secrets) out of the agent's judgement, while
  leaving ordinary work to review and git diffs. Multi-agent workflows were used where independent views pay off
  (planning review, the first milestone's verification); later milestones were built directly because the workflow
  was slow at maximum effort.
- **One model family.** The application, its support check and the grader's judge all use Gemini
  `gemini-3.8-flash`, so self-preference is possible. A judge from another model family would be the first change.
- **Not used.** The `researcher` subagent, `AGENTS.md`, and every connector, plugin and MCP server. No extra skills,
  agents or hooks were created to fill the manifest.
- **What I would change.** Record the Claude Code version per session, save each workflow script in the repository
  from the start (sanitized), and give the UI builder a definition file so it can be restored.
