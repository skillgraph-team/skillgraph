"""Checks on the skill list CSVs (M4.1, M4.9): right columns, ids the database accepts,
a name in all three languages, no duplicate ids, names or aliases, every reference points
at a real skill, and no loops in the parent links. Reads the files with the standard csv
module; no database needed.
"""

import csv
import re
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "app" / "skills" / "data"

# Same pattern as the CHECK on skills.id (app/db/models/skills.py).
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.+#_-]*$")
CATEGORIES = {
    "language",
    "framework",
    "library",
    "database",
    "cloud",
    "devops",
    "tool",
    "data",
    "ai",
    "practice",
    "area",
    "soft",
    "spoken_language",
}


NAME_COLUMNS = ("name_en", "name_fr", "name_ar")
ARABIC_LETTER = re.compile(r"[؀-ۿ]")


def read(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def header(name: str) -> list[str]:
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return next(csv.reader(f))


def skill_ids() -> set[str]:
    return {row["id"] for row in read("skills.csv")}


def test_files_have_the_expected_columns() -> None:
    assert header("skills.csv") == ["id", "name_en", "name_fr", "name_ar", "category"]
    assert header("aliases.csv") == ["alias", "skill_id"]
    assert header("relations.csv") == ["child_id", "parent_id"]


def test_skill_count_is_in_the_planned_range() -> None:
    assert 150 <= len(read("skills.csv")) <= 300


def test_skill_ids_are_valid_and_unique() -> None:
    ids = [row["id"] for row in read("skills.csv")]
    bad = [i for i in ids if not ID_PATTERN.match(i) or len(i) > 64]
    assert bad == []
    assert len(ids) == len(set(ids)), sorted({i for i in ids if ids.count(i) > 1})


def own_names(row: dict[str, str]) -> set[str]:
    """The id and the three names, lowercased: what the normalizer (M4.2) matches
    without needing an alias."""
    return {row["id"]} | {row[c].lower() for c in NAME_COLUMNS}


def test_skills_have_three_names_and_a_known_category() -> None:
    rows = read("skills.csv")
    for column in NAME_COLUMNS:
        assert [r["id"] for r in rows if not r[column].strip()] == [], column
        assert [r["id"] for r in rows if r[column] != r[column].strip()] == [], column
    assert [r["id"] for r in rows if r["category"] not in CATEGORIES] == []


def test_names_are_unique_within_each_language() -> None:
    rows = read("skills.csv")
    for column in NAME_COLUMNS:
        names = [r[column].lower() for r in rows]
        assert len(names) == len(set(names)), (
            column,
            sorted({n for n in names if names.count(n) > 1}),
        )


def test_arabic_names_use_arabic_letters_or_stay_technical() -> None:
    """An Arabic name is either written in Arabic, or is exactly the English name
    (Python, Docker: technical names stay in Latin letters, localization.md section 3)."""
    rows = read("skills.csv")
    bad = [
        r["id"]
        for r in rows
        if not ARABIC_LETTER.search(r["name_ar"]) and r["name_ar"] != r["name_en"]
    ]
    assert bad == []


def test_aliases_are_lowercase_unique_and_point_at_a_skill() -> None:
    rows = read("aliases.csv")
    aliases = [r["alias"] for r in rows]
    assert [a for a in aliases if a != a.lower() or a != a.strip() or not a] == []
    assert [a for a in aliases if len(a) > 100] == []
    assert len(aliases) == len(set(aliases)), sorted({a for a in aliases if aliases.count(a) > 1})
    ids = skill_ids()
    assert [r for r in rows if r["skill_id"] not in ids] == []


def test_an_alias_never_names_a_different_skill() -> None:
    """An alias can't be another skill's id or name in any language ("js" can't point
    at javascript if some other skill is called "js")."""
    own_name = {name: r["id"] for r in read("skills.csv") for name in own_names(r)}
    clashes = [
        r
        for r in read("aliases.csv")
        if r["alias"] in own_name and own_name[r["alias"]] != r["skill_id"]
    ]
    assert clashes == []


def test_aliases_do_not_repeat_the_id_or_name() -> None:
    """The normalizer (M4.2) already matches the id and the three names; repeating them
    here would only hide mistakes."""
    names = {r["id"]: own_names(r) for r in read("skills.csv")}
    repeats = [r for r in read("aliases.csv") if r["alias"] in names.get(r["skill_id"], set())]
    assert repeats == []


def test_relations_point_at_real_skills_and_are_unique() -> None:
    rows = read("relations.csv")
    ids = skill_ids()
    assert [r for r in rows if r["child_id"] not in ids or r["parent_id"] not in ids] == []
    assert [r for r in rows if r["child_id"] == r["parent_id"]] == []
    pairs = [(r["child_id"], r["parent_id"]) for r in rows]
    assert len(pairs) == len(set(pairs))


def test_parent_links_have_no_loops() -> None:
    parents: dict[str, set[str]] = {}
    for r in read("relations.csv"):
        parents.setdefault(r["child_id"], set()).add(r["parent_id"])

    def reaches_itself(start: str) -> bool:
        seen: set[str] = set()
        todo = list(parents.get(start, ()))
        while todo:
            node = todo.pop()
            if node == start:
                return True
            if node not in seen:
                seen.add(node)
                todo.extend(parents.get(node, ()))
        return False

    assert [s for s in parents if reaches_itself(s)] == []


def test_the_example_chain_from_the_plan_exists() -> None:
    pairs = {(r["child_id"], r["parent_id"]) for r in read("relations.csv")}
    assert ("postgresql", "sql") in pairs
    assert ("sql", "databases") in pairs
    aliases = {r["alias"]: r["skill_id"] for r in read("aliases.csv")}
    assert aliases["postgres"] == "postgresql"
    assert aliases["js"] == "javascript"
