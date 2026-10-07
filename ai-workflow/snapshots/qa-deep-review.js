// SANITIZED SNAPSHOT of a Claude Code workflow script (multi-agent orchestration) used during development.
// Workflow: qa-deep-review. Used during planning, before any application code was written.
// The original lives in a local-only, git-ignored folder; this copy is for reading, not for running as-is.
// Removed or replaced, values not shown:
// - paths of the local-only planning files: the working brief is <PLAN_FILE>, the assignment brief is <BRIEF_FILE>,
//   the review output folder is <REVIEW_OUTPUT_DIR>, the merged plan is <IMPLEMENTATION_PLAN_FILE>;
// - the author's first name (now "the author");
// - the name of the local-only folder in one prompt line (now "local-only files").
// Everything else (phases, schemas, prompts, agent fan-out, verification and judging logic) is unchanged.
// To run it again: pass real files through args ({ plan, outDir, finalPlan }) and replace <BRIEF_FILE>.

export const meta = {
  name: 'qa-deep-review',
  description: 'Phase 1: deep read-only review of brief, data and rules, verified findings, three judged plans, merged implementation plan',
  whenToUse: 'Before any implementation. Re-run after major changes to the brief or data.',
  phases: [
    { title: 'Map', detail: 'six independent lenses read everything and report findings with evidence' },
    { title: 'Verify', detail: 'a skeptic per lens re-opens the evidence and drops or corrects findings' },
    { title: 'Design', detail: 'three independent implementation plans from different angles' },
    { title: 'Judge', detail: 'two judges score every plan against the requirements' },
    { title: 'Synthesize', detail: 'merge, completeness critic, patch, write the output files' },
  ],
}

// ---------- inputs ----------
const A = args || {}
const PLAN = A.plan || '<PLAN_FILE>'
const OUT = A.outDir || '<REVIEW_OUTPUT_DIR>'
const FINAL = A.finalPlan || '<IMPLEMENTATION_PLAN_FILE>'

const CONTEXT = [
  'Project: Questionnaire Evidence & Review Workspace (Provectus Junior AI Engineer take-home, Alternative C).',
  'Read in full before answering: ' + PLAN + ' (working brief: verbatim requirements with IDs, inputs, ambiguities, design space, references);',
  '<BRIEF_FILE> (authoritative brief: open the Alternative C tab and the "For the hiring team" section);',
  'data/seed/domain.md, data/seed/seed.json, data/seed/expected-seed-results.json, data/seed/document.template.json;',
  'starter-pack/README.md; .claude/skills/generate-assignment-data/SKILL.md; ai-workflow/manifest.template.json; ai-workflow/README.template.md.',
  'This phase is READ-ONLY: do not create, edit or delete any file unless your instructions name a specific output file.',
  'Evidence rule: every claim cites a file path with an exact quote, or a URL you opened with an exact quote. Anything you cannot cite is labelled an assumption.',
  'Do not estimate time or schedule anything.',
].join('\n')

// Agents that return nothing (API error, timeout or skip) are logged and listed in the result, never dropped silently.
// The list never goes into a prompt, so a resumed run keeps its cached agent results.
const failed = []
function noteFailure(label, consequence) {
  failed.push(label)
  log('FAILED: ' + label + ' returned nothing; ' + consequence)
}

const FINDINGS = {
  type: 'object',
  required: ['summary', 'items'],
  properties: {
    summary: { type: 'string' },
    items: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'kind', 'statement', 'evidence', 'severity'],
        properties: {
          id: { type: 'string' },
          kind: { type: 'string', enum: ['requirement', 'fact', 'logic', 'gap', 'ambiguity', 'risk', 'option', 'test-case', 'constraint'] },
          statement: { type: 'string' },
          evidence: { type: 'array', items: { type: 'string' } },
          severity: { type: 'string', enum: ['blocking', 'important', 'minor'] },
          requirementIds: { type: 'array', items: { type: 'string' } },
        },
      },
    },
  },
}

const VERDICTS = {
  type: 'object',
  required: ['verdicts'],
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'keep', 'reason'],
        properties: {
          id: { type: 'string' },
          keep: { type: 'boolean' },
          corrected: { type: 'string' },
          reason: { type: 'string' },
        },
      },
    },
  },
}

