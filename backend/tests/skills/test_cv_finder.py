"""Tests for finding skills in CV text (M4.2): which CV section each sentence is in
(that decides the evidence type), which skills it names, and the exact quote. No
database: the skill index is built from the CSV files. All CV text is made up.
"""

import pytest

from app.skills.cv_finder import find_in_cv
from app.skills.findings import Finding
from app.skills.index import SkillIndex


@pytest.fixture(scope="module")
def index() -> SkillIndex:
    return SkillIndex.from_csv()


def by_type(findings: list[Finding]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for finding in findings:
        out.setdefault(finding.type, []).extend(finding.skill_ids)
    return out


EN_CV = """Sam Example
Computer science student looking for a backend internship.
Skills: Python, FastAPI, PostgreSQL and Docker.
Experience: intern at Example Startup, where I wrote REST endpoints for the team.
Project: a library management app built with Django and tested with pytest."""

FR_CV = """Camille Exemple
Étudiante en informatique à la recherche d'un stage en développement web.
Compétences : Python, Django, PostgreSQL et le développement de tests.
Expérience : stagiaire chez Exemple SARL, où j'ai écrit des API pour l'équipe.
Projet : une application de gestion de bibliothèque avec une base de données."""


def test_english_cv_with_inline_headings(index: SkillIndex) -> None:
    found = by_type(find_in_cv(EN_CV, index, cv_language="en"))
    assert found == {
        "cv_summary": ["backend-development"],
        "cv_skills_list": ["python", "fastapi", "postgresql", "docker"],
        "cv_experience": ["rest-api"],
        "cv_project": ["django", "pytest"],
    }


def test_french_cv_with_inline_headings(index: SkillIndex) -> None:
    found = by_type(find_in_cv(FR_CV, index, cv_language="fr"))
    assert found == {
        "cv_summary": ["web-development"],
        "cv_skills_list": ["python", "django", "postgresql"],
        "cv_experience": ["api-design"],
        "cv_project": ["databases"],
    }


def test_a_heading_on_its_own_line_applies_to_the_lines_below() -> None:
    cv = """PROFIL
Développeuse passionnée.
COMPÉTENCES TECHNIQUES
• Java, Spring Boot
• Git
Expériences professionnelles
– Stage : développement d'une API REST en Java avec Spring Boot.
FORMATION
Licence Informatique – module Bases de données
Certifications
AWS Certified Cloud Practitioner
Centres d'intérêt
Photographie, Python le serpent"""
    found = by_type(find_in_cv(cv, SkillIndex.from_csv(), cv_language="fr"))
    assert found == {
        "cv_skills_list": ["java", "spring-boot", "git"],
        "cv_experience": ["rest-api", "java", "spring-boot"],
        "cv_education": ["databases"],
        "certificate": ["aws", "cloud-computing"],
    }


def test_each_finding_keeps_the_exact_sentence_and_where_it_is(index: SkillIndex) -> None:
    findings = find_in_cv(EN_CV, index, cv_language="en")
    project = next(f for f in findings if f.type == "cv_project")
    assert project.quote == (
        "Project: a library management app built with Django and tested with pytest."
    )
    assert project.location == {"section": "Project", "line": 5}
    assert project.language == "en"


def test_one_sentence_with_several_skills_is_one_finding_without_repeats(
    index: SkillIndex,
) -> None:
    cv = "Projects\nBuilt a REST API with FastAPI and PostgreSQL, and tested the FastAPI app."
    findings = find_in_cv(cv, index, cv_language="en")
    assert [f.skill_ids for f in findings] == [["rest-api", "fastapi", "postgresql"]]


def test_longest_name_wins(index: SkillIndex) -> None:
    cv = "Skills: Spring Boot, React Native, Microsoft SQL Server"
    assert by_type(find_in_cv(cv, index, cv_language="en")) == {
        "cv_skills_list": ["spring-boot", "react-native", "sql-server"]
    }


def test_short_ambiguous_words_count_in_a_skills_list(index: SkillIndex) -> None:
    cv = "Languages: C, R, Go, Rust"
    assert by_type(find_in_cv(cv, index, cv_language="en")) == {
        "cv_skills_list": ["c", "r", "go", "rust"]
    }


def test_short_ambiguous_words_in_prose_only_count_when_capitalized(
    index: SkillIndex,
) -> None:
    cv = """Experience
I go to meetups and rest on weekends; c'est la vie, j'ai un tableau de bord.
Wrote a small HTTP server in C and a CLI in Go."""
    findings = find_in_cv(cv, index, cv_language="en")
    assert [f.skill_ids for f in findings] == [["c", "go"]]
    assert findings[0].location["line"] == 3


def test_text_before_any_heading_counts_as_summary(index: SkillIndex) -> None:
    findings = find_in_cv("Data analysis and SQL enthusiast.", index, cv_language="en")
    assert [(f.type, f.skill_ids) for f in findings] == [("cv_summary", ["data-analysis", "sql"])]


def test_long_lines_are_split_into_sentences(index: SkillIndex) -> None:
    cv = (
        "Experience\nWorked on the payments team for six months. "
        "Wrote integration tests in Python. Organised the office party."
    )
    findings = find_in_cv(cv, index, cv_language="en")
    assert [f.quote for f in findings] == ["Wrote integration tests in Python."]


def test_quotes_longer_than_300_characters_are_cut_at_a_word(index: SkillIndex) -> None:
    filler = "very " * 80
    cv = f"Projects\nA {filler}long description that finally mentions Kubernetes at the end"
    [finding] = find_in_cv(cv, index, cv_language="en")
    assert len(finding.quote) <= 300
    assert "Kubernetes" in finding.quote
    assert finding.quote.startswith("…")
    assert finding.quote.removeprefix("…") in cv


def test_quote_language_falls_back_to_the_cv_language(index: SkillIndex) -> None:
    """A bare list of tools has no English or French words in it."""
    [finding] = find_in_cv("Compétences\nPython, SQL", index, cv_language="fr")
    assert finding.language == "fr"


def test_nothing_found_gives_an_empty_list(index: SkillIndex) -> None:
    assert find_in_cv("Sam Example\nHobbies\nHiking", index, cv_language="en") == []
    assert find_in_cv("", index, cv_language="en") == []
