<!-- Output of the separate AI agent that re-derived the key for X27-X35 blind and cross-checked X1-X26 against the
new passages (decision 042), saved unedited as evidence. -->

# Blind answer key 2: X27-X35, cross-check of X1-X26, scenario counts

Derived only from data/seed/domain.md, data/seed/seed.json (documents only), data/additions/extended.json (working-tree
version), data/changes/access-2fa-version-2.json, data/scenario/extended-demo.json and decisions 001, 002, 005, 006,
007, 008, 011, 013, 014, 016, 020. I read nothing under src/, runs/, tests/, reference/, docs/RESULTS.md or docs/research/.

## Authority (from supersedes edges only)

Replaced documents: EXPORT-v1 (by EXPORT-v2), EXPORT-LIMITS-v1, SUPPORT-STATUS-v1, ACCESS-SESSION-v1,
BILLING-REFUND-v1, BILLING-RETRY-v1 (by BILLING-RETRY-v2, although v2 has the OLDER date: 2026-06-01 vs 2026-09-01).
Every other document is authoritative. No status/supersedes mismatch exists: each replaced document is marked
"superseded" and every "current" document is unreplaced. EXPORT-DELIMITER-v2 has `supersedes: null`, so it does NOT
replace EXPORT-DELIMITER-v1 despite its "-v2" ID, version 2 and newer date.

## X27-X35

### X27 "Will items that were moved to the archive appear in the downloaded file?"
- Status: answered (documented negative, decision 005). Owner: Product reviewer (exports).
- Gold: EXPORT-ARCHIVE-v1:p1 ("Archived records are left out of every export."). Replaced shown: none.
- Must state: No; archived records are left out of (not included in) exports. Saying "any/every export" is fine
  because the passage says "every".
- Must NOT claim: that archived records can be included by a setting, restored or un-archived for export; anything
  about deleted records; anything about scheduled exports specifically beyond "every export"; that this is undocumented.
- Doubt: the question is paraphrased ("items moved to the archive" = archived records; "downloaded file" = export file;
  EXPORT-FILES-v1:p1 links export files and downloading). A too-literal system might call it undocumented; I judge the
  mapping direct enough to answer. Minor tension, not a conflict: EXPORT-SCHEDULE-v1:p1 says a scheduled export
  "contains the records changed in the previous 24 hours"; read with EXPORT-ARCHIVE it simply means archived ones are
  still excluded.

### X28 "Can a customer who deleted the payment confirmation email get it again?"
- Status: answered. Owner: Billing reviewer.
- Gold: BILLING-RECEIPTS-v1:p1 ("Receipts can be sent again from the Payments page.") required;
  BILLING-PAYMENT-v1:p1 ("A receipt is sent by email after each payment.") acceptable as supporting, since it is what
  identifies the payment confirmation email as the receipt. Replaced shown: none.
- Must state: Yes; the receipt can be sent again from the Payments page.
- Must NOT claim: who may resend it (e.g. "only account owners", "the customer themselves", "support"); that it can be
  downloaded; a time limit; that it is an invoice or that invoices can be downloaded instead (BILLING-v1:p1 is about
  invoices, not receipts, and its "Account owners can" must not be carried over); delivery to another address.
- Doubt: the passage does not say WHO can trigger the resend. The question asks whether the customer can "get it
  again", not whether they can resend it themselves, so I treat it as answered; a strict reviewer could call the
  "who" part undocumented (decision 007). I keep answered.

### X29 "If the product stops working on a Sunday, where can a customer see what is happening?"
- Status: answered. Owner: Support reviewer.
- Gold: SUPPORT-OUTAGE-v1:p1 ("During an outage, customers can follow progress on the status page at any time of
  day or week."). Replaced shown: none (if an answer also cites SUPPORT-STATUS-v2:p1, SUPPORT-STATUS-v1:p1 is shown as
  replaced; that citation is not needed).
- Must state: on the status page, which can be followed at any time, including weekends/Sundays.
- Must NOT claim: email support on Sunday (SUPPORT-v1:p1 limits email support to Monday-Friday), live chat (not
  offered), phone (not offered); that the status page is updated every 30 minutes (SUPPORT-STATUS-v2:p1 does not say
  where its updates are posted; linking them is an inference); the "every hour" figure from replaced SUPPORT-STATUS-v1;
  "only" the status page.
- Doubt: "product stops working" = "outage" is a paraphrase mapping; judged direct.

