// SANITIZED SNAPSHOT of a Claude Code workflow script (multi-agent orchestration) used during development.
// Workflow: qa-build. Used for the first milestone (M0) only; later milestones were built directly in the main
// session. M0 ran with the earlier effort settings; the change-log entry below was prepared for later milestones.
// The original lives in a local-only, git-ignored folder; this copy is for reading, not for running as-is.
// Removed or replaced, values not shown:
// - paths of the local-only planning files: the working brief is <PLAN_FILE>, the merged plan is
//   <IMPLEMENTATION_PLAN_FILE>, the progress-note folder is <PROGRESS_DIR>;
// - the "Teach" phase and every instruction about it: it maintained the author's private study notes, which are
//   not exercise configuration;
// - the author's first name (now "the author") and the name of the local instruction file and folder (now "the
//   author's local instructions" and "local-only files").
// Everything else (prepare, sequential implement, check loop, multi-lens review with refuters, fix, report) is
// unchanged. To run it again: pass real files through args ({ milestone, plan }) and replace the placeholders.

export const meta = {
  name: 'qa-build',
  description: 'Phase 2: build one milestone of the implementation plan with a test loop, multi-lens verification and fixes',
  whenToUse: 'Once per milestone, after the author approved the implementation plan. Pass args: { milestone: "M1" }.',
  phases: [
    { title: 'Prepare', detail: 'read the milestone, list tasks and human gates' },
    { title: 'Implement', detail: 'one task at a time, tests with the code' },
    { title: 'Check', detail: 'format, lint and tests in a loop until green or no progress' },
    { title: 'Verify', detail: 'four lenses review the milestone, skeptics try to refute each issue' },
    { title: 'Fix', detail: 'fix confirmed issues and re-check' },
    { title: 'Report', detail: 'progress note and summary for the author' },
  ],
}

// ---------- inputs ----------
const A = args || {}
const MILESTONE = A.milestone
if (!MILESTONE) throw new Error('Pass args: { milestone: "M1" } (the milestone id from the implementation plan).')
const PLAN = A.plan || '<IMPLEMENTATION_PLAN_FILE>'
const ALLOW_LIVE = A.allowLive === true
const GATES_DONE = A.gatesDone === true
const MAX_FIX_ROUNDS = typeof A.maxFixRounds === 'number' ? A.maxFixRounds : 4

// ---------- change log ----------
// 2026-10-08, the author, applies from M1 on (M0 ran with the earlier version):
// - Implement agents run at effort 'high'.
// - Prepare and Verify (review lenses and refuters) are pinned to effort 'max'.
// - Unchanged: checks run at 'low'; the fix and report agents inherit the session effort.
// - Why: implement tasks were too slow at max effort in M0.
// Each entry below is also written into the progress note of the milestone it first applies to.
const CHANGES = [
  {
    from: 'M1',
    date: '2026-10-08',
    text: 'At the author\'s request: implement agents run at effort high; Prepare and Verify (review lenses and refuters) stay at effort max; checks stay at low; fix and report agents inherit the session effort. Reason: implement tasks were too slow at max effort in M0.',
  },
]
const CHANGES_NOW = CHANGES.filter(c => c.from === MILESTONE)

const RULES = [
  'Project: Questionnaire Evidence & Review Workspace. Working brief: <PLAN_FILE>. Implementation plan: ' + PLAN + '. Current milestone: ' + MILESTONE + '.',
  'Follow CLAUDE.md and the author\'s local instructions (protected paths, privacy, clean code).',
  'Never edit starter-pack/, data/seed/ or reference/ (reference/ only if the plan says the human has unlocked it). Never read .env.',
  ALLOW_LIVE
    ? 'Live model calls are ALLOWED in this run; every live response must be recorded and labelled live.'
    : 'Do NOT make live model calls. Use recorded responses or clearly labelled simulated fixtures.',
  'Public files must never mention, link or quote local-only files.',
  'No time estimates. Do not commit; the author reviews the diff and commits.',
].join('\n')

