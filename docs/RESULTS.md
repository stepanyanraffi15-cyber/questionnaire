# Check results

Written by `reference/grade.py` from `runs/report/observed.json`. Do not edit by hand.

- Mode: replay · model: gemini-3.8-flash
- Answer key sha256: dd744404df67da3b
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

## Every check

| Case | Kind | Where | Expected | Observed | Result | Sign-off |
|---|---|---|---|---|---|---|
| RC-1 | mechanical | S1 R1/Q3 status | {"equals": "answered"} | "answered" | PASS |  |
| RC-1 | mechanical | S1 R1/Q3 citations | {"ids_subset_of": ["SUPPORT-v1:p1"], "non_empty": true} | [{"passage_id": "SUPPORT-v1:p1", "doc_id": "SUPPORT-v1", "version": 1, "excerpt": "Email support is available Monday to Friday, 09:00 to 17:00 UTC."}] | PASS |  |
| RC-1 | mechanical | S1 R1/Q3 citations | {"excerpts_verbatim": true} | [{"passage_id": "SUPPORT-v1:p1", "doc_id": "SUPPORT-v1", "version": 1, "excerpt": "Email support is available Monday to Friday, 09:00 to 17:00 UTC."}] | PASS |  |
| RC-1 | mechanical | S1 R1/Q3 owner | {"equals": "Support reviewer"} | "Support reviewer" | PASS |  |
| RC-1 | mechanical | S1 R1/Q3 reason | {"not_equals": "conflict"} | null | PASS |  |
| RC-1 | meaning | S1 R1/Q3 answer | {"expected_facts": ["Email support is available Monday to Friday (all five weekdays, not only some of them).", "Support hours are 09:00 to 17:00 (9 am to 5 pm is the same).", "The times are in UTC."], "forbidden_claims": ["Email support is available at weekends.", "The hours are in a time zone other than UTC.", "Live chat is available or offered."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Raffi on 2026-10-08 |
| RC-2 | mechanical | S1 R1/Q2 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| RC-2 | mechanical | S1 R1/Q2 reason | {"equals": "undocumented"} | "undocumented" | PASS |  |
| RC-2 | mechanical | S1 R1/Q2 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| RC-2 | mechanical | S1 R1/Q2 answer | {"equals": ""} | "" | PASS |  |
| RC-2 | mechanical | S1 R1/Q2 citations | {"equals": []} | [] | PASS |  |
| RC-2 | mechanical | S2 R1/Q2 note | {"equals_text": "N"} | "Needs Product reviewer: JSON export is not documented." | PASS |  |
| RC-2 | mechanical | S2 R1/Q2 status | {"equals": "unresolved"} | "unresolved" | PASS |  |
| RC-2 | meaning | S1 R1/Q2 suggestion.answer | {"expected_facts": [], "forbidden_claims": ["JSON export is available.", "JSON export is not available or not supported.", "The CSV paid-plan rule also covers JSON export."]} | empty text states nothing, so no forbidden claim is made | PASS | not needed |
| RC-3 | mechanical | S1 R1/Q1 status | {"equals": "answered"} | "answered" | PASS |  |
| RC-3 | mechanical | S1 R1/Q1 citations | {"ids_subset_of": ["EXPORT-v2:p1"], "non_empty": true} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 2, "excerpt": "CSV exports are available on paid plans only."}, {"passage_id": "EXPORT-v2:p1", | PASS |  |
| RC-3 | mechanical | S1 R1/Q1 citations | {"excerpts_verbatim": true} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 2, "excerpt": "CSV exports are available on paid plans only."}, {"passage_id": "EXPORT-v2:p1", | PASS |  |
| RC-3 | mechanical | S1 R1/Q1 replaced_shown | {"ids_include": ["EXPORT-v1:p1"]} | ["EXPORT-v1:p1"] | PASS |  |
| RC-3 | mechanical | S1 R1/Q1 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| RC-3 | mechanical | S1 R1/Q1 reason | {"not_equals": "conflict"} | null | PASS |  |
| RC-3 | meaning | S1 R1/Q1 answer | {"expected_facts": ["The answer is no: free-plan users cannot export CSV.", "CSV export is for paid plans only."], "forbidden_claims": ["Free-plan users can export CSV.", "CSV export is available on every plan as the current policy (mentioning the old, replaced policy as replaced is fine)."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Raffi on 2026-10-08 |
| RC-4 | mechanical | S3 R2/Q1 status | {"equals": "answered"} | "answered" | PASS |  |
| RC-4 | mechanical | S3 R2/Q1 reused | {"equals": false} | false | PASS |  |
| RC-4 | mechanical | S3 R2/Q1 answer | {"not_equals_text": "W"} | "No. CSV exports are available on paid plans only." | PASS |  |
| RC-4 | mechanical | S3 R2/Q1 calls | {"non_empty": true} | [{"call_type": "draft", "label": "REPLAYED", "fingerprint": "f3e209d537da5eef00e6219195c40332ec7b069cbbb1da5020615789d3634bbc", "model": "gemini-3.8-flash", "re | PASS |  |
| RC-4 | mechanical | S3 R2/Q3 answer | {"not_equals_text": "E3"} | "Email support is available Monday to Friday, 09:00 to 17:00 UTC." | PASS |  |
| RC-4 | mechanical | S4 R1/Q1 status | {"equals": "approved"} | "approved" | PASS |  |
| RC-4 | mechanical | S4 R1/Q1 approval.text | {"equals_text": "W"} | "No. CSV export is for paid plans only; free-plan users cannot export CSV." | PASS |  |
| RC-4 | mechanical | S4 R1/Q1 approval.approver | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| RC-4 | mechanical | S4 R1/Q1 approval.at | {"equals": "2026-10-08T09:03:00Z"} | "2026-10-08T09:03:00Z" | PASS |  |
| RC-4 | mechanical | S4 R1/Q1 approval.sources | {"versions": {"EXPORT-v2:p1": 2}} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 2, "excerpt": "Free-plan users cannot export CSV."}] | PASS |  |
| RC-4 | mechanical | S4 R2/Q1 status | {"equals": "answered"} | "answered" | PASS |  |
| RC-4 | mechanical | S5 R3/Q1 status | {"equals": "approved"} | "approved" | PASS |  |
| RC-4 | mechanical | S5 R3/Q1 reused | {"equals": true} | true | PASS |  |
| RC-4 | mechanical | S5 R3/Q1 answer | {"equals_text": "W"} | "No. CSV export is for paid plans only; free-plan users cannot export CSV." | PASS |  |
| RC-4 | mechanical | S5 R3/Q1 approval.item | {"equals": "R1/Q1"} | "R1/Q1" | PASS |  |
| RC-4 | mechanical | S5 R3/Q1 approval.approver | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| RC-4 | mechanical | S5 R3/Q1 approval.sources | {"versions": {"EXPORT-v2:p1": 2}} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 2, "excerpt": "Free-plan users cannot export CSV."}] | PASS |  |
| RC-4 | mechanical | S5 R3/Q1 replaced_shown | {"ids_include": ["EXPORT-v1:p1"]} | ["EXPORT-v1:p1"] | PASS |  |
| RC-4 | mechanical | S5 R3/Q1 calls | {"equals": []} | [] | PASS |  |
| RC-4 | mechanical | S5 R3/Q3 status | {"equals": "answered"} | "answered" | PASS |  |
| RC-4 | mechanical | S5 R3/Q3 answer | {"not_equals_text": "E3"} | "Email support is available Monday to Friday, 09:00 to 17:00 UTC." | PASS |  |
| RC-4 | mechanical | S5 R1/Q3 edited | {"equals": true} | true | PASS |  |
| RC-4 | mechanical | S5 R1/Q3 status | {"equals": "answered"} | "answered" | PASS |  |
| RC-5 | mechanical | S6 | {"same_as": "S5"} | items and counts equal S5 | PASS |  |
| RC-5 | mechanical | S7 R1/Q1 status | {"equals": "needs_review"} | "needs_review" | PASS |  |
| RC-5 | mechanical | S7 R1/Q1 approval.stale_reasons | {"equals": [{"doc_id": "EXPORT-v2", "approved_version": 2, "current_version": 3, "change": "version"}]} | [{"doc_id": "EXPORT-v2", "approved_version": 2, "current_version": 3, "change": "version"}] | PASS |  |
| RC-5 | mechanical | S7 R3/Q1 status | {"equals": "needs_review"} | "needs_review" | PASS |  |
| RC-5 | mechanical | S7 R3/Q1 approval.stale_reasons | {"equals": [{"doc_id": "EXPORT-v2", "approved_version": 2, "current_version": 3, "change": "version"}]} | [{"doc_id": "EXPORT-v2", "approved_version": 2, "current_version": 3, "change": "version"}] | PASS |  |
| RC-5 | mechanical | S7 R2/Q1 status | {"equals": "answered"} | "answered" | PASS |  |
| RC-5 | mechanical | S8 R4/Q1 status | {"equals": "answered"} | "answered" | PASS |  |
| RC-5 | mechanical | S8 R4/Q1 reused | {"equals": false} | false | PASS |  |
| RC-5 | mechanical | S8 R4/Q1 stale_approval_shown | {"not_equals": null} | "A1" | PASS |  |
| RC-5 | mechanical | S8 R4/Q1 calls | {"non_empty": true} | [{"call_type": "draft", "label": "REPLAYED", "fingerprint": "f3e209d537da5eef00e6219195c40332ec7b069cbbb1da5020615789d3634bbc", "model": "gemini-3.8-flash", "re | PASS |  |
| RC-5 | mechanical | S9 | {"same_as": "S8"} | items and counts equal S8 | PASS |  |
| XR-1 | mechanical | S10 R1/Q1 status | {"equals": "approved"} | "approved" | PASS |  |
| XR-1 | mechanical | S10 R1/Q1 approval.sources | {"versions": {"EXPORT-v2:p1": 3}} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 3, "excerpt": "Free-plan users cannot export CSV."}] | PASS |  |
| XR-1 | mechanical | S10 R3/Q1 status | {"equals": "needs_review"} | "needs_review" | PASS |  |
| XR-1 | mechanical | S11 R5/Q1 status | {"equals": "approved"} | "approved" | PASS |  |
| XR-1 | mechanical | S11 R5/Q1 reused | {"equals": true} | true | PASS |  |
| XR-1 | mechanical | S11 R5/Q1 answer | {"equals_text": "W"} | "No. CSV export is for paid plans only; free-plan users cannot export CSV." | PASS |  |
| XR-1 | mechanical | S11 R5/Q1 approval.sources | {"versions": {"EXPORT-v2:p1": 3}} | [{"passage_id": "EXPORT-v2:p1", "doc_id": "EXPORT-v2", "version": 3, "excerpt": "Free-plan users cannot export CSV."}] | PASS |  |
| XR-1 | mechanical | S11 R5/Q1 calls | {"equals": []} | [] | PASS |  |
| XR-Q4 | mechanical | S1 R1/Q4 status | {"equals": "answered"} | "answered" | PASS |  |
| XR-Q4 | mechanical | S1 R1/Q4 citations | {"ids_subset_of": ["SUPPORT-v1:p1"], "non_empty": true} | [{"passage_id": "SUPPORT-v1:p1", "doc_id": "SUPPORT-v1", "version": 1, "excerpt": "Live chat is not offered."}] | PASS |  |
| XR-Q4 | mechanical | S1 R1/Q4 owner | {"equals": "Support reviewer"} | "Support reviewer" | PASS |  |
| XR-Q4 | meaning | S1 R1/Q4 answer | {"expected_facts": ["No: live chat is not offered."], "forbidden_claims": ["Live chat is offered.", "Another support channel, such as phone support, is offered."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| XR-Q5 | mechanical | S1 R1/Q5 status | {"equals": "answered"} | "answered" | PASS |  |
| XR-Q5 | mechanical | S1 R1/Q5 citations | {"ids_subset_of": ["ACCESS-v1:p1"], "non_empty": true} | [{"passage_id": "ACCESS-v1:p1", "doc_id": "ACCESS-v1", "version": 1, "excerpt": "Users can sign in with email and password."}] | PASS |  |
| XR-Q5 | mechanical | S1 R1/Q5 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| XR-Q5 | meaning | S1 R1/Q5 answer | {"expected_facts": ["Users sign in with email and password."], "forbidden_claims": ["Email and password is the only sign-in method.", "Single sign-on (SSO) or another sign-in method is available, or is not available."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Raffi on 2026-10-08 |
| XR-Q6 | mechanical | S1 R1/Q6 status | {"equals": "answered"} | "answered" | PASS |  |
| XR-Q6 | mechanical | S1 R1/Q6 citations | {"ids_subset_of": ["ACCESS-v1:p1"], "non_empty": true} | [{"passage_id": "ACCESS-v1:p1", "doc_id": "ACCESS-v1", "version": 1, "excerpt": "Account owners can invite team members."}] | PASS |  |
| XR-Q6 | mechanical | S1 R1/Q6 owner | {"equals": "Product reviewer"} | "Product reviewer" | PASS |  |
| XR-Q6 | meaning | S1 R1/Q6 answer | {"expected_facts": ["Account owners can invite team members (the bare answer \"Account owners.\" is acceptable)."], "forbidden_claims": ["Only account owners can invite team members.", "Any claim about whether other roles can invite team members."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Raffi on 2026-10-08 |
| XR-Q7 | mechanical | S1 R1/Q7 status | {"equals": "answered"} | "answered" | PASS |  |
| XR-Q7 | mechanical | S1 R1/Q7 citations | {"ids_subset_of": ["BILLING-v1:p1"], "non_empty": true} | [{"passage_id": "BILLING-v1:p1", "doc_id": "BILLING-v1", "version": 1, "excerpt": "Paid subscriptions are billed monthly in USD."}] | PASS |  |
| XR-Q7 | mechanical | S1 R1/Q7 owner | {"equals": "Billing reviewer"} | "Billing reviewer" | PASS |  |
| XR-Q7 | meaning | S1 R1/Q7 answer | {"expected_facts": ["Subscriptions are billed monthly (saying \"paid subscriptions\" or mentioning USD is fine, and leaving them out is fine)."], "forbidden_claims": ["Subscriptions are billed at another frequency, such as yearly.", "No other billing frequency exists."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PENDING | awaiting the author's sign-off |
| XR-Q8 | mechanical | S1 R1/Q8 status | {"equals": "answered"} | "answered" | PASS |  |
| XR-Q8 | mechanical | S1 R1/Q8 citations | {"ids_subset_of": ["BILLING-v1:p1"], "non_empty": true} | [{"passage_id": "BILLING-v1:p1", "doc_id": "BILLING-v1", "version": 1, "excerpt": "Account owners can download billing invoices."}] | PASS |  |
| XR-Q8 | mechanical | S1 R1/Q8 owner | {"equals": "Billing reviewer"} | "Billing reviewer" | PASS |  |
| XR-Q8 | meaning | S1 R1/Q8 answer | {"expected_facts": ["Account owners can download billing invoices (the bare answer \"Account owners.\" is acceptable)."], "forbidden_claims": ["Only account owners can download billing invoices.", "Any claim about whether other roles can download invoices."]} | judge (gemini-3.8-flash): all facts stated, no forbidden claim | PASS | pass by Raffi on 2026-10-08 |
| counts | mechanical | S1 R1 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S2 R1 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S3 R1 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S3 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S4 R1 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| counts | mechanical | S4 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S5 R1 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| counts | mechanical | S5 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S5 R3 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| counts | mechanical | S6 R1 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| counts | mechanical | S6 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S6 R3 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| counts | mechanical | S7 R1 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| counts | mechanical | S7 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S7 R3 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| counts | mechanical | S8 R1 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| counts | mechanical | S8 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S8 R3 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| counts | mechanical | S8 R4 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S9 R1 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| counts | mechanical | S9 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S9 R3 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| counts | mechanical | S9 R4 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S10 R1 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| counts | mechanical | S10 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S10 R3 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| counts | mechanical | S10 R4 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S11 R1 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
| counts | mechanical | S11 R2 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S11 R3 | [6, 1, 0, 1, 0] | [6, 1, 0, 1, 0] | PASS |  |
| counts | mechanical | S11 R4 | [7, 1, 0, 0, 0] | [7, 1, 0, 0, 0] | PASS |  |
| counts | mechanical | S11 R5 | [6, 1, 1, 0, 0] | [6, 1, 1, 0, 0] | PASS |  |
