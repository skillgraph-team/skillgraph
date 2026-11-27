"""Tests for finding skills in a project the user typed in (M4.10). No database."""

import pytest

from app.skills.index import SkillIndex
from app.skills.project_finder import find_in_project


@pytest.fixture(scope="module")
def index() -> SkillIndex:
    return SkillIndex.from_csv()


def test_title_and_description_sentences_become_manual_project_findings(
    index: SkillIndex,
) -> None:
    findings = find_in_project(
        "Library app in Django",
        "Built a library app with PostgreSQL. Deployed it on Heroku.\nIt was fun.",
        index,
        project_id="p-1",
    )
    assert [(f.type, f.skill_ids, f.location, f.quote) for f in findings] == [
        (
            "manual_project",
            ["django"],
            {"project_id": "p-1", "field": "title", "line": 1},
            "Library app in Django",
        ),
        (
            "manual_project",
            ["postgresql"],
            {"project_id": "p-1", "field": "description", "line": 1},
            "Built a library app with PostgreSQL.",
        ),
        (
            "manual_project",
            ["heroku"],
            {"project_id": "p-1", "field": "description", "line": 1},
            "Deployed it on Heroku.",
        ),
    ]
    assert findings[1].language == "en"


def test_a_french_project(index: SkillIndex) -> None:
    [finding] = find_in_project(
        "Projet de fin d'études",
        "Développement d'une application avec React et Node.js pour l'association.",
        index,
        project_id="p-2",
    )
    assert finding.skill_ids == ["react", "node.js"]
    assert finding.language == "fr"


def test_a_project_naming_no_skill_gives_nothing(index: SkillIndex) -> None:
    assert find_in_project("Garden", "I grew tomatoes.", index, project_id="p-3") == []
