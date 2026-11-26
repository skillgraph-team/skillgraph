"""Checks on the learning resources list (M4.8): the only place recommendations may take
links from. Right columns, known values, links to real skills, no duplicates, and at
least two free resources for every skill. Reads the CSV with the standard csv module.
Whether each link still opens is checked separately (see the README in the data folder).
"""

import csv
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "app" / "skills" / "data"

TYPES = {"course", "docs", "tutorial", "project_idea"}
LANGUAGES = {"en", "fr", "ar"}
MIN_FREE_PER_SKILL = 2


def read(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_file_has_the_expected_columns() -> None:
    with (DATA / "resources.csv").open(encoding="utf-8", newline="") as f:
        assert next(csv.reader(f)) == ["skill_id", "title", "url", "type", "free", "language"]


def test_values_are_known() -> None:
    rows = read("resources.csv")
    assert [r for r in rows if r["type"] not in TYPES] == []
    assert [r for r in rows if r["free"] not in {"yes", "no"}] == []
    assert [r for r in rows if r["language"] not in LANGUAGES] == []
    assert [r for r in rows if not r["title"].strip()] == []


def test_links_are_https_without_spaces() -> None:
    bad = [
        r["url"]
        for r in read("resources.csv")
        if not r["url"].startswith("https://") or any(c.isspace() for c in r["url"])
    ]
    assert bad == []


def test_every_resource_points_at_a_skill() -> None:
    ids = {r["id"] for r in read("skills.csv")}
    assert [r for r in read("resources.csv") if r["skill_id"] not in ids] == []


def test_no_resource_is_listed_twice_for_the_same_skill() -> None:
    pairs = Counter((r["skill_id"], r["url"]) for r in read("resources.csv"))
    assert [p for p, n in pairs.items() if n > 1] == []


def test_every_skill_has_at_least_two_free_resources() -> None:
    free = Counter(r["skill_id"] for r in read("resources.csv") if r["free"] == "yes")
    missing = sorted(r["id"] for r in read("skills.csv") if free[r["id"]] < MIN_FREE_PER_SKILL)
    assert missing == []