// ---------- Prepare ----------
phase('Prepare')
const TASKS = {
  type: 'object',
  required: ['milestoneFound', 'tasks', 'humanGates'],
  properties: {
    milestoneFound: { type: 'boolean' },
    tasks: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'title', 'acceptance', 'requirementIds'],
        properties: {
          id: { type: 'string' },
          title: { type: 'string' },
          acceptance: { type: 'array', items: { type: 'string' } },
          files: { type: 'array', items: { type: 'string' } },
          requirementIds: { type: 'array', items: { type: 'string' } },
        },
      },
    },
    humanGates: { type: 'array', items: { type: 'string' } },
  },
}
const prep = await agent(
  RULES + '\n\nRead ' + PLAN + ' and extract milestone ' + MILESTONE + ': its tasks in order (each with acceptance criteria, likely files, requirement IDs) and any human gates ' +
  '(API keys, live runs, answer-key review, recordings). Also read <PROGRESS_DIR> to see what earlier milestones left open. Do not modify files.',
  { label: 'prepare', phase: 'Prepare', schema: TASKS, effort: 'max' },
)
if (!prep || !prep.milestoneFound) throw new Error('Milestone ' + MILESTONE + ' not found in ' + PLAN)
if (prep.humanGates.length && !GATES_DONE) {
  log('Human gates for ' + MILESTONE + ': ' + prep.humanGates.join(' | '))
  return { stopped: 'human gates must be cleared first; re-run with args.gatesDone=true', humanGates: prep.humanGates, tasks: prep.tasks.map(t => t.id + ' ' + t.title) }
}

// ---------- Implement (sequential: tasks may touch the same files) ----------
phase('Implement')
const implNotes = []
for (const t of prep.tasks) {
  const r = await agent(
    RULES + '\n\nImplement task ' + t.id + ': ' + t.title + '\nAcceptance criteria:\n- ' + t.acceptance.join('\n- ') + '\nRequirement IDs: ' + t.requirementIds.join(', ') +
    '\nWrite tests with the code for code-only logic (no network). Keep the code clean and small. Record any meaningful choice as a decision in docs/decisions/. ' +
    'When done, run the relevant tests yourself. Return what you changed and anything left open.',
    // From M1 on: effort high (see the change log at the top).
    { label: 'impl:' + t.id, phase: 'Implement', effort: 'high' },
  )
  implNotes.push({ task: t.id, notes: r })
}

// ---------- Check loop ----------
const CHECK = {
  type: 'object',
  required: ['passed', 'failureCount', 'failures'],
  properties: {
    passed: { type: 'boolean' },
    failureCount: { type: 'number' },
    failures: { type: 'array', items: { type: 'object', required: ['where', 'message'], properties: { where: { type: 'string' }, message: { type: 'string' } } } },
  },
}
const runChecks = label => agent(
  RULES + '\n\nRun, without changing any file: uv run ruff format --check . ; uv run ruff check . ; uv run pytest -q ; and the project replay/check command if it exists. ' +
  'Report passed=true only if every command succeeded. failureCount = number of distinct failures. Quote the exact failing output.',
  { label: label, phase: 'Check', schema: CHECK, effort: 'low' },
)
let check = await runChecks('check:0')
let best = check ? check.failureCount : Infinity
let stale = 0
let round = 0
while (check && !check.passed && round < MAX_FIX_ROUNDS && stale < 2) {
  round++
  await agent(
    RULES + '\n\nFix these check failures properly (fix the cause, never weaken or skip a test, never edit the answer key to match the code):\n' + JSON.stringify(check.failures, null, 1),
    { label: 'fix-checks:' + round, phase: 'Check' },
  )
  check = await runChecks('check:' + round)
  if (check && check.failureCount < best) { best = check.failureCount; stale = 0 } else { stale++ }
  log('check round ' + round + ': ' + (check ? (check.passed ? 'green' : check.failureCount + ' failures') : 'no result'))
}
if (check && !check.passed) log('checks still failing after ' + round + ' rounds; continuing to verification so the issues are reported')

