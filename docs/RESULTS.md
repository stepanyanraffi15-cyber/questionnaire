# Check results

Written by `reference/grade.py` from `runs/report/observed.json` (seed scenario) and
`runs/report/observed-extended.json` (extended scenario). Do not edit by hand.

- Seed: mode replay · model gemini-3.8-flash · embeddings gemini-embedding-001
- Extended: mode replay · model gemini-3.8-flash · embeddings gemini-embedding-001
- Answer key sha256: b899a463d6a13a0d
- Mechanical rows are graded by code. Meaning rows use a recorded Gemini judge (same model family
  as the application, a stated limitation) plus the author's sign-off. Only a sign-off makes a
  meaning row PASS; unsigned, a judge PASS is PENDING and a judge FAIL is FAIL.

## Minimum demonstration

| Check | Case | Result |
|---|---|---|
| MIN-1 | RC-1: A supported question gets a draft whose cited passages exist and support it (Q3) | PASS |
| MIN-2 | RC-2: The unsupported question stays unresolved with a review route and no invented capability (Q2) | PASS |
| MIN-3 | RC-3: The outdated policy's conflict is visible and the answer uses the document that supersedes it (Q1) | PASS |
| MIN-4 | RC-4: An approved correction is reused when Q1 is asked again; an unapproved edit is not | PASS |
| MIN-5 | RC-5: Reloading keeps approval and evidence; a source version change makes the approved answer need review | PASS |
| REQ-A3 | answered / unresolved / approved counts at every step | PASS |

## Extended questionnaire (added data, X1-X26)

| Kind | Case | Result |
|---|---|---|
| supported, multi-sentence passage | EXT-X1: The run time is the first of three sentences (X1) | PENDING |
| can vs only (supported) | EXT-X2: "can be sent to an SFTP server" is a permission, not the only destination (X2) | PENDING |
| can vs only (undocumented) | EXT-X3: SFTP is documented; Amazon S3 is not, so the answer is unknown, not No (X3) | PASS |
| conflict settled by supersedes | EXT-X4: EXPORT-LIMITS-v2 supersedes v1: 50,000 rows, with the old 10,000 shown as replaced (X4) | FAIL |
| conflict not settled by supersedes | EXT-X5: 7 days vs 30 days; EXPORT-HELP-v1 is newer but supersedes nothing (X5) | PASS |
| undocumented | EXT-X6: No passage mentions XLSX (X6) | PASS |
| supported, distractor in the same passage | EXT-X7: Paid plans: one business day (the free-plan sentence must not be used) (X7) | PENDING |
| documented No, multi-sentence passage | EXT-X8: "Phone support is not offered" is the second of three sentences (X8) | PENDING |
| can vs only (undocumented) | EXT-X9: English and German requests are answered; French is not mentioned (X9) | PASS |
| conflict settled by supersedes | EXT-X10: SUPPORT-STATUS-v2 supersedes v1: every 30 minutes, with every hour shown as replaced (X10) | PENDING |
| conflict not settled by supersedes | EXT-X11: English only vs English and Spanish; SUPPORT-FAQ-v1 is newer but supersedes nothing (X11) | PASS |
| supported | EXT-X12: Tickets close after 14 days without a customer reply (X12) | PENDING |
| supported, multi-sentence passage | EXT-X13: Yes: account owners can require 2FA for the whole team (X13) | PENDING |
| can vs only (supported) | EXT-X14: Each user can turn 2FA on; the answer must not limit it to account owners (X14) | PENDING |
| partial answer | EXT-X15: Removing team members is documented; changing roles is not (X15) | PASS |
| conflict settled by supersedes | EXT-X16: ACCESS-SESSION-v2 supersedes v1: 8 hours, with 12 hours shown as replaced (X16) | PENDING |
| documented No, multi-sentence passage | EXT-X17: "Passwords do not expire" is the second sentence (X17) | PENDING |
| conflict not settled by supersedes | EXT-X18: can vs cannot; ACCESS-GUEST-NOTE-v1 is newer but supersedes nothing (X18) | PASS |
| supported, on-topic distractors | EXT-X19: 90 days (EXPORT-AUDIT-v1 also mentions the audit log but does not answer) (X19) | PENDING |
| conflict settled by supersedes | EXT-X20: BILLING-REFUND-v2 supersedes v1: 30 days, with 14 days shown as replaced (X20) | PENDING |
| supported | EXT-X21: Yes: payments can be made by credit card (X21) | PENDING |
| can vs only (undocumented) | EXT-X22: "can be made by credit card" does not say only (X22) | PASS |
| documented No, multi-sentence passage | EXT-X23: "Annual billing is not offered" (X23) | PENDING |
| conflict not settled by supersedes | EXT-X24: include vs do not include sales tax; BILLING-PRICING-v1 is newer but supersedes nothing (X24) | PASS |
| partial answer | EXT-X25: The refund method is documented; how long refunds take is not (X25) | PASS |
| partial answer | EXT-X26: Password expiry is documented (No); the lockout threshold is not (X26) | PASS |
| approved reuse | EXT-REUSE: Approved X1 and X13 are reused in R2 with no model call; the unapproved X12 edit is not | PASS |
| changed source version | EXT-CHANGE: ACCESS-2FA-v1 goes to version 2: the X13 approval needs review; R3/X13 gets a fresh draft | PASS |
| unresolved with a note | EXT-NOTE: The X5 conflict is left unresolved with a note for the Product reviewer | PASS |
| counts | counts at every step | PASS |

## Retrieval recall@k

Measured, not graded: recall@k is the share of a row's gold passages in the first retrieval for the
question; "shown" adds the passages the model's own searches found. n/a: no gold passage (an
undocumented question) or no draft at that item.