const LENSES = [
  {
    key: 'requirements',
    prompt: 'LENS: requirements tracer. Trace every requirement ID in the working brief (RULE-*, DATA-*, REF-*, REQ-*, MIN-*, SCOPE, GEN-*, OPT-*, AI-*, SUB-*, HIRE-*) to (a) testable acceptance criteria, (b) the inputs needed to demonstrate it, (c) how a reviewer would verify it. Report contradictions or gaps between the brief HTML, domain.md and the working brief. Use kind=requirement for each traced requirement (put the acceptance criteria in the statement) and kind=gap/ambiguity for problems.',
  },
  {
    key: 'data',
    prompt: 'LENS: data analyst. Analyse the seed exhaustively: every document, passage, sentence, version, date, status, supersedes link, question, topic and owner. Build the logic map: for EACH question, the relevant passages (quote them), the authority that applies, the rule that decides the outcome, and the expected status / answer facts / allowed sources / conflict to show / owner, derived by source inspection only. Note edge cases inside the data (two facts in one passage, documented negatives versus unknown, "can" versus "only", the redundant status field, shared dates). List scenarios required by the brief that the seed cannot demonstrate and propose minimal rule-consistent additions, each tied to the check it serves (proposals only). Use kind=logic for per-question derivations and kind=test-case for proposed reference cases.',
  },
  {
    key: 'rules',
    prompt: 'LENS: rules logician. Formalise the four rules in domain.md and the related requirements as precise logic: authority resolution; conflict classes (resolved by explicit metadata versus not); abstention when evidence is missing; owner routing; the draft / edit / approval / reuse lifecycle; version-change staleness; exact question matching. Express each as a decision table or state machine listing every transition, then enumerate edge cases and which ambiguity (AMB-*) each depends on, with the options and consequences of each choice.',
  },
  {
    key: 'research',
    prompt: 'LENS: research reviewer. For each design area in the working brief section 7, open the most relevant primary sources from section 11 and check the claims the working brief attributes to them. Report which techniques are applicable to API-based models in a small local project, what each would cost in complexity, and what verifiable evidence each would add for reviewers. Flag every reference claim you could not confirm. Use kind=option for applicable techniques and kind=risk for unconfirmed claims.',
  },
  {
    key: 'assessment',
    prompt: 'LENS: reviewer and interviewer. Read the evaluation criteria, the hiring-team notes and the submission list as the Provectus reviewer would. List what the reviewer will check, likely failure points, honesty traps (answer-key independence, live versus replayed versus simulated labels, replay without keys, AI-configuration completeness, secrets), and what the follow-up interview will probe (explain a module, inspect a failure, change an input, explain a setting). Turn each into a concrete acceptance check (kind=test-case) or risk.',
  },
  {
    key: 'platform',
    prompt: 'LENS: platform engineer. Investigate the technical platform with current official sources: the libraries in pyproject.toml and uv.lock, LangGraph v1 versus plain code, the Gemini and Claude APIs (structured output, citation features, thought signatures, current model IDs from the official model lists), approaches to recording and replaying real model responses, SQLite versus JSON storage, Streamlit versus alternatives, testing without network access. Report constraints, version facts and risks with sources (kind=constraint/fact/risk/option).',
  },
]

// ---------- Map + Verify (pipelined per lens) ----------
const verified = await pipeline(
  LENSES,
  lens => agent(CONTEXT + '\n\n' + lens.prompt + '\nPrefix item ids with "' + lens.key + '-".', {
    label: 'map:' + lens.key, phase: 'Map', schema: FINDINGS,
  }),
  (res, lens) => {
    if (!res) noteFailure('map:' + lens.key, 'this lens contributes no findings')
    if (!res || !res.items || !res.items.length) return { lens: lens.key, summary: res ? res.summary : 'no result', items: [] }
    return agent(
      CONTEXT + '\n\nYou are a skeptic checking the findings of the "' + lens.key + '" reviewer. For EACH item: open the cited evidence and try to refute the statement. ' +
      'keep=false if the evidence is missing, misquoted, or the statement does not follow from it. If it is partly right, keep=true and give a corrected statement. ' +
      'If you cannot confirm it, keep=false. Return one verdict per item id.\n\nITEMS:\n' + JSON.stringify(res.items, null, 1),
      { label: 'verify:' + lens.key, phase: 'Verify', schema: VERDICTS },
    ).then(v => {
      const byId = {}
      ;(v && v.verdicts ? v.verdicts : []).forEach(x => { byId[x.id] = x })
      const kept = res.items
        .filter(it => byId[it.id] && byId[it.id].keep)
        .map(it => (byId[it.id].corrected ? Object.assign({}, it, { statement: byId[it.id].corrected }) : it))
      const dropped = res.items.length - kept.length
      log(lens.key + ': ' + kept.length + ' findings kept, ' + dropped + ' dropped by the skeptic')
      return { lens: lens.key, summary: res.summary, items: kept, dropped: dropped }
    })
  },
)
const lensResults = verified.filter(Boolean)
const findingsJson = JSON.stringify(lensResults, null, 1)

