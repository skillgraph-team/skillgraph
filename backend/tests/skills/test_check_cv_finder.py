"""Tests for the CV finder check script (M4.2): it compares the skills found in a CV
file with a list of expected skill ids and prints how many were found and how many
were wrong. Uses the made-up CVs in tests/fixtures/cv/; no database."""

from pathlib import Path

import pytest

from app.skills.check_cv_finder import check, main

CV_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "cv"

# What a person would label in the made-up CVs (tests/fixtures/cv/make_cv_fixtures.py).
EXPECTED = {
    "cv_en.pdf": {
        "backend-development",
        "python",
        "fastapi",
        "postgresql",
        "docker",
        "rest-api",
        "django",
        "pytest",
    },
    "cv_fr.docx": {"web-development", "python", "django", "postgresql", "api-design", "databases"},
}


@pytest.mark.parametrize("file_name", sorted(EXPECTED))
def test_the_finder_gets_every_expected_skill_in_the_fixture_cvs(file_name: str) -> None:
    result = check(CV_DIR / file_name, EXPECTED[file_name])
    assert result.missed == set()
    assert result.wrong == set()
    assert result.found == EXPECTED[file_name]


def test_missed_and_wrong_skills_are_reported() -> None:
    result = check(CV_DIR / "cv_en.pdf", {"python", "kubernetes"})
    assert result.missed == {"kubernetes"}
    assert "docker" in result.wrong
    assert result.found == {"python"}


def test_the_script_prints_the_counts(capsys: pytest.CaptureFixture[str]) -> None:
    main([str(CV_DIR / "cv_en.pdf"), "python,kubernetes"])
    out = capsys.readouterr().out
    assert "expected 2, found 1, missed 1, wrong 7" in out
    assert "missed: kubernetes" in out
