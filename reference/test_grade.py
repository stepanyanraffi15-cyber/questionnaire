"""Checks on the answer key and the grader themselves: independent of the app, internally consistent, and
strict.
"""

import ast
import copy
import json
from pathlib import Path

import grade

HERE = Path(__file__).parent
EXPECTED = json.loads((HERE / "expected.json").read_text())
SEED = json.loads((HERE.parent / "data" / "seed" / "seed.json").read_text())
ADDED = json.loads((HERE.parent / "data" / "additions" / "extended.json").read_text())


def test_the_grader_and_judge_import_nothing_from_the_application():
    for name in ("grade.py", "judge.py"):
        tree = ast.parse((HERE / name).read_text())
        modules = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        modules += [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        assert not [m for m in modules if m.split(".")[0] in ("qa", "src", "importlib")], (name, modules)
        assert "sys.path" not in (HERE / name).read_text()


def test_the_key_counts_add_up():
    sizes = {"seed": len(SEED["questions"]), "extended": len(ADDED["questions"])}
    for suite, key in grade.suites(EXPECTED):
        for step, requests in key["counts"].items():
            for request, numbers in requests.items():
                assert sum(numbers) == sizes[suite], (suite, step, request)
    assert EXPECTED["counts"]["S6"] == EXPECTED["counts"]["S5"]
    assert EXPECTED["counts"]["S9"] == EXPECTED["counts"]["S8"]


def test_the_extended_counts_match_the_rows_statuses():
    key = EXPECTED["extended"]
    statuses = [row["checks"][0]["equals"] for row in key["cases"]]
    assert key["counts"]["S1"]["R1"] == [statuses.count("answered"), statuses.count("unresolved"), 0, 0, 0]


def test_every_quote_and_authority_in_the_key_matches_the_data():
    documents = SEED["documents"] + ADDED["documents"]
    docs = {d["id"]: d for d in documents}
    passages = {p["id"]: p["text"] for d in documents for p in d["passages"]}
    replaced_by = {d["supersedes"]: d["id"] for d in documents if d["supersedes"]}
    rows = [row for _, key in grade.suites(EXPECTED) for row in key["cases"] + key["extra_rows"]]
    for row in rows:
        for gold in row.get("gold_passages", []):
            assert gold in passages and gold.split(":")[0] not in replaced_by, (row["id"], gold)
            assert gold in [s["passage_id"] for s in row["derived_from"]], (row["id"], gold)
        for source in row.get("derived_from", []):
            assert source["quote"] in passages[source["passage_id"]]
            doc, authority = docs[source["authority"]["doc_id"]], source["authority"]
            assert (authority["version"], authority["date"]) == (doc["version"], doc["date"])
            assert (authority["status"], authority["supersedes"]) == (doc["status"], doc["supersedes"])
            assert authority["superseded_by"] == replaced_by.get(doc["id"])


def test_recall_counts_gold_passages_found_first_and_after_the_models_searches():
    case = {"gold_passages": ["A:p1", "B:p1"], "checks": [{"step": "S1", "item": "R1/X1"}]}
    suggestion = {
        "retrieval": {"top_k": 5, "hits": [{"passage_id": "A:p1"}, {"passage_id": "C:p1"}]},
        "steps": [{"action": "search_passages", "new": ["B:p1"]}, {"action": "answer"}],
    }
    steps = {"S1": {"items": {"R1/X1": {"suggestion": suggestion}}}}
    found = grade.recall(case, steps)
    assert (found["at_k"], found["shown"], found["missed"]) == (0.5, 1.0, [])
    assert grade.recall({**case, "gold_passages": []}, steps)["at_k"] is None
    assert grade.recall({"checks": case["checks"]}, steps) is None


def _observed_q1(citations, replaced) -> dict:
    view = {"citations": citations, "replaced_shown": replaced}
    return {"S1": {"items": {"R1/Q1": view}, "counts": {}}}


def test_mechanical_checks_fail_on_a_planted_wrong_observation():
    passages = grade.load_passages()
    good = [{"passage_id": "EXPORT-v2:p1", "excerpt": "Free-plan users cannot export CSV.", "version": 2}]
    bad = [
        {"passage_id": "EXPORT-v1:p1", "excerpt": "CSV exports are available on every plan.", "version": 1}
    ]
    subset = {
        "step": "S1",
        "item": "R1/Q1",
        "field": "citations",
        "ids_subset_of": ["EXPORT-v2:p1"],
        "non_empty": True,
    }
    shown = {"step": "S1", "item": "R1/Q1", "field": "replaced_shown", "ids_include": ["EXPORT-v1:p1"]}
    assert grade.check_mechanical(subset, _observed_q1(good, ["EXPORT-v1:p1"]), {}, passages)[0] == "PASS"
    assert grade.check_mechanical(subset, _observed_q1(bad, []), {}, passages)[0] == "FAIL"
    assert grade.check_mechanical(shown, _observed_q1(good, []), {}, passages)[0] == "FAIL"
    dashed = [{"passage_id": "EXPORT-v2:p1", "excerpt": "Free plan users cannot export CSV."}]
    verbatim = {"step": "S1", "item": "R1/Q1", "field": "citations", "excerpts_verbatim": True}
    assert grade.check_mechanical(verbatim, _observed_q1(dashed, []), {}, passages)[0] == "FAIL"


def test_meaning_is_pending_without_sign_off_and_a_bad_judge_quote_fails():
    check = copy.deepcopy(EXPECTED["cases"][2]["meaning"][0])  # RC-3, Q1
    answer = "No, free-plan users cannot export CSV; it is for paid plans only."
    steps = {
        "S1": {"items": {"R1/Q1": {"question_text": "Can free-plan users export CSV?", "answer": answer}}}
    }
    key = grade.meaning_key(
        "Can free-plan users export CSV?", answer, check["expected_facts"], check["forbidden_claims"]
    )
    facts = [
        {"fact": f, "stated": True, "quote": "free-plan users cannot export CSV"}
        for f in check["expected_facts"]
    ]
    forbidden = [{"claim": c, "made": False, "quote": ""} for c in check["forbidden_claims"]]
    verdict = {"model": "simulated", "response": {"facts": facts, "forbidden": forbidden}}
    assert grade.check_meaning(check, steps, {}, {})[0] == "PENDING"
    assert grade.check_meaning(check, steps, {key: verdict}, {})[0] == "PENDING"
    signed = {key: {"result": "pass", "by": "author", "date": "2026-10-08"}}
    assert grade.check_meaning(check, steps, {key: verdict}, signed)[0] == "PASS"
    facts[0]["quote"] = "words the answer never used"
    assert grade.check_meaning(check, steps, {key: verdict}, {})[0] == "FAIL"
