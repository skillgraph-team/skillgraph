"""Finds skills in one imported GitHub repo (M4.3, System A: fixed rules, no AI).

`find_in_repo(repo, index, github_username=..., today=...)` reads the `RepoInfo` saved by
the GitHub import (M3.6) and returns findings in this order:

1. **Languages** → `repo_language`, one per language GitHub reports that is a skill.
   Quote `Python 90%`. The location keeps what M4.4's rule needs (evidence model §3.2):
   the share, whether the repo is `owned` by the user's GitHub name, and `is_fork`.
   Every share is kept here, even under 10 %; the rule decides.
2. **Dependency files** → `repo_dependency`, one per skill per file: `requirements.txt`,
   `pyproject.toml`, `package.json`, `pom.xml`. Quote the line, location the file path
   and line. A file that can't be parsed gives nothing.
3. **README** → `repo_readme`, one per sentence naming skills, matched like CV prose
   (app/skills/matching.py). Markdown headings and code blocks are skipped, and links
   are ignored when matching.
4. **Topics** → one `repo_readme` finding listing the topics, location `field: topics`.
   There is no evidence type for topics; like the README they are the repo describing
   itself, so they are context only (T-148).

No `repo_code` evidence: the import doesn't download code files (T-149).

Package and GitHub language names are matched in this order: the mapping files
(`packages.csv`, `github_languages.csv` in app/skills/data/, for names that differ from
the skill, like `psycopg` → postgresql; a trailing `*` matches any ending), then the
skill index. Scoped npm names (`@types/node`) only match through the mapping file.

Every location also has the repo's `weight` (`repo_weight`), 0 to 1, higher for larger,
more recently pushed repos where the user made more of the commits. The status rules
don't use it (they follow D-006 exactly); it orders and explains evidence (T-147).
"""

import csv
import json
import re
import tomllib
from datetime import date
from functools import cache
from pathlib import PurePosixPath
from typing import Any

from app.ingestion.github_repos import RepoFile, RepoInfo
from app.ingestion.language import detect_language
from app.skills.findings import Finding
from app.skills.index import SkillIndex
from app.skills.matching import cut_quote, quote_language, sentences, skills_in
from app.skills.taxonomy import DATA_DIR

FULL_SIZE_BYTES = 50_000
"""A repo with this much code (all languages together) counts as full size."""
RECENT_DAYS = 365
OLD_DAYS = 3 * 365

_PACKAGE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_ARTIFACT = re.compile(r"<artifactId>\s*([^<\s]+)\s*</artifactId>")
_LINK = re.compile(r"\]\([^)]*\)|https?://\S+")


# --- mapping files ---------------------------------------------------------------------


@cache
def _mapping(file_name: str, key: str) -> dict[str, str]:
    with (DATA_DIR / file_name).open(encoding="utf-8", newline="") as f:
        return {row[key]: row["skill_id"] for row in csv.DictReader(f)}


def package_skill(package: str, index: SkillIndex) -> str | None:
    name = package.lower().replace("_", "-")
    mapping = _mapping("packages.csv", "package")
    if name in mapping:
        return mapping[name]
    prefixes = sorted((p for p in mapping if p.endswith("*")), key=len, reverse=True)
    for prefix in prefixes:
        if name.startswith(prefix[:-1]):
            return mapping[prefix]
    if name.startswith("@"):
        return None
    return index.resolve(name)


def language_skill(language: str, index: SkillIndex) -> str | None:
    return _mapping("github_languages.csv", "language").get(language) or index.resolve(language)


# --- weight ------------------------------------------------------------------------------


def repo_weight(repo: RepoInfo, *, today: date) -> float:
    """authorship × recency × size, each 0 to 1, rounded to 2 decimals.

    - authorship: the user's share of the commits; 0 for a fork or a repo with no commits;
      1 when GitHub gave no commit counts.
    - recency: 1 if pushed in the last year, 0.5 in the last three, otherwise 0.25.
    - size: the code's bytes over FULL_SIZE_BYTES, at most 1.
    """
    if repo.is_fork:
        return 0.0
    if repo.commits is None:
        authorship = 1.0
    elif repo.commits.total == 0:
        return 0.0
    else:
        authorship = repo.commits.by_user / repo.commits.total

    days = (today - repo.pushed_at.date()).days if repo.pushed_at else OLD_DAYS + 1
    recency = 1.0 if days <= RECENT_DAYS else 0.5 if days <= OLD_DAYS else 0.25
    size = min(1.0, sum(repo.languages.values()) / FULL_SIZE_BYTES)
    return round(authorship * recency * size, 2)


# --- the finder --------------------------------------------------------------------------


def find_in_repo(
    repo: RepoInfo, index: SkillIndex, *, github_username: str | None, today: date
) -> list[Finding]:
    weight = repo_weight(repo, today=today)
    owned = bool(github_username) and repo.owner.lower() == (github_username or "").lower()
    return [
        *_languages(repo, index, owned=owned, weight=weight),
        *_dependencies(repo, index, weight=weight),
        *_readme(repo, index, weight=weight),
        *_topics(repo, index, weight=weight),
    ]