| Scenario | Case | Item | Gold | recall@k | shown | Missed | Row result |
|---|---|---|---|---|---|---|---|
| seed | RC-1 | S1 R1/Q3 | SUPPORT-v1:p1 | 1.00 | 1.00 |  | PASS |
| seed | RC-2 | S1 R1/Q2 | - | n/a | n/a |  | PASS |
| seed | RC-3 | S1 R1/Q1 | EXPORT-v2:p1 | 1.00 | 1.00 |  | PASS |
| seed | XR-Q4 | S1 R1/Q4 | SUPPORT-v1:p1 | 1.00 | 1.00 |  | PASS |
| seed | XR-Q5 | S1 R1/Q5 | ACCESS-v1:p1 | 1.00 | 1.00 |  | PASS |
| seed | XR-Q6 | S1 R1/Q6 | ACCESS-v1:p1 | 1.00 | 1.00 |  | PASS |
| seed | XR-Q7 | S1 R1/Q7 | BILLING-v1:p1 | 1.00 | 1.00 |  | PASS |
| seed | XR-Q8 | S1 R1/Q8 | BILLING-v1:p1 | 1.00 | 1.00 |  | PASS |
| extended | EXT-X1 | S1 R1/X1 | EXPORT-SCHEDULE-v1:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X2 | S1 R1/X2 | EXPORT-SCHEDULE-v1:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X3 | S1 R1/X3 | - | n/a | n/a |  | PASS |
| extended | EXT-X4 | S1 R1/X4 | EXPORT-LIMITS-v2:p1 | 1.00 | 1.00 |  | FAIL |
| extended | EXT-X5 | S1 R1/X5 | EXPORT-FILES-v1:p1, EXPORT-HELP-v1:p1 | 1.00 | 1.00 |  | PASS |
| extended | EXT-X6 | S1 R1/X6 | - | n/a | n/a |  | PASS |
| extended | EXT-X7 | S1 R1/X7 | SUPPORT-REPLY-v1:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X8 | S1 R1/X8 | SUPPORT-CHANNELS-v1:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X9 | S1 R1/X9 | - | n/a | n/a |  | PASS |
| extended | EXT-X10 | S1 R1/X10 | SUPPORT-STATUS-v2:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X11 | S1 R1/X11 | SUPPORT-FAQ-v1:p1, SUPPORT-HELPCENTRE-v1:p1 | 1.00 | 1.00 |  | PASS |
| extended | EXT-X12 | S1 R1/X12 | SUPPORT-TICKETS-v1:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X13 | S1 R1/X13 | ACCESS-2FA-v1:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X14 | S1 R1/X14 | ACCESS-2FA-v1:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X15 | S1 R1/X15 | ACCESS-ROLES-v1:p1 | 1.00 | 1.00 |  | PASS |
| extended | EXT-X16 | S1 R1/X16 | ACCESS-SESSION-v2:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X17 | S1 R1/X17 | ACCESS-PASSWORD-v1:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X18 | S1 R1/X18 | ACCESS-GUEST-NOTE-v1:p1, ACCESS-GUEST-v1:p1 | 1.00 | 1.00 |  | PASS |
| extended | EXT-X19 | S1 R1/X19 | ACCESS-AUDIT-v1:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X20 | S1 R1/X20 | BILLING-REFUND-v2:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X21 | S1 R1/X21 | BILLING-PAYMENT-v1:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X22 | S1 R1/X22 | - | n/a | n/a |  | PASS |
| extended | EXT-X23 | S1 R1/X23 | BILLING-TERMS-v1:p1 | 1.00 | 1.00 |  | PENDING |
| extended | EXT-X24 | S1 R1/X24 | BILLING-PRICING-v1:p1, BILLING-TAX-v1:p1 | 1.00 | 1.00 |  | PASS |
| extended | EXT-X25 | S1 R1/X25 | BILLING-REFUND-v2:p1 | 1.00 | 1.00 |  | PASS |
| extended | EXT-X26 | S1 R1/X26 | ACCESS-PASSWORD-v1:p1 | 1.00 | 1.00 |  | PASS |
| **mean** | 29 rows with gold | | | 1.00 | 1.00 | | |

## Every check

