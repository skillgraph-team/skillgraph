"""Tests for finding skills in an imported GitHub repo (M4.3): languages, dependency
files, README sentences and topics, each becoming a finding that points to the repo and
file. No database; repos are built in the test or read from the fake GitHub's made-up
account `test-student` (tests/fixtures/github/)."""

import tempfile
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pytest

from app.ingestion.github_repos import Commits, RepoFile, RepoInfo, fetch_repos
from app.skills.findings import Finding
from app.skills.index import SkillIndex
from app.skills.repo_finder import find_in_repo, repo_weight
from tests.fixtures.github.fake_github import FakeGitHub

TODAY = date(2026, 11, 26)


@pytest.fixture(scope="module")
def index() -> SkillIndex:
    return SkillIndex.from_csv()


def make_repo(**overrides: Any) -> RepoInfo:
    values: dict[str, Any] = {
        "full_name": "sam/app",
        "owner": "sam",
        "html_url": "https://github.com/sam/app",
        "description": None,
        "is_fork": False,
        "is_archived": False,
        "default_branch": "main",
        "pushed_at": datetime(2026, 11, 1, tzinfo=UTC),
        "topics": [],
        # Full-size code by default (weight 1.0), but no language shares, so a test
        # only gets language findings when it sets `language_shares` itself.
        "languages": {"Python": 80_000},
        "language_shares": {},
        "commits": Commits(by_user=10, total=10),
    }
    return RepoInfo(**(values | overrides))


def summary(findings: list[Finding]) -> list[tuple[str, list[str], Any]]:
    return [(f.type, f.skill_ids, f.location.get("line")) for f in findings]


def find(repo: RepoInfo, index: SkillIndex, username: str = "sam") -> list[Finding]:
    return find_in_repo(repo, index, github_username=username, today=TODAY)


# --- languages -------------------------------------------------------------------


def test_each_known_language_is_a_finding_with_its_share(index: SkillIndex) -> None:
    repo = make_repo(
        languages={"Python": 9000, "Shell": 600, "Dockerfile": 400, "Makefile": 10},
        language_shares={"Python": 90.0, "Shell": 6.0, "Dockerfile": 4.0, "Makefile": 0.1},
    )
    findings = [f for f in find(repo, index) if f.type == "repo_language"]
    assert [(f.quote, f.skill_ids) for f in findings] == [
        ("Python 90%", ["python"]),
        ("Shell 6%", ["bash"]),
        ("Dockerfile 4%", ["docker"]),
    ]
    python = findings[0].location
    assert python["repo"] == "sam/app"
    assert python["language"] == "Python"
    assert python["share"] == 90.0
    assert python["owned"] is True
    assert python["is_fork"] is False
    assert findings[0].language == "other"


def test_a_repo_of_someone_else_is_marked_not_owned(index: SkillIndex) -> None:
    repo = make_repo(owner="team", full_name="team/app", language_shares={"Go": 100.0})
    [finding] = find(repo, index, username="sam")
    assert finding.location["owned"] is False


def test_a_fork_still_gives_language_findings_marked_as_fork(index: SkillIndex) -> None:
    repo = make_repo(is_fork=True, commits=None, language_shares={"JavaScript": 80.0})
    [finding] = find(repo, index)
    assert finding.skill_ids == ["javascript"]
    assert finding.location["is_fork"] is True
    assert finding.location["weight"] == 0.0


def test_a_decimal_share_keeps_its_decimal(index: SkillIndex) -> None:
    [finding] = find(make_repo(language_shares={"HTML": 6.2}), index)
    assert finding.quote == "HTML 6.2%"


# --- dependency files --------------------------------------------------------------


def dependency(path: str, content: str) -> RepoInfo:
    return make_repo(dependency_files=[RepoFile(path=path, content=content)])


def test_requirements_txt(index: SkillIndex) -> None:
    repo = dependency(
        "requirements.txt",
        "fastapi==0.110\n# comment\npsycopg[binary]>=3\n-r dev.txt\nuvicorn\nFastAPI-Utils\n",
    )
    findings = find(repo, index)
    assert summary(findings) == [
        ("repo_dependency", ["fastapi"], 1),
        ("repo_dependency", ["postgresql"], 3),
    ]
    assert findings[1].quote == "psycopg[binary]>=3"
    assert findings[1].location == {
        "repo": "sam/app",
        "path": "requirements.txt",
        "line": 3,
        "package": "psycopg",
        "weight": 1.0,
    }


def test_package_json_with_scoped_packages_and_one_finding_per_skill(
    index: SkillIndex,
) -> None:
    content = """{
  "name": "shop-admin",
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@reduxjs/toolkit": "^2.0.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "@types/node": "^20.0.0"
  }
}
"""
    findings = find(dependency("admin/package.json", content), index)
    assert summary(findings) == [
        ("repo_dependency", ["react"], 4),
        ("repo_dependency", ["redux"], 6),
        ("repo_dependency", ["jest"], 9),
    ]
    assert findings[0].quote == '"react": "^18.3.0",'


