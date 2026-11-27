"""Tests for the status and confidence rules (M4.4), docs/design/evidence-model.md
sections 4, 5 and 7. Every worked example in section 9 is a test here. No database."""

import pytest

from app.skills.status_rules import Link, RuleViolationError, compute, validate

CV = "cv-1"
REPO = "repo-shop-api"
REPO_2 = "repo-thesis-tools"
CERT = "cert-aws"

_n = 0


def link(
    type_: str, judgement: str, reason: str, source: str | None = CV, **location: object
) -> Link:
    global _n
    _n += 1
    return Link(
        evidence_id=f"ev-{_n}",
        source_id=source,
        type=type_,  # type: ignore[arg-type]
        judgement=judgement,  # type: ignore[arg-type]
        reason_code=reason,
        location=dict(location),
    )


def result(*links: Link) -> tuple[str, str]:
    r = compute(list(links))
    return r.status, r.confidence


# --- 9.1 Python REST API with PostgreSQL ------------------------------------------------


def test_9_1_python_is_demonstrated_high() -> None:
    assert result(
        link("repo_language", "supports", "language_share_ok", REPO, share=90.0),
        link("repo_code", "supports", "code_uses_skill", REPO),
        link("cv_skills_list", "supports", "named_in_list"),
    ) == ("demonstrated", "high")


def test_9_1_sql_is_demonstrated_high() -> None:
    assert result(
        link("repo_code", "supports", "code_uses_skill", REPO),
        link("cv_skills_list", "supports", "named_in_list"),
    ) == ("demonstrated", "high")


def test_9_1_rest_api_is_demonstrated_medium() -> None:
    assert result(
        link("repo_code", "supports", "code_uses_skill", REPO),
        link("repo_dependency", "weak", "dependency_only", REPO),
    ) == ("demonstrated", "medium")


def test_9_1_postgresql_with_only_the_dependency_is_unverified() -> None:
    assert result(link("repo_dependency", "weak", "dependency_only", REPO)) == (
        "unverified",
        "low",
    )


def test_9_1_backend_inferred_only_is_unverified_low() -> None:
    assert result(
        link("repo_code", "weak", "inferred_from_related", REPO),
        link("cv_project", "weak", "inferred_from_related"),
    ) == ("unverified", "low")


# --- 9.2 French CV, no GitHub -------------------------------------------------------------


def test_9_2_two_types_from_one_cv_are_independent() -> None:
    assert result(
        link("cv_project", "supports", "concrete_work"),
        link("cv_skills_list", "supports", "named_in_list"),
    ) == ("demonstrated", "high")


def test_9_2_one_cv_project_is_at_most_medium() -> None:
    assert result(link("cv_project", "supports", "concrete_work")) == ("demonstrated", "medium")


def test_9_2_skills_list_only_is_claimed_medium() -> None:
    assert result(link("cv_skills_list", "supports", "named_in_list")) == ("claimed", "medium")


def test_9_2_education_only_is_unverified() -> None:
    assert result(link("cv_education", "weak", "education_only")) == ("unverified", "low")


# --- 9.3 a vague mention ------------------------------------------------------------------


def test_9_3_a_vague_experience_mention_is_claimed_low() -> None:
    assert result(link("cv_experience", "weak", "vague_mention")) == ("claimed", "low")


# --- 9.4 a forked repo --------------------------------------------------------------------


def test_9_4_a_fork_adds_nothing() -> None:
    fork = link("repo_language", "weak", "forked_repo", REPO, share=80.0, is_fork=True)
    assert result(fork) == ("unverified", "low")
    assert result(fork, link("cv_skills_list", "supports", "named_in_list")) == (
        "claimed",
        "medium",
    )


# --- 9.5 certificate plus skills list -------------------------------------------------------


def test_9_5_certificate_and_list_are_claimed_high() -> None:
    assert result(
        link("certificate", "supports", "certificate_match", CERT),
        link("cv_skills_list", "supports", "named_in_list"),
    ) == ("claimed", "high")


# --- 9.6 a small language share --------------------------------------------------------------


def test_9_6_small_share_then_real_code() -> None:
    small = link("repo_language", "weak", "language_share_low", REPO_2, share=6.0)
    assert result(small) == ("unverified", "low")
    assert result(small, link("repo_code", "supports", "code_uses_skill", REPO_2)) == (
        "demonstrated",
        "medium",
    )


# --- 9.7 and 9.8 ----------------------------------------------------------------------------


def test_9_7_a_skill_the_user_added_is_claimed_medium() -> None:
    assert result(link("user_added", "supports", "added_by_user", None)) == ("claimed", "medium")


def test_9_8_no_evidence_is_unverified_low() -> None:
    r = compute([])
    assert (r.status, r.confidence) == ("unverified", "low")
    assert r.reason.code == "no_evidence"
    assert r.reason.evidence_id is None


# --- other rules ----------------------------------------------------------------------------


def test_two_code_links_in_the_same_repo_count_once() -> None:
    assert result(
        link("repo_code", "supports", "code_uses_skill", REPO),
        link("repo_code", "supports", "code_uses_skill", REPO),
    ) == ("demonstrated", "medium")


def test_an_assessment_gives_assessed() -> None:
    assert result(link("assessment", "supports", "assessment_passed", "assessment-1")) == (
        "assessed",
        "medium",
    )


def test_the_reason_points_at_the_link_that_set_the_status() -> None:
    repo_link = link("repo_language", "supports", "language_share_ok", REPO, share=90.0)
    r = compute([link("cv_skills_list", "supports", "named_in_list"), repo_link])
    assert r.reason.code == "language_share_ok"
    assert r.reason.evidence_id == repo_link.evidence_id


def test_the_reason_of_a_vague_claim_is_the_vague_mention() -> None:
    vague = link("cv_experience", "weak", "vague_mention")
    assert compute([vague]).reason.code == "vague_mention"


# --- validator (section 7) ---------------------------------------------------------------------


def violation(links: list[Link], status: str, confidence: str) -> str:
    with pytest.raises(RuleViolationError) as error:
        validate(links, status, confidence)  # type: ignore[arg-type]
    return error.value.code


def test_valid_links_pass() -> None:
    links = [link("cv_skills_list", "supports", "named_in_list")]
    validate(links, "claimed", "medium")


def test_a_skill_needs_at_least_one_link() -> None:
    assert violation([], "unverified", "low") == "no_links"


def test_supports_on_a_context_type_is_refused() -> None:
    links = [link("repo_dependency", "supports", "dependency_only", REPO)]
    assert violation(links, "unverified", "low") == "supports_on_context_type"


def test_supports_on_a_language_that_fails_the_conditions_is_refused() -> None:
    for facts in (
        {"share": 5.0, "owned": True, "is_fork": False},
        {"share": 50.0, "owned": False, "is_fork": False},
        {"share": 50.0, "owned": True, "is_fork": True},
    ):
        links = [link("repo_language", "supports", "language_share_ok", REPO, **facts)]
        assert violation(links, "demonstrated", "medium") == "repo_language_conditions"


def test_a_wrong_status_or_confidence_is_refused() -> None:
    links = [link("cv_skills_list", "supports", "named_in_list")]
    assert violation(links, "demonstrated", "medium") == "status_mismatch"
    assert violation(links, "claimed", "high") == "confidence_mismatch"


def test_assessed_is_refused_in_the_mvp() -> None:
    links = [link("assessment", "supports", "assessment_passed", "assessment-1")]
    assert violation(links, "assessed", "medium") == "assessed_not_allowed"