| Scenario | Case | Kind | Where | Expected | Observed | Result | Sign-off |
|---|---|---|---|---|---|---|---|
| seed | RC-1 | mechanical | S1 R1/Q3 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | RC-1 | mechanical | S1 R1/Q3 citations | {"ids_subset_of": ["SUPPORT-v1:p1"], "non_empty": true} | [{"passage_id": "SUPPORT-v1:p1", "doc_id": "SUPPORT-v1", "version": 1, "excerpt": "Email support is available Monday to Friday, 09:00 to 17:00 UTC."}] | PASS |  |
| seed | RC-1 | mechanical | S1 R1/Q3 citations | {"excerpts_verbatim": true} | [{"passage_id": "SUPPORT-v1:p1", "doc_id": "SUPPORT-v1", "version": 1, "excerpt": "Email support is available Monday to Friday, 09:00 to 17:00 UTC."}] | PASS |  |
| seed | RC-1 | mechanical | S1 R1/Q3 owner | {"equals": "Support reviewer"} | "Support reviewer" | PASS |  |
| seed | RC-1 | mechanical | S1 R1/Q3 reason | {"not_equals": "conflict"} | null | PASS |  |
| seed | RC-1 | meaning | S1 R1/Q3 answer | {"expected_facts": ["Email support is available Monday to Friday (all five weekdays, not only some of them).", "Support hours are 09:00 to 17:00 (9 am to 5 pm is the same).", "The times are in UTC."], "forbidden_claims": ["Email support is available at weekends.", "The hours are in a time zone other than UTC.", "Live chat is available or offered."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Claude Code, delegated by the author on 2026-10-08 |
| seed | RC-2 | mechanical | S1 R1/Q2 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| seed | RC-2 | mechanical | S1 R1/Q2 reason | {"equals": "undocumented"} | "undocumented" | PASS |  |
| seed | RC-2 | mechanical | S1 R1/Q2 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| seed | RC-2 | mechanical | S1 R1/Q2 answer | {"equals": ""} | "" | PASS |  |
| seed | RC-2 | mechanical | S1 R1/Q2 citations | {"equals": []} | [] | PASS |  |
| seed | RC-2 | mechanical | S2 R1/Q2 note | {"equals_text": "N"} | "Needs Product reviewer: JSON export is not documented." | PASS |  |
| seed | RC-2 | mechanical | S2 R1/Q2 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| seed | RC-2 | meaning | S1 R1/Q2 suggestion.answer | {"expected_facts": [], "forbidden_claims": ["JSON export is available.", "JSON export is not available or not supported.", "The CSV paid-plan rule also covers JSON export."]} | empty text states nothing, so no forbidden claim is made | PASS | not needed |
| seed | RC-3 | mechanical | S1 R1/Q1 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | RC-3 | mechanical | S1 R1/Q1 citations | {"ids_subset_of": ["EXPORT-v2:p1"], "non_empty": true} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 2, "excerpt": "CSV exports are available on paid plans only."}] | PASS |  |
| seed | RC-3 | mechanical | S1 R1/Q1 citations | {"excerpts_verbatim": true} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 2, "excerpt": "CSV exports are available on paid plans only."}] | PASS |  |
| seed | RC-3 | mechanical | S1 R1/Q1 replaced_shown | {"ids_include": ["EXPORT-v1:p1"]} | ["EXPORT-v1:p1"] | PASS |  |
| seed | RC-3 | mechanical | S1 R1/Q1 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| seed | RC-3 | mechanical | S1 R1/Q1 reason | {"not_equals": "conflict"} | null | PASS |  |
| seed | RC-3 | meaning | S1 R1/Q1 answer | {"expected_facts": ["The answer is no: free-plan users cannot export CSV.", "CSV export is for paid plans only."], "forbidden_claims": ["Free-plan users can export CSV.", "CSV export is available on every plan as the current policy (mentioning the old, replaced policy as replaced is fine)."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Claude Code, delegated by the author on 2026-10-08 |
| seed | RC-4 | mechanical | S3 R2/Q1 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | RC-4 | mechanical | S3 R2/Q1 reused | {"equals": false} | false | PASS |  |
| seed | RC-4 | mechanical | S3 R2/Q1 answer | {"not_equals_text": "W"} | "No. CSV exports are available on paid plans only." | PASS |  |
| seed | RC-4 | mechanical | S3 R2/Q1 calls | {"non_empty": true} | [{"call_type": "draft", "label": "REPLAYED", "fingerprint": "dfd9a8e5eb3be41226a95bbd602bee11c372d39fd917030dd206fbfc47fd043c", "model": "gemini-3.8-flash", "re | PASS |  |
| seed | RC-4 | mechanical | S3 R2/Q3 answer | {"not_equals_text": "E3"} | "Email support is available Monday to Friday, 09:00 to 17:00 UTC." | PASS |  |
| seed | RC-4 | mechanical | S4 R1/Q1 status | {"equals": "approved"} | "approved" | PASS |  |
| seed | RC-4 | mechanical | S4 R1/Q1 approval.text | {"equals_text": "W"} | "No. CSV export is for paid plans only; free-plan users cannot export CSV." | PASS |  |
| seed | RC-4 | mechanical | S4 R1/Q1 approval.approver | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| seed | RC-4 | mechanical | S4 R1/Q1 approval.at | {"equals": "2026-10-08T09:03:00Z"} | "2026-10-08T09:03:00Z" | PASS |  |
| seed | RC-4 | mechanical | S4 R1/Q1 approval.sources | {"versions": {"EXPORT-v2:p1": 2}} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 2, "excerpt": "CSV exports are available on paid plans only."}] | PASS |  |
| seed | RC-4 | mechanical | S4 R2/Q1 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | RC-4 | mechanical | S5 R3/Q1 status | {"equals": "approved"} | "approved" | PASS |  |
| seed | RC-4 | mechanical | S5 R3/Q1 reused | {"equals": true} | true | PASS |  |
| seed | RC-4 | mechanical | S5 R3/Q1 answer | {"equals_text": "W"} | "No. CSV export is for paid plans only; free-plan users cannot export CSV." | PASS |  |
| seed | RC-4 | mechanical | S5 R3/Q1 approval.item | {"equals": "R1/Q1"} | "R1/Q1" | PASS |  |
| seed | RC-4 | mechanical | S5 R3/Q1 approval.approver | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| seed | RC-4 | mechanical | S5 R3/Q1 approval.sources | {"versions": {"EXPORT-v2:p1": 2}} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 2, "excerpt": "CSV exports are available on paid plans only."}] | PASS |  |
| seed | RC-4 | mechanical | S5 R3/Q1 replaced_shown | {"ids_include": ["EXPORT-v1:p1"]} | ["EXPORT-v1:p1"] | PASS |  |
| seed | RC-4 | mechanical | S5 R3/Q1 calls | {"equals": []} | [] | PASS |  |
| seed | RC-4 | mechanical | S5 R3/Q3 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | RC-4 | mechanical | S5 R3/Q3 answer | {"not_equals_text": "E3"} | "Email support is available Monday to Friday, 09:00 to 17:00 UTC." | PASS |  |
| seed | RC-4 | mechanical | S5 R1/Q3 edited | {"equals": true} | true | PASS |  |
| seed | RC-4 | mechanical | S5 R1/Q3 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | RC-5 | mechanical | S6 | {"same_as": "S5"} | items and counts equal S5 | PASS |  |
| seed | RC-5 | mechanical | S7 R1/Q1 status | {"equals": "needs_review"} | "needs_review" | PASS |  |
| seed | RC-5 | mechanical | S7 R1/Q1 approval.stale_reasons | {"equals": [{"doc_id": "EXPORT-v2", "approved_version": 2, "current_version": 3, "change": "version"}]} | [{"doc_id": "EXPORT-v2", "approved_version": 2, "current_version": 3, "change": "version"}] | PASS |  |
| seed | RC-5 | mechanical | S7 R3/Q1 status | {"equals": "needs_review"} | "needs_review" | PASS |  |
| seed | RC-5 | mechanical | S7 R3/Q1 approval.stale_reasons | {"equals": [{"doc_id": "EXPORT-v2", "approved_version": 2, "current_version": 3, "change": "version"}]} | [{"doc_id": "EXPORT-v2", "approved_version": 2, "current_version": 3, "change": "version"}] | PASS |  |
| seed | RC-5 | mechanical | S7 R2/Q1 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | RC-5 | mechanical | S8 R4/Q1 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | RC-5 | mechanical | S8 R4/Q1 reused | {"equals": false} | false | PASS |  |
| seed | RC-5 | mechanical | S8 R4/Q1 stale_approval_shown | {"not_equals": null} | "A1" | PASS |  |
| seed | RC-5 | mechanical | S8 R4/Q1 calls | {"non_empty": true} | [{"call_type": "draft", "label": "REPLAYED", "fingerprint": "dfd9a8e5eb3be41226a95bbd602bee11c372d39fd917030dd206fbfc47fd043c", "model": "gemini-3.8-flash", "re | PASS |  |
| seed | RC-5 | mechanical | S9 | {"same_as": "S8"} | items and counts equal S8 | PASS |  |
| seed | XR-1 | mechanical | S10 R1/Q1 status | {"equals": "approved"} | "approved" | PASS |  |
| seed | XR-1 | mechanical | S10 R1/Q1 approval.sources | {"versions": {"EXPORT-v2:p1": 3}} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 3, "excerpt": "CSV exports are available on paid plans only."}] | PASS |  |
| seed | XR-1 | mechanical | S10 R3/Q1 status | {"equals": "needs_review"} | "needs_review" | PASS |  |
| seed | XR-1 | mechanical | S11 R5/Q1 status | {"equals": "approved"} | "approved" | PASS |  |
| seed | XR-1 | mechanical | S11 R5/Q1 reused | {"equals": true} | true | PASS |  |
| seed | XR-1 | mechanical | S11 R5/Q1 answer | {"equals_text": "W"} | "No. CSV export is for paid plans only; free-plan users cannot export CSV." | PASS |  |
| seed | XR-1 | mechanical | S11 R5/Q1 approval.sources | {"versions": {"EXPORT-v2:p1": 3}} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 3, "excerpt": "CSV exports are available on paid plans only."}] | PASS |  |
| seed | XR-1 | mechanical | S11 R5/Q1 calls | {"equals": []} | [] | PASS |  |
| seed | XR-Q4 | mechanical | S1 R1/Q4 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | XR-Q4 | mechanical | S1 R1/Q4 citations | {"ids_subset_of": ["SUPPORT-v1:p1"], "non_empty": true} | [{"passage_id": "SUPPORT-v1:p1", "doc_id": "SUPPORT-v1", "version": 1, "excerpt": "Live chat is not offered."}] | PASS |  |
| seed | XR-Q4 | mechanical | S1 R1/Q4 owner | {"equals": "Support reviewer"} | "Support reviewer" | PASS |  |
| seed | XR-Q4 | meaning | S1 R1/Q4 answer | {"expected_facts": ["No: live chat is not offered."], "forbidden_claims": ["Live chat is offered.", "Another support channel, such as phone support, is offered."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Claude Code, delegated by the author on 2026-10-08 |
| seed | XR-Q5 | mechanical | S1 R1/Q5 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | XR-Q5 | mechanical | S1 R1/Q5 citations | {"ids_subset_of": ["ACCESS-v1:p1"], "non_empty": true} | [{"passage_id": "ACCESS-v1:p1", "doc_id": "ACCESS-v1", "version": 1, "excerpt": "Users can sign in with email and password."}] | PASS |  |
| seed | XR-Q5 | mechanical | S1 R1/Q5 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| seed | XR-Q5 | meaning | S1 R1/Q5 answer | {"expected_facts": ["Users sign in with email and password."], "forbidden_claims": ["Email and password is the only sign-in method.", "Single sign-on (SSO) or another sign-in method is available, or is not available."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Claude Code, delegated by the author on 2026-10-08 |
| seed | XR-Q6 | mechanical | S1 R1/Q6 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | XR-Q6 | mechanical | S1 R1/Q6 citations | {"ids_subset_of": ["ACCESS-v1:p1"], "non_empty": true} | [{"passage_id": "ACCESS-v1:p1", "doc_id": "ACCESS-v1", "version": 1, "excerpt": "Account owners can invite team members."}] | PASS |  |
| seed | XR-Q6 | mechanical | S1 R1/Q6 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| seed | XR-Q6 | meaning | S1 R1/Q6 answer | {"expected_facts": ["Account owners can invite team members (the bare answer \"Account owners.\" is acceptable)."], "forbidden_claims": ["Only account owners can invite team members.", "Any claim about whether other roles can invite team members."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Claude Code, delegated by the author on 2026-10-08 |
| seed | XR-Q7 | mechanical | S1 R1/Q7 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | XR-Q7 | mechanical | S1 R1/Q7 citations | {"ids_subset_of": ["BILLING-v1:p1"], "non_empty": true} | [{"passage_id": "BILLING-v1:p1", "doc_id": "BILLING-v1", "version": 1, "excerpt": "Paid subscriptions are billed monthly in USD."}] | PASS |  |
| seed | XR-Q7 | mechanical | S1 R1/Q7 owner | {"equals": "Billing reviewer"} | "Billing reviewer" | PASS |  |
| seed | XR-Q7 | meaning | S1 R1/Q7 answer | {"expected_facts": ["Subscriptions are billed monthly (saying \"paid subscriptions\" or mentioning USD is fine, and leaving them out is fine)."], "forbidden_claims": ["Subscriptions are billed at another frequency, such as yearly.", "No other billing frequency exists."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Claude Code, delegated by the author on 2026-10-08 |
| seed | XR-Q8 | mechanical | S1 R1/Q8 status | {"equals": "answered"} | "answered" | PASS |  |
| seed | XR-Q8 | mechanical | S1 R1/Q8 citations | {"ids_subset_of": ["BILLING-v1:p1"], "non_empty": true} | [{"passage_id": "BILLING-v1:p1", "doc_id": "BILLING-v1", "version": 1, "excerpt": "Account owners can download billing invoices."}] | PASS |  |
| seed | XR-Q8 | mechanical | S1 R1/Q8 owner | {"equals": "Billing reviewer"} | "Billing reviewer" | PASS |  |
| seed | XR-Q8 | meaning | S1 R1/Q8 answer | {"expected_facts": ["Account owners can download billing invoices (the bare answer \"Account owners.\" is acceptable)."], "forbidden_claims": ["Only account owners can download billing invoices.", "Any claim about whether other roles can download invoices."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Claude Code, delegated by the author on 2026-10-08 |
| seed | counts | mechanical | S1 R1 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S2 R1 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S3 R1 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S3 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S4 R1 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| seed | counts | mechanical | S4 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S5 R1 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| seed | counts | mechanical | S5 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S5 R3 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| seed | counts | mechanical | S6 R1 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| seed | counts | mechanical | S6 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S6 R3 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| seed | counts | mechanical | S7 R1 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| seed | counts | mechanical | S7 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S7 R3 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| seed | counts | mechanical | S8 R1 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| seed | counts | mechanical | S8 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S8 R3 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| seed | counts | mechanical | S8 R4 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S9 R1 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| seed | counts | mechanical | S9 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S9 R3 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| seed | counts | mechanical | S9 R4 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S10 R1 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| seed | counts | mechanical | S10 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S10 R3 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| seed | counts | mechanical | S10 R4 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S11 R1 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| seed | counts | mechanical | S11 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S11 R3 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| seed | counts | mechanical | S11 R4 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| seed | counts | mechanical | S11 R5 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| extended | EXT-X1 | mechanical | S1 R1/X1 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X1 | mechanical | S1 R1/X1 citations | {"ids_subset_of": ["EXPORT-SCHEDULE-v1:p1"], "non_empty": true} | [{"passage_id": "EXPORT-SCHEDULE-v1:p1", "doc_id": "EXPORT-SCHEDULE-v1", "version": 1, "excerpt": "Scheduled exports run once a day at 02:00 UTC."}] | PASS |  |
| extended | EXT-X1 | mechanical | S1 R1/X1 citations | {"excerpts_verbatim": true} | [{"passage_id": "EXPORT-SCHEDULE-v1:p1", "doc_id": "EXPORT-SCHEDULE-v1", "version": 1, "excerpt": "Scheduled exports run once a day at 02:00 UTC."}] | PASS |  |
| extended | EXT-X1 | mechanical | S1 R1/X1 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X1 | meaning | S1 R1/X1 answer | {"expected_facts": ["Scheduled exports run once a day.", "They run at 02:00 UTC."], "forbidden_claims": ["Scheduled exports run more than once a day.", "They run at a time other than 02:00 UTC."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X2 | mechanical | S1 R1/X2 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X2 | mechanical | S1 R1/X2 citations | {"ids_subset_of": ["EXPORT-SCHEDULE-v1:p1"], "non_empty": true} | [{"passage_id": "EXPORT-SCHEDULE-v1:p1", "doc_id": "EXPORT-SCHEDULE-v1", "version": 1, "excerpt": "Scheduled exports can be sent to an SFTP server."}] | PASS |  |
| extended | EXT-X2 | mechanical | S1 R1/X2 citations | {"excerpts_verbatim": true} | [{"passage_id": "EXPORT-SCHEDULE-v1:p1", "doc_id": "EXPORT-SCHEDULE-v1", "version": 1, "excerpt": "Scheduled exports can be sent to an SFTP server."}] | PASS |  |
| extended | EXT-X2 | mechanical | S1 R1/X2 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X2 | meaning | S1 R1/X2 answer | {"expected_facts": ["Scheduled exports can be sent to an SFTP server."], "forbidden_claims": ["An SFTP server is the only destination for scheduled exports.", "Scheduled exports cannot be sent anywhere other than an SFTP server.", "Scheduled exports can be sent by email or to cloud storage."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X3 | mechanical | S1 R1/X3 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | EXT-X3 | mechanical | S1 R1/X3 reason | {"equals": "undocumented"} | "undocumented" | PASS |  |
| extended | EXT-X3 | mechanical | S1 R1/X3 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X3 | mechanical | S1 R1/X3 answer | {"equals": ""} | "" | PASS |  |
| extended | EXT-X4 | mechanical | S1 R1/X4 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X4 | mechanical | S1 R1/X4 citations | {"ids_subset_of": ["EXPORT-LIMITS-v2:p1"], "non_empty": true} | [{"passage_id": "EXPORT-LIMITS-v2:p1", "doc_id": "EXPORT-LIMITS-v2", "version": 2, "excerpt": "A single CSV export can contain up to 50,000 rows."}, {"passage_i | FAIL |  |
| extended | EXT-X4 | mechanical | S1 R1/X4 citations | {"excerpts_verbatim": true} | [{"passage_id": "EXPORT-LIMITS-v2:p1", "doc_id": "EXPORT-LIMITS-v2", "version": 2, "excerpt": "A single CSV export can contain up to 50,000 rows."}, {"passage_i | PASS |  |
| extended | EXT-X4 | mechanical | S1 R1/X4 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X4 | mechanical | S1 R1/X4 replaced_shown | {"ids_include": ["EXPORT-LIMITS-v1:p1"]} | ["EXPORT-LIMITS-v1:p1", "EXPORT-v1:p1"] | PASS |  |
| extended | EXT-X4 | meaning | S1 R1/X4 answer | {"expected_facts": ["A single CSV export can contain up to 50,000 rows."], "forbidden_claims": ["A single CSV export is limited to 10,000 rows.", "Exports larger than the limit are refused."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X5 | mechanical | S1 R1/X5 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | EXT-X5 | mechanical | S1 R1/X5 reason | {"equals": "conflict"} | "conflict" | PASS |  |
| extended | EXT-X5 | mechanical | S1 R1/X5 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X5 | mechanical | S1 R1/X5 answer | {"equals": ""} | "" | PASS |  |
| extended | EXT-X5 | mechanical | S1 R1/X5 conflicts_shown | {"ids_include": ["EXPORT-FILES-v1:p1", "EXPORT-HELP-v1:p1"]} | ["EXPORT-FILES-v1:p1", "EXPORT-HELP-v1:p1"] | PASS |  |
| extended | EXT-X6 | mechanical | S1 R1/X6 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | EXT-X6 | mechanical | S1 R1/X6 reason | {"equals": "undocumented"} | "undocumented" | PASS |  |
| extended | EXT-X6 | mechanical | S1 R1/X6 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X6 | mechanical | S1 R1/X6 answer | {"equals": ""} | "" | PASS |  |
| extended | EXT-X7 | mechanical | S1 R1/X7 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X7 | mechanical | S1 R1/X7 citations | {"ids_subset_of": ["SUPPORT-REPLY-v1:p1"], "non_empty": true} | [{"passage_id": "SUPPORT-REPLY-v1:p1", "doc_id": "SUPPORT-REPLY-v1", "version": 1, "excerpt": "Paid-plan customers receive a first reply to email support within | PASS |  |
| extended | EXT-X7 | mechanical | S1 R1/X7 citations | {"excerpts_verbatim": true} | [{"passage_id": "SUPPORT-REPLY-v1:p1", "doc_id": "SUPPORT-REPLY-v1", "version": 1, "excerpt": "Paid-plan customers receive a first reply to email support within | PASS |  |
| extended | EXT-X7 | mechanical | S1 R1/X7 owner | {"equals": "Support reviewer"} | "Support reviewer" | PASS |  |
| extended | EXT-X7 | meaning | S1 R1/X7 answer | {"expected_facts": ["Paid-plan customers get a first reply to email support within one business day."], "forbidden_claims": ["Paid-plan customers wait up to three business days for a first reply.", "The first reply comes within 24 hours."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X8 | mechanical | S1 R1/X8 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X8 | mechanical | S1 R1/X8 citations | {"ids_subset_of": ["SUPPORT-CHANNELS-v1:p1"], "non_empty": true} | [{"passage_id": "SUPPORT-CHANNELS-v1:p1", "doc_id": "SUPPORT-CHANNELS-v1", "version": 1, "excerpt": "Phone support is not offered."}] | PASS |  |
| extended | EXT-X8 | mechanical | S1 R1/X8 citations | {"excerpts_verbatim": true} | [{"passage_id": "SUPPORT-CHANNELS-v1:p1", "doc_id": "SUPPORT-CHANNELS-v1", "version": 1, "excerpt": "Phone support is not offered."}] | PASS |  |
| extended | EXT-X8 | mechanical | S1 R1/X8 owner | {"equals": "Support reviewer"} | "Support reviewer" | PASS |  |
| extended | EXT-X8 | meaning | S1 R1/X8 answer | {"expected_facts": ["Phone support is not offered (the answer is No)."], "forbidden_claims": ["Phone support is offered or available."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X9 | mechanical | S1 R1/X9 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | EXT-X9 | mechanical | S1 R1/X9 reason | {"equals": "undocumented"} | "undocumented" | PASS |  |
| extended | EXT-X9 | mechanical | S1 R1/X9 owner | {"equals": "Support reviewer"} | "Support reviewer" | PASS |  |
| extended | EXT-X9 | mechanical | S1 R1/X9 answer | {"equals": ""} | "" | PASS |  |
| extended | EXT-X10 | mechanical | S1 R1/X10 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X10 | mechanical | S1 R1/X10 citations | {"ids_subset_of": ["SUPPORT-STATUS-v2:p1"], "non_empty": true} | [{"passage_id": "SUPPORT-STATUS-v2:p1", "doc_id": "SUPPORT-STATUS-v2", "version": 2, "excerpt": "During an incident, status updates are posted every 30 minutes. | PASS |  |
| extended | EXT-X10 | mechanical | S1 R1/X10 citations | {"excerpts_verbatim": true} | [{"passage_id": "SUPPORT-STATUS-v2:p1", "doc_id": "SUPPORT-STATUS-v2", "version": 2, "excerpt": "During an incident, status updates are posted every 30 minutes. | PASS |  |
| extended | EXT-X10 | mechanical | S1 R1/X10 owner | {"equals": "Support reviewer"} | "Support reviewer" | PASS |  |
| extended | EXT-X10 | mechanical | S1 R1/X10 replaced_shown | {"ids_include": ["SUPPORT-STATUS-v1:p1"]} | ["SUPPORT-STATUS-v1:p1"] | PASS |  |
| extended | EXT-X10 | meaning | S1 R1/X10 answer | {"expected_facts": ["During an incident, status updates are posted every 30 minutes."], "forbidden_claims": ["Status updates are posted every hour."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X11 | mechanical | S1 R1/X11 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | EXT-X11 | mechanical | S1 R1/X11 reason | {"equals": "conflict"} | "conflict" | PASS |  |
| extended | EXT-X11 | mechanical | S1 R1/X11 owner | {"equals": "Support reviewer"} | "Support reviewer" | PASS |  |
| extended | EXT-X11 | mechanical | S1 R1/X11 answer | {"equals": ""} | "" | PASS |  |
| extended | EXT-X11 | mechanical | S1 R1/X11 conflicts_shown | {"ids_include": ["SUPPORT-FAQ-v1:p1", "SUPPORT-HELPCENTRE-v1:p1"]} | ["SUPPORT-FAQ-v1:p1", "SUPPORT-HELPCENTRE-v1:p1"] | PASS |  |
| extended | EXT-X12 | mechanical | S1 R1/X12 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X12 | mechanical | S1 R1/X12 citations | {"ids_subset_of": ["SUPPORT-TICKETS-v1:p1"], "non_empty": true} | [{"passage_id": "SUPPORT-TICKETS-v1:p1", "doc_id": "SUPPORT-TICKETS-v1", "version": 1, "excerpt": "Support tickets are closed automatically after 14 days withou | PASS |  |
| extended | EXT-X12 | mechanical | S1 R1/X12 citations | {"excerpts_verbatim": true} | [{"passage_id": "SUPPORT-TICKETS-v1:p1", "doc_id": "SUPPORT-TICKETS-v1", "version": 1, "excerpt": "Support tickets are closed automatically after 14 days withou | PASS |  |
| extended | EXT-X12 | mechanical | S1 R1/X12 owner | {"equals": "Support reviewer"} | "Support reviewer" | PASS |  |
| extended | EXT-X12 | meaning | S1 R1/X12 answer | {"expected_facts": ["Support tickets are closed automatically after 14 days without a customer reply."], "forbidden_claims": ["Tickets are closed after a period other than 14 days.", "Tickets are closed 14 days after they are opened."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X13 | mechanical | S1 R1/X13 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X13 | mechanical | S1 R1/X13 citations | {"ids_subset_of": ["ACCESS-2FA-v1:p1"], "non_empty": true} | [{"passage_id": "ACCESS-2FA-v1:p1", "doc_id": "ACCESS-2FA-v1", "version": 1, "excerpt": "Account owners can require two-factor authentication for the whole team | PASS |  |
| extended | EXT-X13 | mechanical | S1 R1/X13 citations | {"excerpts_verbatim": true} | [{"passage_id": "ACCESS-2FA-v1:p1", "doc_id": "ACCESS-2FA-v1", "version": 1, "excerpt": "Account owners can require two-factor authentication for the whole team | PASS |  |
| extended | EXT-X13 | mechanical | S1 R1/X13 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X13 | meaning | S1 R1/X13 answer | {"expected_facts": ["Yes, account owners can require two-factor authentication for the whole team."], "forbidden_claims": ["Two-factor authentication is required for every user by default."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X14 | mechanical | S1 R1/X14 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X14 | mechanical | S1 R1/X14 citations | {"ids_subset_of": ["ACCESS-2FA-v1:p1"], "non_empty": true} | [{"passage_id": "ACCESS-2FA-v1:p1", "doc_id": "ACCESS-2FA-v1", "version": 1, "excerpt": "Each user can turn on two-factor authentication in their profile settin | PASS |  |
| extended | EXT-X14 | mechanical | S1 R1/X14 citations | {"excerpts_verbatim": true} | [{"passage_id": "ACCESS-2FA-v1:p1", "doc_id": "ACCESS-2FA-v1", "version": 1, "excerpt": "Each user can turn on two-factor authentication in their profile settin | PASS |  |
| extended | EXT-X14 | mechanical | S1 R1/X14 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X14 | meaning | S1 R1/X14 answer | {"expected_facts": ["Each user can turn on two-factor authentication for their own account."], "forbidden_claims": ["Only account owners can turn on two-factor authentication.", "Only administrators can turn on two-factor authentication."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X15 | mechanical | S1 R1/X15 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | EXT-X15 | mechanical | S1 R1/X15 reason | {"equals": "undocumented"} | "undocumented" | PASS |  |
| extended | EXT-X15 | mechanical | S1 R1/X15 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X15 | mechanical | S1 R1/X15 answer | {"equals": ""} | "" | PASS |  |
| extended | EXT-X16 | mechanical | S1 R1/X16 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X16 | mechanical | S1 R1/X16 citations | {"ids_subset_of": ["ACCESS-SESSION-v2:p1"], "non_empty": true} | [{"passage_id": "ACCESS-SESSION-v2:p1", "doc_id": "ACCESS-SESSION-v2", "version": 2, "excerpt": "Inactive sessions are signed out after 8 hours."}] | PASS |  |
| extended | EXT-X16 | mechanical | S1 R1/X16 citations | {"excerpts_verbatim": true} | [{"passage_id": "ACCESS-SESSION-v2:p1", "doc_id": "ACCESS-SESSION-v2", "version": 2, "excerpt": "Inactive sessions are signed out after 8 hours."}] | PASS |  |
| extended | EXT-X16 | mechanical | S1 R1/X16 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X16 | mechanical | S1 R1/X16 replaced_shown | {"ids_include": ["ACCESS-SESSION-v1:p1"]} | ["ACCESS-SESSION-v1:p1"] | PASS |  |
| extended | EXT-X16 | meaning | S1 R1/X16 answer | {"expected_facts": ["Inactive sessions are signed out after 8 hours."], "forbidden_claims": ["Inactive sessions are signed out after 12 hours."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X17 | mechanical | S1 R1/X17 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X17 | mechanical | S1 R1/X17 citations | {"ids_subset_of": ["ACCESS-PASSWORD-v1:p1"], "non_empty": true} | [{"passage_id": "ACCESS-PASSWORD-v1:p1", "doc_id": "ACCESS-PASSWORD-v1", "version": 1, "excerpt": "Passwords do not expire."}] | PASS |  |
| extended | EXT-X17 | mechanical | S1 R1/X17 citations | {"excerpts_verbatim": true} | [{"passage_id": "ACCESS-PASSWORD-v1:p1", "doc_id": "ACCESS-PASSWORD-v1", "version": 1, "excerpt": "Passwords do not expire."}] | PASS |  |
| extended | EXT-X17 | mechanical | S1 R1/X17 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X17 | meaning | S1 R1/X17 answer | {"expected_facts": ["Passwords do not expire (the answer is No)."], "forbidden_claims": ["Passwords expire after some period."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X18 | mechanical | S1 R1/X18 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | EXT-X18 | mechanical | S1 R1/X18 reason | {"equals": "conflict"} | "conflict" | PASS |  |
| extended | EXT-X18 | mechanical | S1 R1/X18 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X18 | mechanical | S1 R1/X18 answer | {"equals": ""} | "" | PASS |  |
| extended | EXT-X18 | mechanical | S1 R1/X18 conflicts_shown | {"ids_include": ["ACCESS-GUEST-NOTE-v1:p1", "ACCESS-GUEST-v1:p1"]} | ["ACCESS-GUEST-NOTE-v1:p1", "ACCESS-GUEST-v1:p1"] | PASS |  |
| extended | EXT-X19 | mechanical | S1 R1/X19 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X19 | mechanical | S1 R1/X19 citations | {"ids_subset_of": ["ACCESS-AUDIT-v1:p1"], "non_empty": true} | [{"passage_id": "ACCESS-AUDIT-v1:p1", "doc_id": "ACCESS-AUDIT-v1", "version": 1, "excerpt": "Sign-in attempts are kept in the audit log for 90 days."}] | PASS |  |
| extended | EXT-X19 | mechanical | S1 R1/X19 citations | {"excerpts_verbatim": true} | [{"passage_id": "ACCESS-AUDIT-v1:p1", "doc_id": "ACCESS-AUDIT-v1", "version": 1, "excerpt": "Sign-in attempts are kept in the audit log for 90 days."}] | PASS |  |
| extended | EXT-X19 | mechanical | S1 R1/X19 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X19 | meaning | S1 R1/X19 answer | {"expected_facts": ["Sign-in attempts are kept in the audit log for 90 days."], "forbidden_claims": ["Sign-in attempts are kept for a period other than 90 days."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X20 | mechanical | S1 R1/X20 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X20 | mechanical | S1 R1/X20 citations | {"ids_subset_of": ["BILLING-REFUND-v2:p1"], "non_empty": true} | [{"passage_id": "BILLING-REFUND-v2:p1", "doc_id": "BILLING-REFUND-v2", "version": 2, "excerpt": "Refunds can be requested within 30 days of a payment."}] | PASS |  |
| extended | EXT-X20 | mechanical | S1 R1/X20 citations | {"excerpts_verbatim": true} | [{"passage_id": "BILLING-REFUND-v2:p1", "doc_id": "BILLING-REFUND-v2", "version": 2, "excerpt": "Refunds can be requested within 30 days of a payment."}] | PASS |  |
| extended | EXT-X20 | mechanical | S1 R1/X20 owner | {"equals": "Billing reviewer"} | "Billing reviewer" | PASS |  |
| extended | EXT-X20 | mechanical | S1 R1/X20 replaced_shown | {"ids_include": ["BILLING-REFUND-v1:p1"]} | ["BILLING-REFUND-v1:p1"] | PASS |  |
| extended | EXT-X20 | meaning | S1 R1/X20 answer | {"expected_facts": ["A refund can be requested within 30 days of a payment."], "forbidden_claims": ["Refunds must be requested within 14 days."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X21 | mechanical | S1 R1/X21 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X21 | mechanical | S1 R1/X21 citations | {"ids_subset_of": ["BILLING-PAYMENT-v1:p1"], "non_empty": true} | [{"passage_id": "BILLING-PAYMENT-v1:p1", "doc_id": "BILLING-PAYMENT-v1", "version": 1, "excerpt": "Payments can be made by credit card."}] | PASS |  |
| extended | EXT-X21 | mechanical | S1 R1/X21 citations | {"excerpts_verbatim": true} | [{"passage_id": "BILLING-PAYMENT-v1:p1", "doc_id": "BILLING-PAYMENT-v1", "version": 1, "excerpt": "Payments can be made by credit card."}] | PASS |  |
| extended | EXT-X21 | mechanical | S1 R1/X21 owner | {"equals": "Billing reviewer"} | "Billing reviewer" | PASS |  |
| extended | EXT-X21 | meaning | S1 R1/X21 answer | {"expected_facts": ["Yes, payments can be made by credit card."], "forbidden_claims": ["Credit card is the only accepted payment method."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X22 | mechanical | S1 R1/X22 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | EXT-X22 | mechanical | S1 R1/X22 reason | {"equals": "undocumented"} | "undocumented" | PASS |  |
| extended | EXT-X22 | mechanical | S1 R1/X22 owner | {"equals": "Billing reviewer"} | "Billing reviewer" | PASS |  |
| extended | EXT-X22 | mechanical | S1 R1/X22 answer | {"equals": ""} | "" | PASS |  |
| extended | EXT-X23 | mechanical | S1 R1/X23 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-X23 | mechanical | S1 R1/X23 citations | {"ids_subset_of": ["BILLING-TERMS-v1:p1"], "non_empty": true} | [{"passage_id": "BILLING-TERMS-v1:p1", "doc_id": "BILLING-TERMS-v1", "version": 1, "excerpt": "Annual billing is not offered."}] | PASS |  |
| extended | EXT-X23 | mechanical | S1 R1/X23 citations | {"excerpts_verbatim": true} | [{"passage_id": "BILLING-TERMS-v1:p1", "doc_id": "BILLING-TERMS-v1", "version": 1, "excerpt": "Annual billing is not offered."}] | PASS |  |
| extended | EXT-X23 | mechanical | S1 R1/X23 owner | {"equals": "Billing reviewer"} | "Billing reviewer" | PASS |  |
| extended | EXT-X23 | meaning | S1 R1/X23 answer | {"expected_facts": ["Annual billing is not offered (the answer is No)."], "forbidden_claims": ["Annual billing is offered or available."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| extended | EXT-X24 | mechanical | S1 R1/X24 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | EXT-X24 | mechanical | S1 R1/X24 reason | {"equals": "conflict"} | "conflict" | PASS |  |
| extended | EXT-X24 | mechanical | S1 R1/X24 owner | {"equals": "Billing reviewer"} | "Billing reviewer" | PASS |  |
| extended | EXT-X24 | mechanical | S1 R1/X24 answer | {"equals": ""} | "" | PASS |  |
| extended | EXT-X24 | mechanical | S1 R1/X24 conflicts_shown | {"ids_include": ["BILLING-PRICING-v1:p1", "BILLING-TAX-v1:p1"]} | ["BILLING-PRICING-v1:p1", "BILLING-TAX-v1:p1"] | PASS |  |
| extended | EXT-X25 | mechanical | S1 R1/X25 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | EXT-X25 | mechanical | S1 R1/X25 reason | {"equals": "undocumented"} | "undocumented" | PASS |  |
| extended | EXT-X25 | mechanical | S1 R1/X25 owner | {"equals": "Billing reviewer"} | "Billing reviewer" | PASS |  |
| extended | EXT-X25 | mechanical | S1 R1/X25 answer | {"equals": ""} | "" | PASS |  |
| extended | EXT-X26 | mechanical | S1 R1/X26 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | EXT-X26 | mechanical | S1 R1/X26 reason | {"equals": "undocumented"} | "undocumented" | PASS |  |
| extended | EXT-X26 | mechanical | S1 R1/X26 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| extended | EXT-X26 | mechanical | S1 R1/X26 answer | {"equals": ""} | "" | PASS |  |
| extended | EXT-REUSE | mechanical | S2 R1/X1 status | {"equals": "approved"} | "approved" | PASS |  |
| extended | EXT-REUSE | mechanical | S2 R1/X1 approval.text | {"equals_text": "A1"} | "Scheduled exports run once a day at 02:00 UTC." | PASS |  |
| extended | EXT-REUSE | mechanical | S2 R1/X1 approval.sources | {"versions": {"EXPORT-SCHEDULE-v1:p1": 1}} | [{"passage_id": "EXPORT-SCHEDULE-v1:p1", "doc_id": "EXPORT-SCHEDULE-v1", "version": 1, "excerpt": "Scheduled exports run once a day at 02:00 UTC."}] | PASS |  |
| extended | EXT-REUSE | mechanical | S2 R1/X12 edited | {"equals": true} | true | PASS |  |
| extended | EXT-REUSE | mechanical | S2 R1/X12 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-REUSE | mechanical | S3 R2/X1 status | {"equals": "approved"} | "approved" | PASS |  |
| extended | EXT-REUSE | mechanical | S3 R2/X1 reused | {"equals": true} | true | PASS |  |
| extended | EXT-REUSE | mechanical | S3 R2/X1 answer | {"equals_text": "A1"} | "Scheduled exports run once a day at 02:00 UTC." | PASS |  |
| extended | EXT-REUSE | mechanical | S3 R2/X1 calls | {"equals": []} | [] | PASS |  |
| extended | EXT-REUSE | mechanical | S3 R2/X13 reused | {"equals": true} | true | PASS |  |
| extended | EXT-REUSE | mechanical | S3 R2/X13 answer | {"equals_text": "A13"} | "Yes. Account owners can require two-factor authentication for the whole team." | PASS |  |
| extended | EXT-REUSE | mechanical | S3 R2/X12 reused | {"equals": false} | false | PASS |  |
| extended | EXT-REUSE | mechanical | S3 R2/X12 answer | {"not_equals_text": "E12"} | "Support tickets are closed automatically after 14 days without a customer reply." | PASS |  |
| extended | EXT-CHANGE | mechanical | S4 R1/X13 status | {"equals": "needs_review"} | "needs_review" | PASS |  |
| extended | EXT-CHANGE | mechanical | S4 R1/X13 reason | {"equals": "source_changed"} | "source_changed" | PASS |  |
| extended | EXT-CHANGE | mechanical | S4 R2/X13 status | {"equals": "needs_review"} | "needs_review" | PASS |  |
| extended | EXT-CHANGE | mechanical | S4 R1/X1 status | {"equals": "approved"} | "approved" | PASS |  |
| extended | EXT-CHANGE | mechanical | S5 R3/X13 reused | {"equals": false} | false | PASS |  |
| extended | EXT-CHANGE | mechanical | S5 R3/X13 status | {"equals": "answered"} | "answered" | PASS |  |
| extended | EXT-CHANGE | mechanical | S5 R3/X13 stale_approval_shown | {"equals": "A2"} | "A2" | PASS |  |
| extended | EXT-CHANGE | mechanical | S5 R3/X13 calls | {"non_empty": true} | [{"call_type": "draft", "label": "REPLAYED", "fingerprint": "93ed29bea1636319fdbe2de284660929a5a51d00c802cf34136a895d6eb0fe03", "model": "gemini-3.8-flash", "re | PASS |  |
| extended | EXT-CHANGE | mechanical | S5 R3/X1 reused | {"equals": true} | true | PASS |  |
| extended | EXT-NOTE | mechanical | S2 R1/X5 note | {"equals_text": "N5"} | "Needs Product reviewer: EXPORT-FILES-v1 and EXPORT-HELP-v1 give different download periods, and neither supersedes the other." | PASS |  |
| extended | EXT-NOTE | mechanical | S2 R1/X5 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| extended | counts | mechanical | S1 R1 | [15, 11, 0, 0, 0] | [15, 11, 0, 0, 0] | PASS |  |
| extended | counts | mechanical | S2 R1 | [13, 11, 2, 0, 0] | [13, 11, 2, 0, 0] | PASS |  |
| extended | counts | mechanical | S3 R1 | [13, 11, 2, 0, 0] | [13, 11, 2, 0, 0] | PASS |  |
| extended | counts | mechanical | S3 R2 | [13, 11, 2, 0, 0] | [13, 11, 2, 0, 0] | PASS |  |
| extended | counts | mechanical | S4 R1 | [13, 11, 1, 1, 0] | [13, 11, 1, 1, 0] | PASS |  |
| extended | counts | mechanical | S4 R2 | [13, 11, 1, 1, 0] | [13, 11, 1, 1, 0] | PASS |  |
| extended | counts | mechanical | S5 R1 | [13, 11, 1, 1, 0] | [13, 11, 1, 1, 0] | PASS |  |
| extended | counts | mechanical | S5 R2 | [13, 11, 1, 1, 0] | [13, 11, 1, 1, 0] | PASS |  |
| extended | counts | mechanical | S5 R3 | [14, 11, 1, 0, 0] | [14, 11, 1, 0, 0] | PASS |  |