// ---------- Verify: diverse lenses, then skeptics per issue ----------
const ISSUES = {
  type: 'object',
  required: ['issues'],
  properties: {
    issues: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'severity', 'statement', 'evidence'],
        properties: {
          id: { type: 'string' },
          severity: { type: 'string', enum: ['blocking', 'important', 'minor'] },
          statement: { type: 'string' },
          evidence: { type: 'string' },
          file: { type: 'string' },
        },
      },
    },
  },
}
const REFUTE = { type: 'object', required: ['refuted', 'reason'], properties: { refuted: { type: 'boolean' }, reason: { type: 'string' } } }
const LENSES = [
  { key: 'rules-requirements', text: 'Does the milestone apply the four rules in data/seed/domain.md exactly and meet every acceptance criterion and requirement ID listed for it? Quote the brief and the code.' },
  { key: 'code-quality', text: 'Is the code clean and explainable by a junior engineer: small functions, clear names, type hints, why-docstrings, no dead or duplicated code, visible errors, tests that test behaviour?' },
  { key: 'honesty-evidence', text: 'Is the answer key independent of the app, are live/replayed/simulated results labelled, are failures reported, do README/check claims match the code and recordings?' },
  { key: 'security-privacy', text: 'Are secrets absent (git grep for keys), is .env untouched, is document text kept separate from instructions, and do public files avoid any mention of local-only files? Check git status for staged local-only paths.' },
]
const tasksText = prep.tasks.map(t => t.id + ' ' + t.title + ' | acceptance: ' + t.acceptance.join('; ')).join('\n')
const confirmed = (await pipeline(
  LENSES,
  lens => agent(
    RULES + '\n\nReview milestone ' + MILESTONE + ' (git diff against HEAD plus new files) through this lens: ' + lens.text + '\nTasks:\n' + tasksText +
    '\nReport concrete issues with evidence (file:line and quote). Do not modify files.',
    { label: 'review:' + lens.key, phase: 'Verify', schema: ISSUES, effort: 'max' },
  ),
  (res, lens) => {
    const serious = res && res.issues ? res.issues.filter(i => i.severity !== 'minor') : []
    const minor = res && res.issues ? res.issues.filter(i => i.severity === 'minor') : []
    if (!serious.length) return { lens: lens.key, confirmed: [], minor: minor }
    return parallel(serious.map(issue => () => parallel([0, 1].map(k => () => agent(
      RULES + '\n\nTry to REFUTE this review issue. Open the cited code and the brief. refuted=true if the issue is wrong or not actually a problem; if uncertain, refuted=false.\nISSUE: ' + JSON.stringify(issue),
      { label: 'refute:' + issue.id + ':' + k, phase: 'Verify', schema: REFUTE, effort: 'max' },
    ))).then(votes => ({ issue: issue, survives: votes.filter(Boolean).filter(v => !v.refuted).length >= 1 }))))
      .then(rs => ({ lens: lens.key, confirmed: rs.filter(Boolean).filter(r => r.survives).map(r => r.issue), minor: minor }))
  },
)).filter(Boolean)
const toFix = confirmed.flatMap(c => c.confirmed)
const minors = confirmed.flatMap(c => c.minor)
log(toFix.length + ' confirmed issues to fix, ' + minors.length + ' minor notes')

// ---------- Fix ----------
let finalCheck = check
if (toFix.length) {
  phase('Fix')
  await agent(
    RULES + '\n\nFix every confirmed issue below at its cause. If an issue needs a human decision, do not guess: write it under "Needs the author" in your answer.\n' + JSON.stringify(toFix, null, 1),
    { label: 'fix-review', phase: 'Fix' },
  )
  finalCheck = await runChecks('check:after-fix')
}

// ---------- Report ----------
phase('Report')
const report = await agent(
  RULES + '\n\nWrite <PROGRESS_DIR>/' + MILESTONE + '.md: tasks done, acceptance criteria met or not (with evidence), check results, confirmed issues and how they were fixed, minor notes, ' +
  'anything that needs the author, files changed (git status), and suggested commit message(s). Then return a 10-line summary.\n' +
  (CHANGES_NOW.length
    ? 'Add a section "Workflow changes" that records, word for word: ' + CHANGES_NOW.map(c => c.date + ' — ' + c.text).join(' | ') + '\n'
    : '') +
  'Final check: ' + JSON.stringify(finalCheck) + '\nConfirmed issues: ' + JSON.stringify(toFix) + '\nMinor: ' + JSON.stringify(minors),
  { label: 'report', phase: 'Report' },
)

return {
  milestone: MILESTONE,
  tasks: prep.tasks.map(t => t.id),
  checksGreen: !!(finalCheck && finalCheck.passed),
  fixRounds: round,
  confirmedIssues: toFix.length,
  summary: report,
}
