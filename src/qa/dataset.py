"""Load the documents, questions and owners, apply change files, and report bad references (REQ-D1).

Validation never stops the batch: a bad item is reported with its ID and left out, and everything else
still loads.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from qa.authority import replaced_document_ids

ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / "data" / "seed" / "seed.json"


@dataclass(frozen=True)
class Passage:
    id: str
    doc_id: str
    text: str


@dataclass(frozen=True)
class Document:
    id: str
    version: int
    date: str
    status: str
    supersedes: str | None
    passages: tuple[Passage, ...]


@dataclass(frozen=True)
class Question:
    id: str
    topic: str
    text: str


@dataclass(frozen=True)
class Issue:
    """A data problem found while loading. Errors exclude the item; warnings only inform."""

    code: str
    item_id: str
    detail: str
    severity: str = "error"


@dataclass
class Dataset:
    documents: dict[str, Document]
    questions: list[Question]
    owners: dict[str, str]
    issues: list[Issue] = field(default_factory=list)
    changes: list[str] = field(default_factory=list)

    @property
    def replaced_ids(self) -> set[str]:
        return replaced_document_ids(self.documents)

    @property
    def passages(self) -> dict[str, Passage]:
        return {p.id: p for d in self.documents.values() for p in d.passages}

    def authoritative_passages(self) -> list[Passage]:
        """RULE-2: only passages of documents that no loaded document supersedes count as evidence."""
        replaced = self.replaced_ids
        current = [p for d in self.documents.values() if d.id not in replaced for p in d.passages]
        return sorted(current, key=lambda p: p.id)

    @property
    def current_passage_ids(self) -> set[str]:
        return {p.id for p in self.authoritative_passages()}

    def replaced_by(self, doc_id: str) -> list[Passage]:
        """Passages of every document `doc_id` replaces, down the supersedes chain (RULE-2: kept visible)."""
        passages: list[Passage] = []
        seen = {doc_id}
        target = self.documents[doc_id].supersedes
        while target in self.documents and target not in seen:
            seen.add(target)
            passages += self.documents[target].passages
            target = self.documents[target].supersedes
        return passages

    def owner(self, question: Question) -> str | None:
        """RULE-4: the owner always comes from the supplied topic mapping, never invented."""
        return self.owners.get(question.topic)


def load_dataset(seed_path: Path = SEED_PATH, change_paths: list[Path] | None = None) -> Dataset:
    """Load the seed, apply change files in order, then validate references."""
    raw = json.loads(Path(seed_path).read_text())
    issues: list[Issue] = []
    documents = _load_documents(raw["documents"], issues)
    owners = dict(raw["owners"])
    applied = []
    for path in change_paths or []:
        if _apply_change(Path(path), documents, owners, issues):
            applied.append(_display_path(Path(path)))
    questions = _load_questions(raw["questions"], owners, issues)
    _check_supersedes(documents, issues)
    return Dataset(documents, questions, owners, issues, applied)


def _load_documents(records: list[dict], issues: list[Issue]) -> dict[str, Document]:
    """Duplicate document IDs exclude every copy; duplicate passage IDs exclude the later document."""
    counts: dict[str, int] = {}
    for record in records:
        counts[record["id"]] = counts.get(record["id"], 0) + 1
    documents: dict[str, Document] = {}
    seen_passages: set[str] = set()
    for record in records:
        if counts[record["id"]] > 1:
            issues.append(Issue("duplicate_document_id", record["id"], "document ID appears more than once"))
            continue
        document = _document(record)
        clash = [p.id for p in document.passages if p.id in seen_passages]
        if clash:
            issues.append(
                Issue("duplicate_passage_id", clash[0], f"also used by another document ({document.id})")
            )
            continue
        seen_passages.update(p.id for p in document.passages)
        documents[document.id] = document
    return documents


def _document(record: dict) -> Document:
    passages = tuple(Passage(p["id"], record["id"], p["text"]) for p in record["passages"])
    return Document(
        record["id"], record["version"], record["date"], record["status"], record["supersedes"], passages
    )


def _load_questions(records: list[dict], owners: dict[str, str], issues: list[Issue]) -> list[Question]:
    ids = [r["id"] for r in records]
    questions = []
    for record in records:
        if ids.count(record["id"]) > 1:
            issues.append(Issue("duplicate_question_id", record["id"], "question ID appears more than once"))
        elif record["topic"] not in owners:
            issues.append(Issue("unmapped_topic", record["id"], f"topic {record['topic']!r} has no owner"))
        else:
            questions.append(Question(record["id"], record["topic"], record["text"]))
    return questions


def _check_supersedes(documents: dict[str, Document], issues: list[Issue]) -> None:
    """Report edges to unknown documents, and a status that disagrees with the edges (a warning only)."""
    replaced = replaced_document_ids(documents)
    for doc in documents.values():
        if doc.supersedes and doc.supersedes not in documents:
            issues.append(
                Issue("unknown_supersedes", doc.id, f"supersedes {doc.supersedes!r}, which is not loaded")
            )
        says_superseded = doc.status == "superseded"
        if says_superseded != (doc.id in replaced):
            detail = f"status is {doc.status!r}, but supersedes links decide authority"
            issues.append(Issue("status_mismatch", doc.id, detail, severity="warning"))


def _apply_change(
    path: Path, documents: dict[str, Document], owners: dict[str, str], issues: list[Issue]
) -> bool:
    """A change file replaces loaded documents by ID and/or owner entries by topic; unknown targets are
    rejected.
    """
    change = json.loads(path.read_text())
    new_docs = [_document(r) for r in change.get("documents", [])]
    unknown = [d.id for d in new_docs if d.id not in documents]
    unknown += [t for t in change.get("owners", {}) if t not in owners]
    if unknown:
        issues.append(Issue("unknown_change_target", ", ".join(unknown), f"{path.name} was not applied"))
        return False
    for doc in new_docs:
        documents[doc.id] = doc
    owners.update(change.get("owners", {}))
    return True


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.name
