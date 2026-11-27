"""Property-based tests for the status and confidence rules (M4.4): rules that must hold
for any list of links, checked on many generated lists (Hypothesis), not a few examples.
See GLOSSARY: property-based test."""

from hypothesis import given
from hypothesis import strategies as st

from app.db.values import EvidenceType, Judgement, values
from app.skills.status_rules import CONFIDENCE_ORDER, STATUS_ORDER, Link, compute

REASONS = ["concrete_work", "named_in_list", "vague_mention", "inferred_from_related"]

links = st.builds(
    Link,
    evidence_id=st.uuids().map(str),
    source_id=st.sampled_from(["cv", "repo-a", "repo-b", None]),
    type=st.sampled_from(values(EvidenceType)),
    judgement=st.sampled_from(values(Judgement)),
    reason_code=st.sampled_from(REASONS),
    location=st.just({}),
)
link_lists = st.lists(links, max_size=8)


def supporting(link: Link) -> Link:
    return link.model_copy(update={"judgement": "supports", "reason_code": "named_in_list"})


def weak(link: Link) -> Link:
    return link.model_copy(update={"judgement": "weak"})


@given(link_lists, links)
def test_more_supporting_evidence_never_lowers_confidence_or_status(
    existing: list[Link], extra: Link
) -> None:
    before = compute(existing)
    after = compute([*existing, supporting(extra)])
    assert CONFIDENCE_ORDER[after.confidence] >= CONFIDENCE_ORDER[before.confidence]
    assert STATUS_ORDER[after.status] >= STATUS_ORDER[before.status]


@given(link_lists, links)
def test_weak_evidence_never_changes_confidence(existing: list[Link], extra: Link) -> None:
    assert compute([*existing, weak(extra)]).confidence == compute(existing).confidence


@given(link_lists)
def test_only_an_assessment_gives_assessed(links_: list[Link]) -> None:
    has_passed_assessment = any(
        link.type == "assessment" and link.judgement == "supports" for link in links_
    )
    assert (compute(links_).status == "assessed") == has_passed_assessment


@given(link_lists)
def test_unverified_is_always_low(links_: list[Link]) -> None:
    result = compute(links_)
    if result.status == "unverified":
        assert result.confidence == "low"


@given(link_lists, st.randoms())
def test_the_order_of_links_doesnt_matter(links_: list[Link], random) -> None:  # type: ignore[no-untyped-def]
    shuffled = list(links_)
    random.shuffle(shuffled)
    a, b = compute(links_), compute(shuffled)
    assert (a.status, a.confidence) == (b.status, b.confidence)


def test_no_evidence_is_unverified_low() -> None:
    result = compute([])
    assert (result.status, result.confidence) == ("unverified", "low")
