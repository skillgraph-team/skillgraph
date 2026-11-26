"""Tests for the GitHub client (M3.6): the cache, ETags, the rate limit, the token.
All answers come from the fake GitHub; nothing reaches the network."""

from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from app.ingestion.github_client import (
    GitHubClient,
    GitHubRateLimitError,
    GitHubUnavailableError,
    forget_cached_user,
)
from tests.fixtures.github.fake_github import BASE_URL, FakeGitHub

LANGUAGES = "/repos/test-student/shop-api/languages"


class Clock:
    """Time that only moves when the test says so."""

    def __init__(self) -> None:
        self.now = 1_000_000.0

    def __call__(self) -> float:
        return self.now


def test_returns_the_json_body(tmp_path: Path) -> None:
    client = FakeGitHub().client(tmp_path)

    assert client.get(LANGUAGES) == {"Python": 9000, "Shell": 600, "Dockerfile": 400}


@pytest.mark.parametrize(
    "path",
    [
        "/repos/test-student/empty-repo/readme",  # 404
        "/repos/test-student/empty-repo/git/trees/main?recursive=1",  # 409 empty repo
        "/repos/test-student/empty-repo/contributors?per_page=100",  # 204
    ],
)
def test_nothing_there_is_none(tmp_path: Path, path: str) -> None:
    assert FakeGitHub().client(tmp_path).get(path) is None


def test_fresh_cached_answer_is_reused_without_asking_github(tmp_path: Path) -> None:
    fake = FakeGitHub()
    clock = Clock()
    client = fake.client(tmp_path, cache_seconds=60, clock=clock)

    first = client.get(LANGUAGES)
    clock.now += 59
    second = client.get(LANGUAGES)

    assert first == second
    assert fake.requests == [LANGUAGES]


def test_old_cached_answer_is_checked_with_its_etag(tmp_path: Path) -> None:
    fake = FakeGitHub()
    clock = Clock()
    client = fake.client(tmp_path, cache_seconds=60, clock=clock)
    first = client.get(LANGUAGES)

    clock.now += 61
    again = client.get(LANGUAGES)

    assert again == first
    assert len(fake.requests) == 2
    etag = fake.responses[LANGUAGES]["headers"]["ETag"]
    assert fake.seen_headers[1]["If-None-Match"] == etag  # GitHub answered 304


def test_cache_survives_a_new_client(tmp_path: Path) -> None:
    """The cache is files on disk, so a server restart doesn't empty it."""
    fake = FakeGitHub()
    fake.client(tmp_path).get(LANGUAGES)

    fake.client(tmp_path).get(LANGUAGES)

    assert fake.requests == [LANGUAGES]


def test_broken_cache_file_is_ignored(tmp_path: Path) -> None:
    fake = FakeGitHub()
    fake.client(tmp_path).get(LANGUAGES)
    for file in tmp_path.iterdir():
        file.write_text("not json", encoding="utf-8")

    assert fake.client(tmp_path).get(LANGUAGES) == {"Python": 9000, "Shell": 600, "Dockerfile": 400}


def test_rate_limit_says_when_it_resets(tmp_path: Path) -> None:
    fake = FakeGitHub()
    fake.override(LANGUAGES, 403, {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1795683398"})

    with pytest.raises(GitHubRateLimitError) as caught:
        fake.client(tmp_path).get(LANGUAGES)

    assert caught.value.reset_at == datetime.fromtimestamp(1795683398, UTC)


def test_secondary_rate_limit_uses_retry_after(tmp_path: Path) -> None:
    fake = FakeGitHub()
    fake.override(LANGUAGES, 429, {"retry-after": "30"})

    with pytest.raises(GitHubRateLimitError) as caught:
        fake.client(tmp_path).get(LANGUAGES)

    assert caught.value.reset_at is not None


def test_rate_limit_error_is_not_cached(tmp_path: Path) -> None:
    fake = FakeGitHub()
    fake.override(LANGUAGES, 403, {"x-ratelimit-remaining": "0"})
    with pytest.raises(GitHubRateLimitError):
        fake.client(tmp_path).get(LANGUAGES)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("status", [500, 503, 403, 401])
def test_other_errors_mean_github_is_unavailable(tmp_path: Path, status: int) -> None:
    fake = FakeGitHub()
    fake.override(LANGUAGES, status)

    with pytest.raises(GitHubUnavailableError):
        fake.client(tmp_path).get(LANGUAGES)


def test_network_failure_means_github_is_unavailable(tmp_path: Path) -> None:
    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no network")

    http = httpx.Client(base_url=BASE_URL, transport=httpx.MockTransport(fail))
    client = GitHubClient(http, cache_dir=tmp_path, cache_seconds=60)

    with pytest.raises(GitHubUnavailableError):
        client.get(LANGUAGES)


def test_token_is_sent_but_never_cached(tmp_path: Path) -> None:
    fake = FakeGitHub()

    fake.client(tmp_path, token="ghp_secret_test_token").get(LANGUAGES)

    assert fake.seen_headers[0]["Authorization"] == "Bearer ghp_secret_test_token"
    for file in tmp_path.iterdir():
        assert "ghp_secret_test_token" not in file.read_text(encoding="utf-8")


def test_no_token_sends_no_authorization(tmp_path: Path) -> None:
    fake = FakeGitHub()

    fake.client(tmp_path, token="").get(LANGUAGES)

    assert "Authorization" not in fake.seen_headers[0]


def test_forget_cached_user_deletes_only_that_users_answers(tmp_path: Path) -> None:
    fake = FakeGitHub()
    client = fake.client(tmp_path)
    client.get(LANGUAGES)
    client.get("/users/test-student/repos", {"type": "owner", "sort": "pushed", "per_page": 20})
    fake.responses["/repos/someone-else/app/languages"] = fake.responses[LANGUAGES]
    client.get("/repos/someone-else/app/languages")

    removed = forget_cached_user(tmp_path, "Test-Student")

    assert removed == 2
    assert len(list(tmp_path.iterdir())) == 1  # someone-else's answer stays


def test_forget_cached_user_without_a_cache_folder(tmp_path: Path) -> None:
    assert forget_cached_user(tmp_path / "missing", "test-student") == 0
