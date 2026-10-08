"""Decision 039: the added data loads cleanly beside the unchanged seed, as a separate questionnaire."""

import json

from qa.dataset import ROOT, load_dataset

EXTENDED = ROOT / "data" / "additions" / "extended.json"
SCENARIO = ROOT / "data" / "scenario" / "extended-demo.json"


def test_the_additions_load_with_no_issues_and_reuse_the_seed_topics_and_owners():
    seed = load_dataset()
    extended = load_dataset(additions_path=EXTENDED)
    assert extended.issues == []
    assert [q.id for q in extended.questions] == [f"X{n}" for n in range(1, 36)]
    assert {q.topic for q in extended.questions} == set(seed.owners)
    assert extended.owners == seed.owners
    assert set(seed.documents) < set(extended.documents)
    assert all(extended.documents[d] == seed.documents[d] for d in seed.documents)


def test_the_seed_questionnaire_is_unchanged_without_the_additions():
    seed = load_dataset()
    assert [q.id for q in seed.questions] == [f"Q{n}" for n in range(1, 9)]
    assert len(seed.documents) == 5


def test_every_added_supersedes_link_resolves_and_conflicting_pairs_have_none():
    dataset = load_dataset(additions_path=EXTENDED)
    replaced = dataset.replaced_ids
    for doc in dataset.documents.values():
        assert (doc.status == "superseded") == (doc.id in replaced), doc.id
    pairs = [("EXPORT-FILES-v1", "EXPORT-HELP-v1"), ("SUPPORT-HELPCENTRE-v1", "SUPPORT-FAQ-v1")]
    pairs += [("ACCESS-GUEST-v1", "ACCESS-GUEST-NOTE-v1"), ("BILLING-TAX-v1", "BILLING-PRICING-v1")]
    pairs += [("EXPORT-ENCRYPTION-v1", "EXPORT-GUIDE-v1"), ("ACCESS-READONLY-v1", "ACCESS-OVERVIEW-v1")]
    pairs += [("EXPORT-DELIMITER-v1", "EXPORT-DELIMITER-v2")]
    for older, newer in pairs:
        assert dataset.documents[older].date < dataset.documents[newer].date
        assert {dataset.documents[older].supersedes, dataset.documents[newer].supersedes} == {None}


def test_a_supersedes_link_wins_even_when_the_replacing_document_is_older():
    dataset = load_dataset(additions_path=EXTENDED)
    retry_v1, retry_v2 = dataset.documents["BILLING-RETRY-v1"], dataset.documents["BILLING-RETRY-v2"]
    assert retry_v2.date < retry_v1.date
    assert "BILLING-RETRY-v1" in dataset.replaced_ids and "BILLING-RETRY-v2:p1" in dataset.current_passage_ids
    assert {"EXPORT-DELIMITER-v1:p1", "EXPORT-DELIMITER-v2:p1"} <= dataset.current_passage_ids


def test_the_extended_scenario_names_items_and_passages_that_exist():
    dataset = load_dataset(additions_path=EXTENDED)
    scenario = json.loads(SCENARIO.read_text())
    question_ids = {q.id for q in dataset.questions}
    for step in scenario["steps"]:
        for action in step["actions"]:
            if "item" in action:
                assert action["item"].split("/")[1] in question_ids
            for source in action.get("sources", []):
                assert source in dataset.current_passage_ids
