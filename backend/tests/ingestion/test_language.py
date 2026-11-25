"""Tests for guessing a CV's language (M3.5): en, fr, ar, or `other` when unsure."""

import pytest

from app.ingestion.language import detect_language
from tests.fixtures.cv.make_cv_fixtures import CV_LINES


@pytest.mark.parametrize("language", ["en", "fr", "ar"])
def test_detects_the_language_of_each_test_cv(language: str) -> None:
    assert detect_language("\n".join(CV_LINES[language])) == language


def test_arabic_cv_full_of_english_tool_names_is_still_arabic() -> None:
    text = (
        "المهارات: Python و Django و PostgreSQL و Docker و Git و React و TypeScript.\n"
        "طورت تطبيقا للويب باستخدام FastAPI مع اختبارات pytest."
    )

    assert detect_language(text) == "ar"


def test_english_cv_with_a_name_in_arabic_is_english() -> None:
    text = "سارة مثال\nSkills: Python and SQL. I built a web app for the library of my school."

    assert detect_language(text) == "en"


def test_french_cv_without_accents_is_french() -> None:
    text = "Stage de developpement web pour une entreprise avec les equipes de la banque."

    assert detect_language(text) == "fr"


@pytest.mark.parametrize(
    "text",
    [
        "",
        "Python, SQL, Docker, Git, React",  # a bare list of tools: no sentence to go on
        "2021 - 2024 +212 600 000 000",
        "Ich habe eine Webanwendung mit der Datenbank und dem Team entwickelt.",  # German
    ],
    ids=["empty", "tools-only", "numbers", "german"],
)
def test_unsure_or_another_language_is_other(text: str) -> None:
    assert detect_language(text) == "other"