def test_pyproject_toml(index: SkillIndex) -> None:
    content = """[project]
name = "shop"
dependencies = [
    "sqlalchemy>=2",
    "pandas",
]

[dependency-groups]
dev = ["pytest>=8"]

[tool.poetry.dependencies]
python = "^3.12"
django = "^5.0"
"""
    findings = find(dependency("pyproject.toml", content), index)
    assert summary(findings) == [
        ("repo_dependency", ["sqlalchemy"], 4),
        ("repo_dependency", ["pandas"], 5),
        ("repo_dependency", ["pytest"], 9),
        ("repo_dependency", ["django"], 13),
    ]


def test_pom_xml_ignores_the_projects_own_name(index: SkillIndex) -> None:
    content = """<project>
  <artifactId>library-app</artifactId>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
      <artifactId>postgresql</artifactId>
    </dependency>
    <dependency>
      <artifactId>junit-jupiter</artifactId>
    </dependency>
  </dependencies>
</project>
"""
    findings = find(dependency("pom.xml", content), index)
    assert summary(findings) == [
        ("repo_dependency", ["spring-boot"], 6),
        ("repo_dependency", ["postgresql"], 9),
        ("repo_dependency", ["junit"], 12),
    ]
    assert findings[0].quote == "<artifactId>spring-boot-starter-web</artifactId>"


def test_a_broken_dependency_file_gives_no_findings(index: SkillIndex) -> None:
    assert find(dependency("package.json", "{ not json"), index) == []
    assert find(dependency("pyproject.toml", "[project\n"), index) == []


# --- README and topics --------------------------------------------------------------


def test_readme_sentences_naming_skills_but_not_code_blocks(index: SkillIndex) -> None:
    readme = """# Shop API

A REST API built with FastAPI.
```bash
pip install django
```
Deployed on Heroku. Nothing else here.
"""
    repo = make_repo(readme=RepoFile(path="README.md", content=readme))
    findings = find(repo, index)
    assert summary(findings) == [
        ("repo_readme", ["rest-api", "fastapi"], 3),
        ("repo_readme", ["heroku"], 7),
    ]
    assert findings[0].quote == "A REST API built with FastAPI."
    assert findings[0].location["path"] == "README.md"
    assert findings[0].language == "en"


def test_topics_are_one_readme_finding(index: SkillIndex) -> None:
    repo = make_repo(topics=["fastapi", "postgresql", "hacktoberfest"])
    [finding] = find(repo, index)
    assert finding.type == "repo_readme"
    assert finding.quote == "topics: fastapi, postgresql, hacktoberfest"
    assert finding.skill_ids == ["fastapi", "postgresql"]
    assert finding.location == {"repo": "sam/app", "field": "topics", "weight": 1.0}


# --- weight ---------------------------------------------------------------------------


def test_weight_is_higher_for_larger_more_recent_repos_the_user_wrote() -> None:
    big_recent_mine = make_repo(languages={"Python": 80_000})
    assert repo_weight(big_recent_mine, today=TODAY) == 1.0

    small = make_repo(languages={"Python": 10_000})
    half_mine = make_repo(languages={"Python": 80_000}, commits=Commits(by_user=5, total=10))
    old = make_repo(languages={"Python": 80_000}, pushed_at=datetime(2022, 1, 1, tzinfo=UTC))
    for repo in (small, half_mine, old):
        assert repo_weight(repo, today=TODAY) < 1.0

    assert repo_weight(make_repo(is_fork=True), today=TODAY) == 0.0
    assert repo_weight(make_repo(commits=Commits(by_user=0, total=0)), today=TODAY) == 0.0


# --- the made-up GitHub account ------------------------------------------------------


def test_the_fake_github_account_gives_the_expected_evidence(index: SkillIndex) -> None:
    repos = fetch_repos(FakeGitHub().client(Path(tempfile.mkdtemp())), "test-student", max_repos=20)
    found = {
        repo.full_name: [
            (f.type, f.skill_ids)
            for f in find_in_repo(repo, index, github_username="test-student", today=TODAY)
        ]
        for repo in repos
    }
    assert found == {
        "test-student/shop-api": [
            ("repo_language", ["python"]),
            ("repo_language", ["bash"]),
            ("repo_language", ["docker"]),
            ("repo_dependency", ["fastapi"]),
            ("repo_dependency", ["postgresql"]),
            ("repo_dependency", ["pytest"]),
            ("repo_dependency", ["react"]),
            ("repo_readme", ["rest-api", "fastapi", "postgresql"]),
            ("repo_readme", ["pytest", "docker"]),
            ("repo_readme", ["fastapi", "postgresql"]),
        ],
        "test-student/projet-bibliotheque": [
            ("repo_language", ["java"]),
            ("repo_language", ["html"]),
            ("repo_dependency", ["spring-boot"]),
            ("repo_readme", ["java", "spring-boot"]),
            ("repo_readme", ["databases", "mysql"]),
        ],
        "test-student/awesome-dashboard": [
            ("repo_language", ["javascript"]),
            ("repo_language", ["css"]),
        ],
        "test-student/empty-repo": [],
    }
