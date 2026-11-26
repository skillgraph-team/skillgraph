"""Checks on the two small mapping files the repo finder uses (M4.3): package names and
GitHub language names that differ from any skill name or alias."""

import csv
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "app" / "skills" / "data"


def read(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def skill_ids() -> set[str]:
    return {row["id"] for row in read("skills.csv")}


def test_packages_file() -> None:
    rows = read("packages.csv")
    assert list(rows[0]) == ["package", "skill_id"]
    assert [r for r in rows if r["skill_id"] not in skill_ids()] == []
    names = Counter(r["package"] for r in rows)
    assert [name for name, n in names.items() if n > 1] == []
    assert [r["package"] for r in rows if r["package"] != r["package"].lower()] == []
    # A trailing * is the only wildcard, e.g. spring-boot-starter*.
    assert [r["package"] for r in rows if "*" in r["package"][:-1]] == []


def test_github_languages_file() -> None:
    rows = read("github_languages.csv")
    assert list(rows[0]) == ["language", "skill_id"]
    assert [r for r in rows if r["skill_id"] not in skill_ids()] == []
    names = Counter(r["language"] for r in rows)
    assert [name for name, n in names.items() if n > 1] == []
