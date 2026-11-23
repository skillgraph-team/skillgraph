"""Tests for the database rules in app/db/models: the database itself rejects bad rows.

Each test tries to save one row that breaks a rule and expects PostgreSQL to refuse
it. The rules mirror docs/design/evidence-model.md and docs/design/schema.md.
"""

from collections.abc import Callable
from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import SkillRelation
from tests.db import factories as f


def assert_rejected(session: Session, make: Callable[[], Any]) -> None:
    """`make` must fail with a database error; the rest of the test can go on."""
    with pytest.raises(IntegrityError), session.begin_nested():
        make()


# --- users -------------------------------------------------------------------


def test_user_defaults_to_english(db_session: Session) -> None:
    user = f.make_user(db_session)
    db_session.refresh(user)

    assert user.preferred_language == "en"


def test_user_language_must_be_en_fr_or_ar(db_session: Session) -> None:
    assert_rejected(db_session, lambda: f.make_user(db_session, preferred_language="de"))


def test_user_email_is_unique(db_session: Session) -> None:
    f.make_user(db_session, email="same@example.com")

    assert_rejected(db_session, lambda: f.make_user(db_session, email="same@example.com"))


def test_user_email_must_be_lowercase(db_session: Session) -> None:
    assert_rejected(db_session, lambda: f.make_user(db_session, email="Mixed@Example.com"))


def test_one_profile_per_user(db_session: Session) -> None:
    user = f.make_user(db_session)
    f.make_profile(db_session, user)

    assert_rejected(db_session, lambda: f.make_profile(db_session, user))


# --- sources and evidence ----------------------------------------------------


def test_source_kind_must_be_known(db_session: Session) -> None:
    user = f.make_user(db_session)

    assert_rejected(db_session, lambda: f.make_source(db_session, user, kind="tweet"))


def test_manual_project_source_must_point_to_its_project(db_session: Session) -> None:
    user = f.make_user(db_session)
    project = f.make_manual_project(db_session, f.make_profile(db_session, user))

    f.make_source(db_session, user, kind="manual_project", manual_project_id=project.id)
    assert_rejected(db_session, lambda: f.make_source(db_session, user, kind="manual_project"))
    assert_rejected(
        db_session,
        lambda: f.make_source(db_session, user, kind="cv", manual_project_id=project.id),
    )


def test_evidence_type_must_be_one_of_the_evidence_model_types(db_session: Session) -> None:
    user = f.make_user(db_session)
    source = f.make_source(db_session, user)

    assert_rejected(db_session, lambda: f.make_evidence(db_session, user, source, type="rumour"))


def test_evidence_needs_a_source_unless_user_added(db_session: Session) -> None:
    user = f.make_user(db_session)

    f.make_evidence(db_session, user, None, type="user_added", quote="Figma")
    assert_rejected(db_session, lambda: f.make_evidence(db_session, user, None))


def test_evidence_quote_is_at_most_300_characters(db_session: Session) -> None:
    user = f.make_user(db_session)
    source = f.make_source(db_session, user)

    f.make_evidence(db_session, user, source, quote="x" * 300)
    assert_rejected(db_session, lambda: f.make_evidence(db_session, user, source, quote="x" * 301))


def test_evidence_language_must_be_known(db_session: Session) -> None:
    user = f.make_user(db_session)
    source = f.make_source(db_session, user)

    f.make_evidence(db_session, user, source, language="other")
    assert_rejected(db_session, lambda: f.make_evidence(db_session, user, source, language="es"))


# --- skills ------------------------------------------------------------------


def test_skill_id_is_a_lowercase_slug(db_session: Session) -> None:
    f.make_skill(db_session, id="node.js")
    f.make_skill(db_session, id="c++")

    assert_rejected(db_session, lambda: f.make_skill(db_session, id="Node JS"))


