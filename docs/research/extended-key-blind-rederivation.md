<!-- Output of the separate AI agent that re-derived the extended answer key blind (decision 042), saved unedited as
evidence. It was given only the files listed below and wrote this before seeing the main key or any app output. -->

# Blind answer key: extended questionnaire X1-X26

Sources used: data/seed/domain.md, data/seed/seed.json, data/additions/extended.json,
data/changes/access-2fa-version-2.json, data/scenario/extended-demo.json, and decisions 001, 002, 005, 006, 007, 008,
011, 013, 014, 016 and 020. Nothing under src/, runs/, tests/, docs/RESULTS.md or reference/ was opened.

Owners: exports and access go to the Product reviewer, support to the Support reviewer, billing to the Billing reviewer.

## Per-question key

| ID | Status / reason | Owner | Gold passages | Replaced text to show | Facts the answer must state | Claims it must NOT make |
|---|---|---|---|---|---|---|
| X1 | answered / null | Product | EXPORT-SCHEDULE-v1:p1 | none | Scheduled exports run once a day at 02:00 UTC. | Other run times, or "only"/"always" wording beyond the passage. |
| X2 | answered / null | Product | EXPORT-SCHEDULE-v1:p1 | none | Scheduled exports can be sent to an SFTP server. | "Only to SFTP"; that S3 or any other destination is, or is not, supported. |
| X3 | unresolved / undocumented | Product | [] | none | (none) | Yes; No (inferred from SFTP being the only destination mentioned). |
| X4 | answered / null | Product | EXPORT-LIMITS-v2:p1 | EXPORT-LIMITS-v1:p1 (10,000 rows) | Up to 50,000 rows. It may add that larger exports are split into several files. | 10,000 rows; that larger exports are refused or impossible. |
| X5 | unresolved / conflict | Product | EXPORT-FILES-v1:p1 (7 days), EXPORT-HELP-v1:p1 (30 days) | none | (none; both passages shown neutrally) | Adopting 7 or 30 days; treating the newer date (EXPORT-HELP, 2026-09-15) as authority. |
| X6 | unresolved / undocumented | Product | [] | none | (none) | Yes; No (e.g. "only CSV is offered", inferred from EXPORT-v2's CSV text). |
| X7 | answered / null | Support | SUPPORT-REPLY-v1:p1 | none | Paid-plan customers get a first reply to email support within one business day. | "Within 24 hours"; three business days (that is the free-plan figure). |
| X8 | answered / null | Support | SUPPORT-CHANNELS-v1:p1 | none | No, phone support is not offered. | Any claim that phone support exists. |
| X9 | unresolved / undocumented | Support | [] | none | (none) | "No, French is not answered" (closed-world reading of "English or German"); Yes. |
| X10 | answered / null | Support | SUPPORT-STATUS-v2:p1 | SUPPORT-STATUS-v1:p1 (every hour) | Every 30 minutes during an incident. | Every hour. |
| X11 | unresolved / conflict | Support | SUPPORT-HELPCENTRE-v1:p1 (English only), SUPPORT-FAQ-v1:p1 (English and Spanish) | none | (none) | Adopting either list; adding German (SUPPORT-CHANNELS is about support requests, not the help centre). |
| X12 | answered / null | Support | SUPPORT-TICKETS-v1:p1 | none | Tickets close automatically after 14 days without a customer reply. | "14 days after opening"; closing for any other reason. |
| X13 | answered / null | Product | ACCESS-2FA-v1:p1 | none | Yes, account owners can require 2FA for the whole team. | "Only owners can"; that 2FA is required by default. |
| X14 | answered / null | Product | ACCESS-2FA-v1:p1 | none | Each user can turn on 2FA for their own account, in their profile settings. | "Only account owners"; "only admins". |
| X15 | unresolved / undocumented (partial) | Product | ACCESS-ROLES-v1:p1 (covers the removal part) | none | Draft may say owners can remove members, who lose access immediately, but the item is not answered. | That owners can, or cannot, change roles. |
| X16 | answered / null | Product | ACCESS-SESSION-v2:p1 | ACCESS-SESSION-v1:p1 (12 hours) | Inactive sessions are signed out after 8 hours. | 12 hours. |
| X17 | answered / null | Product | ACCESS-PASSWORD-v1:p1 | none | No, passwords do not expire. | Anything about lockout or rotation. |
| X18 | unresolved / conflict | Product | ACCESS-GUEST-v1:p1 (can), ACCESS-GUEST-NOTE-v1:p1 (cannot) | none | (none) | Adopting either side; the newer date (2026-09-01) deciding it. |
| X19 | answered / null | Product | ACCESS-AUDIT-v1:p1 | none | Sign-in attempts are kept in the audit log for 90 days. | Any other retention period. |
| X20 | answered / null | Billing | BILLING-REFUND-v2:p1 | BILLING-REFUND-v1:p1 (14 days) | Refunds can be requested within 30 days of a payment. | 14 days. |
| X21 | answered / null | Billing | BILLING-PAYMENT-v1:p1 | none | Yes, payments can be made by credit card. | "Only credit card"; any other method being accepted or refused. |
| X22 | unresolved / undocumented | Billing | [] | none | (none) | Yes; No. "Can be made by credit card" is not "only". |
| X23 | answered / null | Billing | BILLING-TERMS-v1:p1 | none | No, annual billing is not offered. | That annual billing exists. It may add that subscriptions renew monthly. |
| X24 | unresolved / conflict | Billing | BILLING-TAX-v1:p1 (include), BILLING-PRICING-v1:p1 (do not include) | none | (none) | Adopting either side; the newer date (2026-09-10) deciding it. |
| X25 | unresolved / undocumented (partial) | Billing | BILLING-REFUND-v2:p1 (covers the original-method part) | BILLING-REFUND-v1:p1, if the draft cites v2 | Draft may say refunds go back to the original payment method, but the item is not answered. | Any arrival time. |
| X26 | unresolved / undocumented (partial) | Product | ACCESS-PASSWORD-v1:p1 (covers "do not expire") | none | Draft may say passwords do not expire, but the item is not answered. | Any lockout threshold. ACCESS-AUDIT (sign-in attempts kept 90 days) is not a lockout rule. |

**Totals:** 15 answered and 11 unresolved, out of 26.

- Answered: X1, X2, X4, X7, X8, X10, X12, X13, X14, X16, X17, X19, X20, X21, X23.
- Unresolved for a conflict (4): X5, X11, X18, X24.
- Unresolved as undocumented (7): X3, X6, X9, X15, X22, X25, X26.
- Answered items that show replaced text: X4, X10, X16, X20 (X25 too, if its draft cites v2).

## Doubts and data checks

1. **X9 could be argued as answered "No".** Someone could read "English or German are answered" as the full list.
   There is no "only", so under decisions 005 and 006 French is unknown. This is the most arguable item in the set.
2. **X2 depends on one reading.** "Where can ... be sent?" could be read as asking for every destination, which would
   make it partial. I followed decision 006's treatment of seed Q6 and Q8: a "can" fact answers a "who/where can"
   question as long as the answer does not say "only".
3. **X14 may raise a warning.** "Each user" may be rephrased as "every user". "every" is on the strengthening-word
   list, so the hint would fire. Under decision 006 that is a warning only, not a failure.
4. **X25 replaced text is unclear.** The rule shows replaced text "when the current replacement is cited". It does not
   say whether that covers a partial, unresolved draft. Pick one reading for X25 and write it down.
5. **X15 has a naming trap.** The document is called ACCESS-ROLES but says nothing about changing roles. This is
   intended, not a data error.
6. **The data files have no errors.**
   - All four supersedes pairs are correct: the old document is marked superseded and the new one is current.
   - All four conflict pairs are current, and none of them is linked by a supersedes edge.
   - In every conflict pair the newer-dated document is the second one, so logic that lets the newest date win would
     wrongly answer X5, X11, X18 and X24.
   - IDs are unique.
   - The change file keeps the ID "ACCESS-2FA-v1" at version 2. That is confusing but correct, since ID suffixes grant
     nothing; its text, date, status and supersedes match the original.
7. **No added passage conflicts with a seed passage.** Some overlap is consistent:
   - SUPPORT-CHANNELS ("not offered") agrees with SUPPORT-v1's "Live chat is not offered".
   - BILLING-TERMS ("renew each month") agrees with BILLING-v1's "monthly".
8. **The seed key would change on this corpus.** Decision 006 forbids seed Q7 from claiming "annual billing is not
   available". On this corpus BILLING-TERMS-v1:p1 documents exactly that. If Q1-Q8 are ever graded against the
   extended corpus, that forbidden claim must be relaxed. Nothing else in the seed key changes: Q2 JSON is still
   undocumented and Q5 still has no sign-in methods beyond email and password.
9. **R1/X12 status after the edit is my assumption.** Decision 020's status order looks at "the latest suggestion",
   and an edit is a draft rather than an approval. So I keep R1/X12 as answered. If the implementation lets an edit
   replace the suggestion's status, it is still answered because the edit is supported.
10. **The scripted approvals are supported.** The X1 and X13 approval texts are backed by their cited passages, so the
    approval guard should not need an override note.

## Scenario counts [answered, unresolved, approved, needs_review, error]

| Step | R1 | R2 | R3 |
|---|---|---|---|
| S1 (run R1) | [15, 11, 0, 0, 0] | n/a | n/a |
| S2 (approve X1 and X13, edit X12, note on X5) | [13, 11, 2, 0, 0] | n/a | n/a |
| S3 (run R2) | [13, 11, 2, 0, 0] | [13, 11, 2, 0, 0] | n/a |
| S4 (ACCESS-2FA-v1 goes from version 1 to 2) | [13, 11, 1, 1, 0] | [13, 11, 1, 1, 0] | n/a |
| S5 (run R3) | [13, 11, 1, 1, 0] | [13, 11, 1, 1, 0] | [14, 11, 1, 0, 0] |

Every row sums to 26.

## What each step should show

**X1**

- S1: R1/X1 is answered, a model draft citing EXPORT-SCHEDULE-v1:p1.
- S2: R1/X1 is approved with the reviewer's text, approver Product reviewer.
- S3: R2/X1 is approved and reused. No model call; the approval and its source are shown.
- S4: no change. EXPORT-SCHEDULE-v1 did not change.
- S5: R3/X1 is approved and reused, with no model call. R1/X1 and R2/X1 stay approved.

**X12**

- S1: R1/X12 is answered (model draft).
- S2: R1/X12 stays answered. The saved edit is shown as a draft, not approved.
- S3: R2/X12 gets a fresh model draft (a model call is made) and is answered. The edit is not reused or shown as
  approved.
- S4: no change.
- S5: R3/X12 gets a fresh draft, answered, same as S3.

**X13**

- S1: R1/X13 is answered.
- S2: R1/X13 is approved.
- S3: R2/X13 is approved and reused, with no model call.
- S4: the X13 approval gets a sticky stale mark (ACCESS-2FA-v1 version 1 to 2). R1/X13 and R2/X13 both become
  needs_review with that reason.
- S5: R3/X13 is not reused. It gets a fresh model draft (a model call is made) that is answered and cites
  ACCESS-2FA-v1:p1 at version 2. The stale approval is shown beside it, labelled "approved earlier - source changed -
  not reused". R1/X13 and R2/X13 stay needs_review.
- X14 also cites ACCESS-2FA-v1 but has no approval, so the change does not affect it.

**R1/X5**

- S1: unresolved, reason conflict, owner Product reviewer. Both EXPORT-FILES-v1:p1 and EXPORT-HELP-v1:p1 are shown,
  and no answer is adopted.
- S2: the note is attached and the item stays unresolved with reason conflict. It cannot be approved.
- S3 to S5: unchanged. R2/X5 and R3/X5 are separate unresolved conflict items without the R1 note.
