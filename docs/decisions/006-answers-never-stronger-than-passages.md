# 006 · Answers are never stronger than their passages ("can" is not "only")

- Status: accepted
- Requirements: Rule 1 of `data/seed/domain.md` ("Use only the supplied fictional product documents as evidence. An
  undocumented feature is unknown, not automatically supported or unsupported."); the assignment brief's "Flag
  unsupported claims and conflicting versions." and "Check that references and excerpts exist and that the cited
  content supports the answer." Ambiguity AMB-5.

## Context

ACCESS-v1:p1 says "Account owners can invite team members." and BILLING-v1:p1 says "Account owners can download
billing invoices." Neither says "only". Q6 and Q8 ask "Who can …?", so an answer such as "Only account owners can
invite team members." claims more than its passage. Only EXPORT-v2:p1 contains "only" ("CSV exports are available on
paid plans only."). The same issue appears for Q5 ("email and password" is supported; "only email and password", "SSO
is supported" and "SSO is not supported" are not) and Q7 ("monthly" is supported; "annual billing is not available"
is not).

An earlier draft of this design let code decide with a list of strengthening words (only, all, every, always, never,
exclusively, solely): a listed word in the answer that none of the cited passages contained made the item
`unresolved / unsupported_claim`, and the support check then never ran. Tried on sample sentences, the list misjudges
in both directions:

- "Account owners alone can invite team members." claims exclusivity, but contains no listed word, so it passes.
- "Email support is available every weekday, 09:00 to 17:00 UTC." restates SUPPORT-v1:p1 ("Monday to Friday"), but
  "every" is not in the passage, so it is flagged.
- A Q6 answer that cites both ACCESS-v1:p1 and EXPORT-v2:p1 escapes the flag, because "only" appears in one of its
  cited passages.

Whether a claim is stronger than its source is a question of meaning (decision 035).

## Options considered

1. **Code decides with the strengthening-word list (`unsupported_claim`, naming the word).** Deterministic and cheap,
   but it misjudges the examples above in both directions.
2. **The recorded support check decides; the word list is only a hint, passed to the support check and shown to the
   reviewer.** Meaning is judged by model reasoning whose response is saved, replayed and open to inspection.
3. **Treat every "who can" question as partly unknown, so unresolved.** Over-abstains; Q6 and Q8 would become
   unresolved although their passages answer them.

## Decision

Option 2.

- Code lists the strengthening words that appear in the answer but in none of its cited passages. The list is a hint
  only: it is sent with the support-check request, stored with the suggestion and shown to the reviewer. It never sets
  a status and never blocks an approval (decision 016).
- The support check runs on every answered draft that passes the mechanical checks (a support citation exists, every
  cited ID is loaded, no cited passage is replaced, every excerpt is verbatim, and the draft reports no verified
  conflict pair), and it decides `unsupported_claim`.
- The draft prompt still asks the model never to be stronger than the passage: no only, all, every, always or never
  unless the passage says so.
- Accepted answer forms, decided by reading the passages: Q6 and Q8 may say "Account owners can …" or simply "Account
  owners."; an answer must not say or imply that only account owners can, and must make no claim about other roles. Q7
  may say "Subscriptions are billed monthly" without the passage's "Paid". Q5 must not claim "only email and password",
  nor that SSO or any other method is or is not available.

## Consequences

- Q1's "paid plans only" raises no hint, because EXPORT-v2:p1 contains "only".
- Planted drafts (hand-written test inputs, labelled SIMULATED) pin the behaviour: P1 "Only account owners can invite
  team members." is expected `unsupported_claim`, decided by the support check, with the hint "only" logged; P1a
  "Account owners alone can invite team members." is expected `unsupported_claim` with no hint; P1b "Email support is
  available every weekday, 09:00 to 17:00 UTC." is expected `answered`, with the hint "every" logged. P1a and P1b show
  why the list cannot decide.
- Risk: the support check can be wrong. Its responses are saved, its verdicts appear in the results table, and a
  reviewer who approves over a "not supported" verdict must write a note (decision 016).

## Evidence

- `data/seed/seed.json:25`, `:38`, `:51`, `:64`.
- `data/seed/domain.md:5`.
