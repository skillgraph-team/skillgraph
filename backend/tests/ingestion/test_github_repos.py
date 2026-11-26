"""Tests for reading a user's repos (M3.6) from the fake GitHub's saved answers for the
made-up account `test-student`: 4 repos, one a fork and one empty."""

from pathlib import Path

import pytest

from app.ingestion.github_repos import (
    GitHubUserNotFoundError,
    RepoInfo,
    dependency_paths,
    fetch_repos,
    language_shares,
)
from tests.fixtures.github.fake_github import FakeGitHub


@pytest.fixture
def repos(tmp_path: Path) -> dict[str, RepoInfo]:
    found = fetch_repos(FakeGitHub().client(tmp_path), "test-student", max_repos=20)
    return {repo.full_name: repo for repo in found}


def test_reads_every_repo_newest_push_first(tmp_path: Path) -> None:
    found = fetch_repos(FakeGitHub().client(tmp_path), "test-student", max_repos=20)

    assert [repo.full_name for repo in found] == [
        "test-student/shop-api",
        "test-student/projet-bibliotheque",
        "test-student/awesome-dashboard",
        "test-student/empty-repo",
    ]


def test_owned_repo_has_languages_topics_readme_dependencies_and_commits(
    repos: dict[str, RepoInfo],
) -> None:
    shop = repos["test-student/shop-api"]

    assert shop.owner == "test-student"
    assert not shop.is_fork
    assert shop.topics == ["fastapi", "postgresql"]
    assert shop.languages == {"Python": 9000, "Shell": 600, "Dockerfile": 400}
    assert shop.language_shares == {"Python": 90.0, "Shell": 6.0, "Dockerfile": 4.0}
    assert shop.readme is not None and shop.readme.path == "README.md"
    assert "built with FastAPI and PostgreSQL" in shop.readme.content
    assert [file.path for file in shop.dependency_files] == [
        "requirements.txt",
        "admin/package.json",
    ]
    assert shop.dependency_files[0].content.splitlines()[0] == "fastapi==0.115.0"
    assert shop.commits is not None
    assert (shop.commits.by_user, shop.commits.total) == (42, 50)


def test_commits_match_the_username_whatever_its_case(repos: dict[str, RepoInfo]) -> None:
    library = repos["test-student/projet-bibliotheque"]

    assert library.commits is not None and library.commits.by_user == 17


def test_fork_only_gets_its_languages(tmp_path: Path) -> None:
    fake = FakeGitHub()
    found = fetch_repos(fake.client(tmp_path), "test-student", max_repos=20)
    fork = next(repo for repo in found if repo.is_fork)

    assert fork.language_shares == {"JavaScript": 80.0, "CSS": 20.0}
    assert fork.commits is None and fork.readme is None and fork.dependency_files == []
    assert [key for key in fake.requests if "awesome-dashboard" in key] == [
        "/repos/test-student/awesome-dashboard/languages"
    ]


def test_empty_repo_has_nothing_but_does_not_fail(repos: dict[str, RepoInfo]) -> None:
    empty = repos["test-student/empty-repo"]

    assert empty.languages == {} and empty.language_shares == {}
    assert empty.commits is not None and empty.commits.total == 0
    assert empty.readme is None and empty.dependency_files == []


def test_unknown_user(tmp_path: Path) -> None:
    with pytest.raises(GitHubUserNotFoundError):
        fetch_repos(FakeGitHub().client(tmp_path), "nobody-here", max_repos=20)


def test_max_repos_limits_the_import(tmp_path: Path) -> None:
    fake = FakeGitHub()
    # The saved listing is for per_page=20; reuse it under per_page=1.
    fake.responses["/users/test-student/repos?per_page=1&sort=pushed&type=owner"] = fake.responses[
        "/users/test-student/repos?per_page=20&sort=pushed&type=owner"
    ]

    found = fetch_repos(fake.client(tmp_path), "test-student", max_repos=1)

    assert [repo.full_name for repo in found] == ["test-student/shop-api"]


def test_dependency_paths_skip_installed_code_and_go_shallowest_first() -> None:
    tree = [
        {"path": "web/package.json", "type": "blob"},
        {"path": "web/node_modules/react/package.json", "type": "blob"},
        {"path": "requirements.txt", "type": "blob"},
        {"path": ".venv/lib/pyproject.toml", "type": "blob"},
        {"path": "pom.xml", "type": "tree"},  # a folder named like a file
        {"path": "src/app.py", "type": "blob"},
    ]

    assert dependency_paths(tree) == ["requirements.txt", "web/package.json"]


def test_dependency_paths_are_capped() -> None:
    tree = [{"path": f"service{n}/requirements.txt", "type": "blob"} for n in range(9)]

    assert len(dependency_paths(tree)) == 5


def test_language_shares() -> None:
    assert language_shares({}) == {}
    assert language_shares({"Python": 2, "Shell": 1}) == {"Python": 66.7, "Shell": 33.3}
