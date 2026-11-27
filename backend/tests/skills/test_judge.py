"""Tests for System A's judgement of one evidence link (M4.4), evidence model section 3.2:
`supports` or `weak`, with a reason code. Quotes are made up, in English and French."""

import pytest

from app.skills.judge import judge


def verdict(type_: str, quote: str = "", **location: object) -> tuple[str, str]:
    j = judge(type_, quote, dict(location))  # type: ignore[arg-type]
    return j.judgement, j.reason_code


# --- claims -------------------------------------------------------------------------------


def test_a_skills_list_supports() -> None:
    assert verdict("cv_skills_list", "Skills: Python, SQL") == ("supports", "named_in_list")
    assert verdict("cv_skills_list", "Compétences : notions de Docker") == (
        "supports",
        "named_in_list",
    )


def test_a_summary_supports() -> None:
    assert verdict("cv_summary", "Data analyst using SQL every day.") == (
        "supports",
        "named_in_summary",
    )


@pytest.mark.parametrize(
    "quote",
    [
        "Interested in Kubernetes.",
        "I would like to learn Rust.",
        "Computer science student looking for a backend internship.",
        "Étudiante à la recherche d'un stage en développement web.",
        "Je souhaite apprendre Kubernetes.",
        "Intéressée par la cybersécurité.",
    ],
)
def test_wanting_to_learn_is_weak(quote: str) -> None:
    assert verdict("cv_summary", quote) == ("weak", "wants_to_learn")


def test_machine_learning_is_not_wanting_to_learn() -> None:
    assert verdict("cv_skills_list", "Machine learning, deep learning") == (
        "supports",
        "named_in_list",
    )


# --- work described on a CV or in the app -----------------------------------------------------


@pytest.mark.parametrize(
    "quote",
    [
        "Built a REST API with FastAPI.",
        "Intern at Example Startup, where I wrote REST endpoints for the team.",
        "Project: a library management app built with Django.",
        "Développement d'une application de gestion de bibliothèque avec Django.",
        "Stagiaire chez Exemple SARL, où j'ai écrit des API pour l'équipe.",
        "Mise en place d'un pipeline CI/CD avec GitHub Actions.",
    ],
)
@pytest.mark.parametrize("type_", ["cv_project", "cv_experience", "manual_project"])
def test_concrete_work_supports(type_: str, quote: str) -> None:
    assert verdict(type_, quote) == ("supports", "concrete_work")


@pytest.mark.parametrize(
    "quote",
    [
        "Familiar with Docker.",
        "Exposure to Agile methods.",
        "Technologies: React, Node.js",
        "Environnement technique : Java, Spring Boot",
        "Notions de Docker.",
        "Une application de gestion de bibliothèque avec une base de données.",
        "Built a website. Tech stack: React",
    ],
)
def test_vague_or_passive_work_is_weak(quote: str) -> None:
    assert verdict("cv_project", quote) == ("weak", "vague_mention")


# --- context types -----------------------------------------------------------------------


def test_context_types_are_always_weak() -> None:
    assert verdict("cv_education", "Licence Informatique, module Bases de données") == (
        "weak",
        "education_only",
    )
    assert verdict("repo_dependency", "fastapi==0.110") == ("weak", "dependency_only")
    assert verdict("repo_readme", "Built with FastAPI.") == ("weak", "readme_only")


# --- repos ----------------------------------------------------------------------------------


def test_a_language_supports_only_when_all_three_conditions_hold() -> None:
    ok = {"share": 90.0, "owned": True, "is_fork": False}
    assert verdict("repo_language", "Python 90%", **ok) == ("supports", "language_share_ok")
    assert verdict("repo_language", "Python 10%", **(ok | {"share": 10.0})) == (
        "supports",
        "language_share_ok",
    )
    assert verdict("repo_language", "Shell 6%", **(ok | {"share": 6.0})) == (
        "weak",
        "language_share_low",
    )
    assert verdict("repo_language", "Python 90%", **(ok | {"owned": False})) == (
        "weak",
        "not_owned_repo",
    )
    assert verdict("repo_language", "JavaScript 80%", **(ok | {"is_fork": True})) == (
        "weak",
        "forked_repo",
    )


def test_a_language_without_its_facts_is_weak() -> None:
    assert verdict("repo_language", "Python 90%") == ("weak", "language_share_low")


def test_repo_code_supports_unless_forked_or_not_owned() -> None:
    assert verdict("repo_code", "def create_order()", owned=True, is_fork=False) == (
        "supports",
        "code_uses_skill",
    )
    assert verdict("repo_code", "x", owned=True, is_fork=True) == ("weak", "forked_repo")
    assert verdict("repo_code", "x", owned=False, is_fork=False) == ("weak", "not_owned_repo")


# --- the rest -------------------------------------------------------------------------------


def test_other_types() -> None:
    assert verdict("certificate", "AWS Certified Cloud Practitioner") == (
        "supports",
        "certificate_match",
    )
    assert verdict("user_added") == ("supports", "added_by_user")
    assert verdict("assessment", passed=True) == ("supports", "assessment_passed")
    assert verdict("assessment", passed=False) == ("weak", "assessment_failed")
