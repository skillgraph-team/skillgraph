"""Tests for the skill index (M4.2): any id, name or alias, in any spelling, gives back
the skill id. Built from the CSV files, so no database is needed."""

import pytest

from app.skills.index import AMBIGUOUS, SkillIndex, SkillIndexCollisionError
from app.skills.taxonomy import AliasRow, SkillRow


@pytest.fixture(scope="module")
def index() -> SkillIndex:
    return SkillIndex.from_csv()


@pytest.mark.parametrize(
    ("text", "skill_id"),
    [
        ("PostgreSQL", "postgresql"),
        ("postgres", "postgresql"),
        ("Postgres", "postgresql"),
        ("postgresql", "postgresql"),
        ("JS", "javascript"),
        ("Node.js", "node.js"),
        ("nodejs", "node.js"),
        ("C++", "c++"),
        ("c#", "c#"),
        (".NET", "dotnet"),
        ("Front-End", "frontend-development"),
        ("REST APIs", "rest-api"),
    ],
)
def test_english_spellings(index: SkillIndex, text: str, skill_id: str) -> None:
    assert index.resolve(text) == skill_id


@pytest.mark.parametrize(
    ("text", "skill_id"),
    [
        ("Bases de données", "databases"),
        ("base de donnees", "databases"),
        ("BDD", "databases"),
        ("Développement web", "web-development"),
        ("developpement-web", "web-development"),
        ("dev web", "web-development"),
        ("Apprentissage automatique", "machine-learning"),
        ("Programmation orientée objet", "oop"),
        ("Anglais", "english"),
    ],
)
def test_french_spellings(index: SkillIndex, text: str, skill_id: str) -> None:
    assert index.resolve(text) == skill_id


@pytest.mark.parametrize(
    ("text", "skill_id"),
    [
        ("قواعد البيانات", "databases"),
        ("قَوَاعِد البَيَانَات", "databases"),
        ("تعلم الآلة", "machine-learning"),
    ],
)
def test_arabic_display_names(index: SkillIndex, text: str, skill_id: str) -> None:
    """Arabic CVs aren't read (D-030), but the Arabic names still resolve, so a
    search box in the Arabic interface can use the same index."""
    assert index.resolve(text) == skill_id


def test_unknown_text_gives_nothing(index: SkillIndex) -> None:
    assert index.resolve("Underwater basket weaving") is None
    assert index.resolve("") is None


def test_every_ambiguous_word_is_a_real_key(index: SkillIndex) -> None:
    """A typo in AMBIGUOUS would silently do nothing."""
    assert sorted(word for word in AMBIGUOUS if index.resolve(word) is None) == []


def skill(skill_id: str, name: str) -> SkillRow:
    return SkillRow(id=skill_id, name_en=name, name_fr=name, name_ar=name, category="tool")


def test_two_skills_with_the_same_key_are_refused() -> None:
    skills = [skill("vue", "Vue.js"), skill("vue-js", "Vue JS")]
    with pytest.raises(SkillIndexCollisionError):
        SkillIndex.from_rows(skills, [])


def test_an_alias_clashing_with_another_skill_is_refused() -> None:
    skills = [skill("java", "Java"), skill("javascript", "JavaScript")]
    with pytest.raises(SkillIndexCollisionError):
        SkillIndex.from_rows(skills, [AliasRow(alias="java", skill_id="javascript")])
