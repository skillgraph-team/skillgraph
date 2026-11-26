"""Collects what we need from a GitHub user's public repos (M3.6). No database here:
`fetch_repos` returns one `RepoInfo` per repo, and app/services/github_imports.py saves them.

For each repo owned by the username (most recently pushed first, at most `max_repos`):
- always: name, fork flag, topics, description, and the language byte counts
  (`/languages`), turned into shares in %. The evidence model's 10 % rule uses these.
- for repos that are **not forks** only (a fork never supports a skill, so its details
  would cost requests for nothing):
  - commit counts from `/contributors`: the user's commits and everyone's. This is
    the "how much of the code did they write" signal. It counts commits on the
    default branch, first 100 contributors only.
  - the README text;
  - the file list (`/git/trees`), used to find dependency files anywhere in the repo
    (requirements.txt, pyproject.toml, package.json, pom.xml), except in folders of
    installed or generated code (node_modules, venv, ...). Up to
    MAX_DEPENDENCY_FILES of them are downloaded.

File texts are kept exactly as they are (only NUL characters are removed, which
PostgreSQL can't store), so line numbers stay right for evidence locations.

Requests per repo: 1 for a fork; 4 plus one per dependency file otherwise.
"""

import base64
from datetime import datetime
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import quote

from pydantic import BaseModel

from app.ingestion.github_client import GitHubClient, GitHubError

DEPENDENCY_FILES = frozenset({"requirements.txt", "pyproject.toml", "package.json", "pom.xml"})
SKIPPED_FOLDERS = frozenset(
    {"node_modules", "vendor", ".venv", "venv", "env", "site-packages", "dist", "build"}
)
MAX_DEPENDENCY_FILES = 5
MAX_FILE_CHARS = 100_000
"""Longer READMEs and dependency files are cut here (and marked `truncated`)."""


class GitHubUserNotFoundError(GitHubError):
    code = "github_user_not_found"


class RepoFile(BaseModel):
    path: str
    content: str
    truncated: bool = False


class Commits(BaseModel):
    by_user: int
    total: int


class RepoInfo(BaseModel):
    full_name: str
    owner: str
    html_url: str
    description: str | None
    is_fork: bool
    is_archived: bool
    default_branch: str | None
    pushed_at: datetime | None
    topics: list[str]
    languages: dict[str, int]
    """Bytes of code per language, as GitHub counts them."""
    language_shares: dict[str, float]
    """The same as % of the repo's code, one decimal: {"Python": 90.0}."""
    commits: Commits | None = None
    readme: RepoFile | None = None
    dependency_files: list[RepoFile] = []
    file_list_truncated: bool = False
    """True when GitHub cut the file list short (very large repos)."""


def fetch_repos(client: GitHubClient, username: str, *, max_repos: int) -> list[RepoInfo]:
    listing = client.get(
        f"/users/{username}/repos", {"type": "owner", "sort": "pushed", "per_page": max_repos}
    )
    if listing is None:
        raise GitHubUserNotFoundError
    return [_fetch_repo(client, username, repo) for repo in listing[:max_repos]]


def _fetch_repo(client: GitHubClient, username: str, repo: dict[str, Any]) -> RepoInfo:
    full_name: str = repo["full_name"]
    languages: dict[str, int] = client.get(f"/repos/{full_name}/languages") or {}
    info = RepoInfo(
        full_name=full_name,
        owner=repo["owner"]["login"],
        html_url=repo["html_url"],
        description=repo.get("description"),
        is_fork=repo["fork"],
        is_archived=repo.get("archived", False),
        default_branch=repo.get("default_branch"),
        pushed_at=repo.get("pushed_at"),
        topics=repo.get("topics", []),
        languages=languages,
        language_shares=language_shares(languages),
    )
    if info.is_fork:
        return info

    contributors = client.get(f"/repos/{full_name}/contributors", {"per_page": 100}) or []
    info.commits = Commits(
        by_user=sum(
            person["contributions"]
            for person in contributors
            if person.get("login", "").lower() == username.lower()
        ),
        total=sum(person["contributions"] for person in contributors),
    )

    readme = client.get(f"/repos/{full_name}/readme")
    if readme is not None:
        info.readme = _file(readme["path"], readme)

    if info.default_branch:
        tree = client.get(
            f"/repos/{full_name}/git/trees/{quote(info.default_branch)}", {"recursive": 1}
        )
        if tree is not None:
            info.file_list_truncated = tree.get("truncated", False)
            for path in dependency_paths(tree["tree"]):
                content = client.get(
                    f"/repos/{full_name}/contents/{quote(path)}", {"ref": info.default_branch}
                )
                if content is not None:
                    info.dependency_files.append(_file(path, content))
    return info


def language_shares(languages: dict[str, int]) -> dict[str, float]:
    total = sum(languages.values())
    if not total:
        return {}
    return {name: round(100 * size / total, 1) for name, size in languages.items()}


def dependency_paths(tree: list[dict[str, Any]]) -> list[str]:
    """Paths of dependency files, shallowest first, skipping installed/generated code."""
    found = []
    for entry in tree:
        path = PurePosixPath(entry["path"])
        if entry.get("type") != "blob" or path.name not in DEPENDENCY_FILES:
            continue
        if any(folder in SKIPPED_FOLDERS for folder in path.parts[:-1]):
            continue
        found.append(entry["path"])
    found.sort(key=lambda p: (p.count("/"), p))
    return found[:MAX_DEPENDENCY_FILES]


def _file(path: str, content: dict[str, Any]) -> RepoFile:
    """A file from GitHub's contents API: base64 text, decoded as UTF-8."""
    raw = base64.b64decode(content.get("content", "")).decode("utf-8", errors="replace")
    text = raw.replace("\x00", "")
    return RepoFile(path=path, content=text[:MAX_FILE_CHARS], truncated=len(text) > MAX_FILE_CHARS)
