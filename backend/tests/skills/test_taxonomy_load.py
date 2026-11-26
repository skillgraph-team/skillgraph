"""Tests for loading the skill list CSVs into the database (M4.2). Needs the test
database (`docker compose up -d db`)."""

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Skill, SkillAlias, SkillRelation
from app.skills.index import load_index
from app.skills.taxonomy import SkillInUseError, load_taxonomy, read_taxonomy
from tests.db.factories import make_skill, make_user, make_user_skill


def count(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def test_loading_puts_every_row_in_the_database(db_session: Session) -> None:
    data = read_taxonomy()
    counts = load_taxonomy(db_session)
    assert counts.skills == len(data.skills) == count(db_session, Skill)
    assert counts.aliases == len(data.aliases) == count(db_session, SkillAlias)
    assert counts.relations == len(data.relations) == count(db_session, SkillRelation)
    postgres = db_session.get(Skill, "postgresql")
    assert postgres is not None
    assert (postgres.name_en, postgres.name_fr, postgres.category) == (
        "PostgreSQL",
        "PostgreSQL",
        "database",
    )


def test_loading_twice_gives_the_same_rows(db_session: Session) -> None:
    load_taxonomy(db_session)
    first = (count(db_session, Skill), count(db_session, SkillAlias))
    load_taxonomy(db_session)
    assert (count(db_session, Skill), count(db_session, SkillAlias)) == first


def test_loading_again_restores_edited_rows(db_session: Session) -> None:
    load_taxonomy(db_session)
    skill = db_session.get(Skill, "python")
    assert skill is not None
    skill.name_fr = "changed by hand"
    db_session.flush()
    load_taxonomy(db_session)
    db_session.refresh(skill)
    assert skill.name_fr == "Python"


def test_a_skill_no_longer_in_the_csv_is_removed(db_session: Session) -> None:
    make_skill(db_session, id="old-skill")
    load_taxonomy(db_session)
    assert db_session.get(Skill, "old-skill") is None


def test_a_skill_still_used_by_a_profile_is_not_removed(db_session: Session) -> None:
    old = make_skill(db_session, id="old-skill")
    make_user_skill(db_session, make_user(db_session), old)
    with pytest.raises(SkillInUseError) as error:
        load_taxonomy(db_session)
    assert error.value.skill_ids == ["old-skill"]
    assert db_session.get(Skill, "old-skill") is not None


def test_the_index_can_be_built_from_the_database(db_session: Session) -> None:
    load_taxonomy(db_session)
    index = load_index(db_session)
    assert index.resolve("Postgres") == "postgresql"
    assert index.resolve("bases de données") == "databases"