def test_skill_cannot_be_its_own_parent(db_session: Session) -> None:
    skill = f.make_skill(db_session)

    def make() -> None:
        db_session.add(SkillRelation(child_id=skill.id, parent_id=skill.id))
        db_session.flush()

    assert_rejected(db_session, make)


# --- user skills and their evidence links ------------------------------------


def test_user_skill_status_and_confidence_must_be_known(db_session: Session) -> None:
    user = f.make_user(db_session)

    assert_rejected(
        db_session,
        lambda: f.make_user_skill(db_session, user, f.make_skill(db_session), status="expert"),
    )
    assert_rejected(
        db_session,
        lambda: f.make_user_skill(db_session, user, f.make_skill(db_session), confidence="0.9"),
    )


def test_unverified_is_always_low_confidence(db_session: Session) -> None:
    user = f.make_user(db_session)

    f.make_user_skill(
        db_session, user, f.make_skill(db_session), status="unverified", confidence="low"
    )
    assert_rejected(
        db_session,
        lambda: f.make_user_skill(
            db_session, user, f.make_skill(db_session), status="unverified", confidence="medium"
        ),
    )


def test_a_skill_appears_once_per_user(db_session: Session) -> None:
    user = f.make_user(db_session)
    skill = f.make_skill(db_session)
    f.make_user_skill(db_session, user, skill)

    assert_rejected(db_session, lambda: f.make_user_skill(db_session, user, skill))


def test_link_judgement_must_be_supports_or_weak(db_session: Session) -> None:
    user = f.make_user(db_session)
    user_skill = f.make_user_skill(db_session, user, f.make_skill(db_session))
    evidence = f.make_evidence(db_session, user, f.make_source(db_session, user))

    assert_rejected(
        db_session, lambda: f.make_link(db_session, user_skill, evidence, judgement="strong")
    )


def test_a_skill_cannot_cite_another_users_evidence(db_session: Session) -> None:
    alice = f.make_user(db_session)
    bob = f.make_user(db_session)
    alice_skill = f.make_user_skill(db_session, alice, f.make_skill(db_session))
    bobs_evidence = f.make_evidence(db_session, bob, f.make_source(db_session, bob))

    # Whichever user the link claims to belong to, one side doesn't match.
    assert_rejected(db_session, lambda: f.make_link(db_session, alice_skill, bobs_evidence))
    assert_rejected(
        db_session,
        lambda: f.make_link(db_session, alice_skill, bobs_evidence, user_id=bob.id),
    )


# --- opportunities, matches, runs --------------------------------------------


def test_requirement_importance_must_be_required_or_nice_to_have(db_session: Session) -> None:
    opportunity = f.make_opportunity(db_session)

    assert_rejected(
        db_session, lambda: f.make_requirement(db_session, opportunity, importance="maybe")
    )


def test_match_score_is_between_0_and_1(db_session: Session) -> None:
    user = f.make_user(db_session)

    f.make_match(db_session, user, f.make_opportunity(db_session), score=0.75)
    assert_rejected(
        db_session,
        lambda: f.make_match(db_session, user, f.make_opportunity(db_session), score=1.5),
    )


def test_one_match_per_user_and_opportunity(db_session: Session) -> None:
    user = f.make_user(db_session)
    opportunity = f.make_opportunity(db_session)
    f.make_match(db_session, user, opportunity)

    assert_rejected(db_session, lambda: f.make_match(db_session, user, opportunity))


def test_run_system_and_status_must_be_known(db_session: Session) -> None:
    user = f.make_user(db_session)

    assert_rejected(db_session, lambda: f.make_run(db_session, user, system="three_agents"))
    assert_rejected(db_session, lambda: f.make_run(db_session, user, status="sleeping"))


def test_message_order_is_unique_within_a_run(db_session: Session) -> None:
    run = f.make_run(db_session, None)
    f.make_message(db_session, run, sequence=1)

    assert_rejected(db_session, lambda: f.make_message(db_session, run, sequence=1))
