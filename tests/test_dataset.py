"""REQ-D1 and RULE-2: loading keeps IDs, reports bad references without stopping, and authority comes from
supersedes.
"""

import json
import subprocess

from qa.dataset import ROOT, SEED_PATH, load_dataset

CHANGE = ROOT / "data" / "changes" / "export-v2-version-3.json"


def _seed_variant(tmp_path, edit) -> object:
    data = json.loads(SEED_PATH.read_text())
    edit(data)
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(data))
    return load_dataset(path)


def test_supplied_seed_is_unchanged_and_loads_cleanly():
    diff = subprocess.run(
        ["diff", "-rq", "starter-pack/tasks/evidence", "data/seed"], cwd=ROOT, capture_output=True
    )
    assert diff.returncode == 0, diff.stdout
    dataset = load_dataset()
    assert dataset.issues == []
    assert [q.id for q in dataset.questions] == [f"Q{n}" for n in range(1, 9)]
    assert dataset.passages["EXPORT-v2:p1"].doc_id == "EXPORT-v2"


def test_bad_references_are_reported_and_the_rest_still_loads(tmp_path):
    def break_it(data):
        data["documents"].append(dict(data["documents"][2]))  # SUPPORT-v1 twice
        data["documents"][3]["supersedes"] = "NOPE-v9"
        data["questions"][4]["topic"] = "acess"  # misspelt: no owner exists for it
        data["questions"].append(dict(data["questions"][0]))  # Q1 twice

    dataset = _seed_variant(tmp_path, break_it)
    codes = {(i.code, i.item_id) for i in dataset.issues}
    assert {("duplicate_document_id", "SUPPORT-v1"), ("unknown_supersedes", "ACCESS-v1")} <= codes
    assert {("unmapped_topic", "Q5"), ("duplicate_question_id", "Q1")} <= codes
    assert "SUPPORT-v1" not in dataset.documents and "EXPORT-v2" in dataset.documents
    assert [q.id for q in dataset.questions] == ["Q2", "Q3", "Q4", "Q6", "Q7", "Q8"]


def test_only_a_supersedes_link_replaces_a_document(tmp_path):
    assert load_dataset().replaced_ids == {"EXPORT-v1"}

    def drop_link(data):  # EXPORT-v2 stays newer and higher-versioned, but no longer supersedes EXPORT-v1
        data["documents"][1]["supersedes"] = None

    dataset = _seed_variant(tmp_path, drop_link)
    assert dataset.replaced_ids == set()
    assert {p.id for p in dataset.authoritative_passages()} >= {"EXPORT-v1:p1", "EXPORT-v2:p1"}
    assert [(i.code, i.item_id, i.severity) for i in dataset.issues] == [
        ("status_mismatch", "EXPORT-v1", "warning")
    ]


def test_replaced_text_is_shown_down_the_whole_supersedes_chain(tmp_path):
    def add_v3(data):  # EXPORT-v3 supersedes EXPORT-v2, which supersedes EXPORT-v1
        data["documents"].append(
            {
                **data["documents"][1],
                "id": "EXPORT-v3",
                "supersedes": "EXPORT-v2",
                "passages": [{"id": "EXPORT-v3:p1", "text": "CSV exports are available on paid plans only."}],
            }
        )

    dataset = _seed_variant(tmp_path, add_v3)
    assert [p.id for p in dataset.replaced_by("EXPORT-v3")] == ["EXPORT-v2:p1", "EXPORT-v1:p1"]
    assert dataset.replaced_ids == {"EXPORT-v1", "EXPORT-v2"}


def test_a_change_file_replaces_a_document_by_id():
    dataset = load_dataset(change_paths=[CHANGE])
    assert dataset.documents["EXPORT-v2"].version == 3
    assert dataset.changes == ["data/changes/export-v2-version-3.json"]
    assert dataset.issues == []