### X30 "How much does an additional seat cost?"
- Status: answered. Owner: Billing reviewer.
- Gold: BILLING-SEATS-v1:p1 ("Extra seats cost 8 USD per month each."). Replaced shown: none.
- Must state: 8 USD per month for each extra seat.
- Must NOT claim: whether the price includes or excludes sales tax (BILLING-TAX-v1 vs BILLING-PRICING-v1 conflict);
  an annual price or annual billing (annual billing is not offered); nonprofit discount applying to seats; any
  free-plan seat price.
- Doubt: a careful checker could ask whether the X24 tax conflict leaks into a price question. It does not: the
  question asks the listed cost, which is documented; tax treatment is a separate, unasked point. Answer must simply
  stay silent on tax.

### X31 "How many seats come with a paid plan?"
- Status: answered. Owner: Billing reviewer.
- Gold: BILLING-SEATS-v1:p1 ("Each paid plan includes five seats."). Replaced shown: none.
- Must state: five seats (included in each paid plan). Mentioning that extra seats can be bought (8 USD/month each)
  is allowed.
- Must NOT claim: "only five"/"at most five" as a hard cap; anything about free-plan seats; differences between paid
  plans.
- Doubt: none.

### X32 "Are export files encrypted?"
- Status: unresolved, reason conflict. Owner: Product reviewer.
- Gold (both shown): EXPORT-ENCRYPTION-v1:p1 ("Export files are encrypted at rest.") and EXPORT-GUIDE-v1:p1 ("Files
  produced by the export tool are stored without any encryption."). No supersedes link; EXPORT-GUIDE's newer date
  (2026-09-18) gives no authority. Replaced shown: none.
- No answer adopted. Must NOT claim yes or no, nor prefer the newer guide.
- Doubt: the conflicting sentence is buried in a longer how-to passage (the other sentences are distractors); a
  retriever or drafter that misses it would wrongly answer "Yes, at rest".

### X33 "Can a team member be limited to read-only access?"
- Status: unresolved, reason conflict. Owner: Product reviewer.
- Gold (both shown): ACCESS-READONLY-v1:p1 ("Team members can be given read-only access.") and ACCESS-OVERVIEW-v1:p1
  ("Everyone the owner adds to the team can edit every page; there is no way to restrict someone to viewing only.").
  No supersedes link; OVERVIEW's newer date gives nothing. Replaced shown: none.
- No answer adopted.
- Doubt: none on the status; the conflicting clause is again inside a longer passage.

### X34 "Which separator do CSV exports use?"
- Status: unresolved, reason conflict. Owner: Product reviewer.
- Gold (both shown): EXPORT-DELIMITER-v1:p1 (comma) and EXPORT-DELIMITER-v2:p1 (semicolon). Both are current;
  EXPORT-DELIMITER-v2 has `supersedes: null`, so its "-v2" ID, version 2 and newer date (2026-09-25) give no
  authority (decision 002). Replaced shown: none.
- Must NOT claim: semicolon (or comma) as the answer; that the separator is configurable; that v2 replaces v1.
- Doubt: none; this is the deliberate "version suffix without supersedes" trap.

### X35 "How many times is a failed payment retried?"
- Status: answered. Owner: Billing reviewer.
- Gold: BILLING-RETRY-v2:p1 ("Failed payments are retried 5 times over 10 days."). Replaced shown: BILLING-RETRY-v1:p1
  ("Failed payments are retried 3 times."). BILLING-RETRY-v2 wins although its date is OLDER, because it carries the
  supersedes edge (decision 002).
- Must state: 5 times (over 10 days; the "over 10 days" part is optional but welcome).
- Must NOT claim: 3 times; a conflict; a fixed interval such as "every 2 days" (not stated); what happens after the
  last retry (cancellation, loss of access, emails).
- Doubt: none; this is the deliberate "older-dated superseder" trap.

Summary X27-X35: answered 6 (X27, X28, X29, X30, X31, X35); unresolved/conflict 3 (X32, X33, X34);
unresolved/undocumented 0.

## Whole-corpus check: do the added passages change X1-X26?

My independent statuses for X1-X26 (needed for counts): answered 15 = X1, X2, X4, X7, X8, X10, X12, X13, X14, X16,
X17, X19, X20, X21, X23; unresolved 11 = X3, X6, X9, X15, X22, X25, X26 (undocumented) and X5, X11, X18, X24
(conflict).

Pairs checked, with verdict:

1. ACCESS-READONLY-v1:p1 / ACCESS-OVERVIEW-v1:p1 vs X15 ("Can account owners remove team members and change their
   roles?"). REAL RISK, status unchanged, reason may shift. Giving a team member read-only access is arguably a role
   change, and OVERVIEW says there is no way to restrict anyone to viewing only. A careful checker reading all current
   passages could report X15 as unresolved/conflict (READONLY vs OVERVIEW) instead of unresolved/undocumented. My
   call: keep "undocumented", because neither passage says account owners can (or cannot) change roles, and "read-only
   access can be given" is not "roles can be changed". But the key should either accept both reasons for X15 or note
   that these two passages are relevant distractors for it. Status (unresolved) and counts do not change.
2. BILLING-SEATS-v1:p1 "Account owners can move a seat from one team member to another" vs X15: not a role change;
   no effect, but a weak tempting distractor.
3. ACCESS-OVERVIEW-v1:p1 "Everyone the owner adds to the team can edit every page" vs X18 (guest users view shared
   reports): only matters if guests are team members, which no passage says. X18 stays conflict on ACCESS-GUEST-v1
   vs ACCESS-GUEST-NOTE-v1; no change.
4. SUPPORT-OUTAGE-v1:p1 vs X10 (status updates every 30 minutes): different facts (where vs how often); no conflict.
   vs SUPPORT-v1:p1 email hours and SUPPORT-CHANNELS-v1:p1: different channels; no conflict.
5. BILLING-RETRY-v2:p1 "over 10 days" vs X25 (how long refunds take to arrive): about retries, not refunds; X25 stays
   unresolved/undocumented. A sloppy drafter could misuse it.
6. BILLING-SEATS-v1:p1 "8 USD per month" vs X23 (annual billing not offered) and BILLING-v1:p1 (billed monthly in
   USD): consistent; no effect.
7. BILLING-RECEIPTS-v1:p1 vs X21/X22: says nothing about payment methods; X22 stays undocumented.
8. EXPORT-ARCHIVE-v1:p1 vs X1/X2 (scheduled exports): no change to when/where; minor tension only with "contains the
   records changed in the previous 24 hours" (see X27 doubt). No conflict for X1/X2.
9. EXPORT-ENCRYPTION / EXPORT-GUIDE / EXPORT-DELIMITER vs X4, X5, X6: no overlap. EXPORT-GUIDE "Large files can take
   a few minutes to appear" does not touch X4 row limits or X5 download period.
10. ACCESS-OVERVIEW-v1:p1 "Each workspace belongs to one account owner" vs X13/X14: no effect.

No added passage changes the status of any X1-X26 item. Only X15's reason is at risk (item 1).

Housekeeping found while reading (not answer-key content):
- extended-demo.json `_purpose` says items "R1/X1 ... R1/X26"; with X27-X35 added it should say R1/X35.
- extended.json `_purpose` cites "decisions 039 and 043"; docs/decisions/ currently ends at 042 (no 043 file yet).

## Scenario counts [answered, unresolved, approved, needs_review, error], 35 items per request

Per-request baseline (fresh drafts, all correct): answered 21 (15 + 6), unresolved 14 (11 + 3).

| Step | Action | R1 | R2 | R3 |
|---|---|---|---|---|
| S1 | run R1 | [21, 14, 0, 0, 0] | - | - |
| S2 | approve R1/X1, R1/X13; save_edit R1/X12; note R1/X5 | [19, 14, 2, 0, 0] | - | - |
| S3 | run R2 | [19, 14, 2, 0, 0] | [19, 14, 2, 0, 0] | - |
| S4 | ACCESS-2FA-v1 version 1 -> 2 | [19, 14, 1, 1, 0] | [19, 14, 1, 1, 0] | - |
| S5 | run R3 | [19, 14, 1, 1, 0] | [19, 14, 1, 1, 0] | [20, 14, 1, 0, 0] |

Reasoning:
- S2: X1 and X13 move answered -> approved. The X12 edit is an unapproved draft; the status rule (decision 020) takes
  the latest suggestion's status, so X12 stays answered. The X5 note is newer than the suggestion -> unresolved, which
  X5 already was.
- S3: R2/X1 and R2/X13 reuse the fresh approvals (exact text). R2/X12 is drafted afresh (edit never reused) ->
  answered; R2/X5 drafted afresh -> unresolved/conflict (the note is not carried).
- S4: the X13 approval cites ACCESS-2FA-v1:p1, whose version changed -> sticky stale mark; R1/X13 (approving item) and
  R2/X13 (served it) -> needs_review. X14 drafts also cite ACCESS-2FA-v1 but are not approved, so nothing changes.
  X1 is unaffected.
- S5: R3/X1 reused -> approved. R3/X13: stale approval not reused (shown beside it), fresh draft -> answered (Yes).
  Earlier requests never change.
- Every row sums to 35.