// ---------- Design: three independent plans (needs ALL verified findings -> barrier is correct) ----------
const PLAN_SCHEMA = {
  type: 'object',
  required: ['plan_markdown', 'key_decisions', 'open_risks'],
  properties: {
    plan_markdown: { type: 'string' },
    key_decisions: {
      type: 'array',
      items: {
        type: 'object',
        required: ['decision', 'rationale', 'requirementIds'],
        properties: { decision: { type: 'string' }, rationale: { type: 'string' }, requirementIds: { type: 'array', items: { type: 'string' } } },
      },
    },
    open_risks: { type: 'array', items: { type: 'string' } },
  },
}

const ANGLES = [
  { key: 'simplest-robust', text: 'the fewest moving parts that still meet EVERY requirement, easiest for the author to explain line by line in the interview' },
  { key: 'evidence-first', text: 'the strongest verifiable guarantees within scope: citation and support checks, answer-key independence, record and replay, honest evaluation' },
  { key: 'reviewer-experience', text: 'what the reviewer runs, sees and checks: setup in minutes, the demonstration path for MIN-1..MIN-5, visible failures and labels' },
]

phase('Design')
const plans = await parallel(ANGLES.map(angle => () => agent(
  CONTEXT + '\n\nVERIFIED FINDINGS FROM THE REVIEW:\n' + findingsJson + '\n\n' +
  'Write a complete implementation plan optimised for: ' + angle.text + '. It must cover: architecture and components; data additions with the check each serves; ' +
  'how the answer key is derived and kept independent; a decision for every ambiguity (AMB-*) with rationale; the state model for drafts, edits, approvals, reuse and staleness; ' +
  'model integration, recording, replay and failure handling; the verification of citations and support; the review workspace UI; tests and the minimum-demonstration report; ' +
  'the AI-configuration record; clean-code conventions; an ordered list of milestones, each with acceptance criteria and the requirement IDs it closes (NO time estimates); ' +
  'human gates (keys, live runs, answer-key review); risks; and what you deliberately leave out. Do not write any file.',
  { label: 'plan:' + angle.key, phase: 'Design', schema: PLAN_SCHEMA },
).then(p => (p ? Object.assign({ angle: angle.key }, p) : null))))
const candidates = plans.filter(Boolean)

// ---------- Judge ----------
const SCORES = {
  type: 'object',
  required: ['scores'],
  properties: {
    scores: {
      type: 'array',
      items: {
        type: 'object',
        required: ['angle', 'score', 'strengths', 'weaknesses', 'missing_requirements'],
        properties: {
          angle: { type: 'string' },
          score: { type: 'number' },
          strengths: { type: 'array', items: { type: 'string' } },
          weaknesses: { type: 'array', items: { type: 'string' } },
          missing_requirements: { type: 'array', items: { type: 'string' } },
        },
      },
    },
  },
}
const JUDGES = [
  { key: 'coverage-correctness', text: 'requirement coverage (every ID), correct application of the four rules, answer-key independence, correctness of the logic' },
  { key: 'simplicity-honesty', text: 'simplicity, explainability by a junior engineer, honest reporting and labelling, risk of over-engineering' },
]
phase('Judge')
const candidatesJson = JSON.stringify(candidates, null, 1)
const judgments = (await parallel(JUDGES.map(j => () => agent(
  CONTEXT + '\n\nScore each candidate plan from 1 to 10 for: ' + j.text + '. List strengths, weaknesses and any requirement IDs it misses. Be strict and specific.\n\nCANDIDATE PLANS:\n' + candidatesJson,
  { label: 'judge:' + j.key, phase: 'Judge', schema: SCORES },
).then(r => (r ? Object.assign({ judge: j.key }, r) : null))))).filter(Boolean)
JUDGES.forEach(j => { if (!judgments.some(x => x.judge === j.key)) noteFailure('judge:' + j.key, 'the merge gets no scores from this judge') })