def _languages(repo: RepoInfo, index: SkillIndex, *, owned: bool, weight: float) -> list[Finding]:
    findings = []
    for language, share in repo.language_shares.items():
        skill_id = language_skill(language, index)
        if skill_id is None:
            continue
        findings.append(
            Finding(
                type="repo_language",
                quote=f"{language} {share:g}%",
                location={
                    "repo": repo.full_name,
                    "language": language,
                    "share": share,
                    "bytes": repo.languages.get(language, 0),
                    "owned": owned,
                    "is_fork": repo.is_fork,
                    "weight": weight,
                },
                language="other",
                skill_ids=[skill_id],
            )
        )
    return findings


def _dependencies(repo: RepoInfo, index: SkillIndex, *, weight: float) -> list[Finding]:
    findings = []
    for file in repo.dependency_files:
        seen: set[str] = set()
        for line, text, package in _packages(file):
            skill_id = package_skill(package, index)
            if skill_id is None or skill_id in seen:
                continue
            seen.add(skill_id)
            findings.append(
                Finding(
                    type="repo_dependency",
                    quote=cut_quote(text, package),
                    location={
                        "repo": repo.full_name,
                        "path": file.path,
                        "line": line,
                        "package": package,
                        "weight": weight,
                    },
                    language="other",
                    skill_ids=[skill_id],
                )
            )
    return findings


def _readme(repo: RepoInfo, index: SkillIndex, *, weight: float) -> list[Finding]:
    if repo.readme is None:
        return []
    readme_language = detect_language(repo.readme.content)
    findings = []
    in_code_block = False
    for line_number, raw_line in enumerate(repo.readme.content.split("\n"), start=1):
        line = raw_line.strip()
        if line.startswith(("```", "~~~")):
            in_code_block = not in_code_block
            continue
        if in_code_block or not line or line.startswith("#"):
            continue
        for _, sentence in sentences(line):
            found = skills_in(_LINK.sub(" ", sentence), index, in_skills_list=False)
            if not found:
                continue
            quote = cut_quote(sentence, found[0][1])
            findings.append(
                Finding(
                    type="repo_readme",
                    quote=quote,
                    location={
                        "repo": repo.full_name,
                        "path": repo.readme.path,
                        "line": line_number,
                        "weight": weight,
                    },
                    language=quote_language(quote, readme_language),
                    skill_ids=[skill_id for skill_id, _ in found],
                )
            )
    return findings


def _topics(repo: RepoInfo, index: SkillIndex, *, weight: float) -> list[Finding]:
    skill_ids = list(dict.fromkeys(s for s in map(index.resolve, repo.topics) if s))
    if not skill_ids:
        return []
    quote = cut_quote("topics: " + ", ".join(repo.topics), repo.topics[0])
    return [
        Finding(
            type="repo_readme",
            quote=quote,
            location={"repo": repo.full_name, "field": "topics", "weight": weight},
            language="other",
            skill_ids=skill_ids,
        )
    ]


# --- dependency files ----------------------------------------------------------------------


def _packages(file: RepoFile) -> list[tuple[int | None, str, str]]:
    """(line number, line text, package name) for each package the file lists."""
    name = PurePosixPath(file.path).name
    try:
        if name == "requirements.txt":
            return _requirements(file.content)
        if name == "package.json":
            names = _package_json(json.loads(file.content))
        elif name == "pyproject.toml":
            names = _pyproject(tomllib.loads(file.content))
        elif name == "pom.xml":
            return _pom(file.content)
        else:
            return []
    except (ValueError, TypeError, AttributeError):  # JSON / TOML errors are ValueErrors
        return []
    lines = file.content.split("\n")
    return [(*_line_of(lines, package), package) for package in names]


def _requirements(content: str) -> list[tuple[int | None, str, str]]:
    out: list[tuple[int | None, str, str]] = []
    for number, raw_line in enumerate(content.split("\n"), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        match = _PACKAGE_NAME.match(line)
        if match:
            out.append((number, raw_line.strip(), match.group()))
    return out


def _package_json(data: Any) -> list[str]:
    names: list[str] = []
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        names.extend(data.get(key) or {})
    return names


def _pyproject(data: dict[str, Any]) -> list[str]:
    project = data.get("project", {})
    requirements: list[str] = list(project.get("dependencies", []))
    for group in project.get("optional-dependencies", {}).values():
        requirements.extend(group)
    for group in data.get("dependency-groups", {}).values():
        requirements.extend(item for item in group if isinstance(item, str))
    names = [m.group() for m in map(_PACKAGE_NAME.match, requirements) if m]

    poetry = data.get("tool", {}).get("poetry", {})
    tables = [poetry.get("dependencies", {}), poetry.get("dev-dependencies", {})]
    tables += [group.get("dependencies", {}) for group in poetry.get("group", {}).values()]
    names += [package for table in tables for package in table if package != "python"]
    return names


def _pom(content: str) -> list[tuple[int | None, str, str]]:
    dependencies_start = content.find("<dependencies>")
    if dependencies_start < 0:
        return []
    out: list[tuple[int | None, str, str]] = []
    for match in _ARTIFACT.finditer(content, dependencies_start):
        number = content.count("\n", 0, match.start()) + 1
        out.append((number, content.split("\n")[number - 1].strip(), match.group(1)))
    return out


def _line_of(lines: list[str], package: str) -> tuple[int | None, str]:
    """The first line naming `package` as a whole name, and its text."""
    pattern = re.compile(r"(?<![\w@/.-])" + re.escape(package) + r"(?![\w/.-])", re.IGNORECASE)
    for number, line in enumerate(lines, start=1):
        if pattern.search(line):
            return number, line.strip()
    return None, package