// ---------- Synthesize, critic, patch, write ----------
phase('Synthesize')
const merged = await agent(
  CONTEXT + '\n\nMerge the candidate plans into ONE implementation plan. Start from the highest-scoring plan and graft in the best ideas from the others; resolve conflicts explicitly and say why. ' +
  'Keep every requirement covered, keep it as simple as the requirements allow, no time estimates. Return the full plan in markdown with these sections: ' +
  'Summary; Requirement coverage table (ID -> where it is met -> how it is checked); Architecture; Data additions; Answer key; Ambiguity decisions (AMB-*); State model; ' +
  'Model integration and replay; Verification; UI; Tests and minimum-demonstration report; AI-configuration record; Clean-code conventions; Milestones (ordered, each with tasks, acceptance criteria, requirement IDs, human gates); ' +
  'Risks; Deliberately out of scope; Open questions for the author.\n\nCANDIDATES:\n' + candidatesJson + '\n\nJUDGMENTS:\n' + JSON.stringify(judgments, null, 1),
  { label: 'merge', phase: 'Synthesize' },
)
if (!merged) {
  noteFailure('merge', 'stopping before the critic so that no file is written from an empty plan')
  return { stoppedBeforeWriting: true, failed: failed, next: 'Resume this run to retry the merge and the steps after it.' }
}

const GAPS = {
  type: 'object',
  required: ['missing'],
  properties: { missing: { type: 'array', items: { type: 'object', required: ['what', 'why'], properties: { what: { type: 'string' }, why: { type: 'string' }, requirementIds: { type: 'array', items: { type: 'string' } } } } } },
}
const critic = await agent(
  CONTEXT + '\n\nYou are a completeness critic. Compare the plan below with EVERY requirement ID and every ambiguity in the working brief, and with the verified findings. ' +
  'List anything missing, contradicted, unverifiable, or likely to fail review. Return an empty list only if nothing is missing.\n\nPLAN:\n' + merged + '\n\nVERIFIED FINDINGS:\n' + findingsJson,
  { label: 'critic', phase: 'Synthesize', schema: GAPS },
)
let finalPlan = merged
if (critic && critic.missing && critic.missing.length) {
  log('critic found ' + critic.missing.length + ' gaps; patching')
  finalPlan = await agent(
    CONTEXT + '\n\nRevise the plan to close every gap below. Return the complete revised plan in markdown (same sections).\n\nGAPS:\n' + JSON.stringify(critic.missing, null, 1) + '\n\nPLAN:\n' + merged,
    { label: 'patch', phase: 'Synthesize' },
  )
}

if (!finalPlan) {
  noteFailure('patch', 'writing the merged plan without the critic fixes')
  finalPlan = merged
}
const written = await agent(
  'Write these files exactly, creating folders as needed. Do not modify any other file.\n' +
  '1. ' + FINAL + ': the FINAL PLAN below, verbatim, with a first line "Status: draft for author review".\n' +
  '2. ' + OUT + '/findings.md: the verified findings grouped by lens, each with its evidence list.\n' +
  '3. ' + OUT + '/data-logic-map.md: from the "data" and "rules" findings, one section per question (Q1..Q8 and any proposed additions) with quoted passages, authority, deciding rule, expected outcome, owner; then the decision tables/state machines.\n' +
  '4. ' + OUT + '/answer-key-draft.md: proposed reference cases with expected values derived by source inspection, each with the passage quote it comes from, clearly marked DRAFT FOR HUMAN REVIEW. Do NOT write anything under reference/.\n' +
  '5. ' + OUT + '/plan-candidates.md: the three candidate plans and the judges\' scores.\n' +
  '6. For each key decision in the final plan, a proposed decision record docs/decisions/NNN-short-title.md using the template in docs/decisions/README.md, Status: proposed. These are PUBLIC files: restate context in full, never mention or link local-only files or the working brief.\n' +
  'Return the list of files written.\n\nFINAL PLAN:\n' + finalPlan + '\n\nVERIFIED FINDINGS:\n' + findingsJson + '\n\nCANDIDATES:\n' + candidatesJson + '\n\nJUDGMENTS:\n' + JSON.stringify(judgments, null, 1),
  { label: 'write-outputs', phase: 'Synthesize' },
)

return {
  findingsKept: lensResults.map(l => ({ lens: l.lens, kept: l.items.length, dropped: l.dropped || 0 })),
  candidates: candidates.map(c => c.angle),
  judges: judgments.map(j => ({ judge: j.judge, scores: j.scores.map(s => ({ angle: s.angle, score: s.score })) })),
  criticGaps: critic && critic.missing ? critic.missing.length : null,
  filesWritten: written,
  next: 'The author reviews ' + FINAL + ', ' + OUT + '/answer-key-draft.md and the proposed decisions before Phase 2.',
}
