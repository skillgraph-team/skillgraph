"""A small client for GitHub's public REST API (M3.6), with a response cache and clear
errors for the rate limit. Only GET requests, only public data (D-009).

`GitHubClient.get(path)` returns the JSON body, or None when GitHub has nothing there
(404 not found, 409 empty repository, 204 no content). It raises:
- `GitHubRateLimitError` when GitHub's request limit is used up (`reset_at` says when
  it refills). We never wait for it: the limit can take up to an hour to refill.
- `GitHubUnavailableError` when GitHub can't be reached or answers with an error.

**Cache.** Every answer is saved as a JSON file in `cache_dir`, named after a hash of
the URL. Within `cache_seconds` the saved answer is used and GitHub isn't asked at all.
After that, the request carries the saved ETag (a version tag GitHub sent with the
answer). If nothing changed, GitHub replies 304 "not modified" and we reuse the saved
body. GitHub's docs say a 304 doesn't count against the limit. The cache holds public
data only, never the token.

Tests pass an `httpx.Client` with a fake transport (saved answers), so they never
reach the network.
"""

import hashlib
import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 15.0
_MISSING = (404, 409, 204, 451)
"""Not found, empty repository, no content, blocked for legal reasons: "nothing there"."""


class GitHubError(Exception):
    """Base class. `code` is what the API sends back."""

    code = "github_error"


class GitHubRateLimitError(GitHubError):
    code = "github_rate_limited"

    def __init__(self, reset_at: datetime | None) -> None:
        super().__init__("GitHub rate limit reached")
        self.reset_at = reset_at


class GitHubUnavailableError(GitHubError):
    code = "github_unavailable"


class GitHubClient:
    def __init__(
        self,
        http: httpx.Client,
        *,
        cache_dir: Path,
        cache_seconds: int,
        token: str | None = None,
        clock: Any = time.time,
    ) -> None:
        self._http = http
        self._cache_dir = cache_dir
        self._cache_seconds = cache_seconds
        self._token = token or None
        self._clock = clock  # replaced in tests to pretend time has passed

    def get(self, path: str, params: dict[str, str | int] | None = None) -> Any:
        url = str(self._http.build_request("GET", path, params=params).url)
        cached = self._read_cache(url)
        if cached and self._clock() - cached["saved_at"] < self._cache_seconds:
            return cached["body"]

        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        if cached and cached.get("etag"):
            headers["If-None-Match"] = cached["etag"]
        try:
            response = self._http.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
        except httpx.HTTPError as error:
            logger.warning("GitHub request failed: %s", type(error).__name__)
            raise GitHubUnavailableError from error

        if response.status_code == 304 and cached:
            body = cached["body"]
        elif response.status_code == 200:
            body = response.json()
        elif response.status_code in _MISSING:
            body = None
        elif _is_rate_limited(response):
            raise GitHubRateLimitError(_reset_time(response))
        else:
            logger.warning("GitHub answered %s for a request", response.status_code)
            raise GitHubUnavailableError
        self._write_cache(url, body, response.headers.get("ETag"))
        return body

    # --- cache files -----------------------------------------------------------

    def _cache_file(self, url: str) -> Path:
        return self._cache_dir / f"{hashlib.sha256(url.encode()).hexdigest()}.json"

    def _read_cache(self, url: str) -> dict[str, Any] | None:
        path = self._cache_file(url)
        if not path.exists():
            return None
        try:
            entry: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None  # a broken cache file is just ignored and rewritten
        return entry

    def _write_cache(self, url: str, body: Any, etag: str | None) -> None:
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        entry = {"url": url, "saved_at": self._clock(), "etag": etag, "body": body}
        self._cache_file(url).write_text(json.dumps(entry), encoding="utf-8")


def _is_rate_limited(response: httpx.Response) -> bool:
    """GitHub signals the limit with 403 or 429, plus either "0 requests left" or a
    Retry-After header (its "secondary" limit for bursts)."""
    if response.status_code not in (403, 429):
        return False
    return response.headers.get("x-ratelimit-remaining") == "0" or (
        "retry-after" in response.headers
    )


def _reset_time(response: httpx.Response) -> datetime | None:
    if "retry-after" in response.headers:
        try:
            return datetime.fromtimestamp(time.time() + int(response.headers["retry-after"]), UTC)
        except ValueError:
            return None
    try:
        return datetime.fromtimestamp(int(response.headers["x-ratelimit-reset"]), UTC)
    except (KeyError, ValueError):
        return None


def forget_cached_user(cache_dir: Path, username: str) -> int:
    """Delete the saved answers about one GitHub user: their repo list and their repos
    (M3.9: account deletion and withdrawn consent). Returns how many files went."""
    if not cache_dir.exists():
        return 0
    prefixes = (f"/users/{username.lower()}/", f"/repos/{username.lower()}/")
    removed = 0
    for path in cache_dir.glob("*.json"):
        try:
            url = json.loads(path.read_text(encoding="utf-8")).get("url", "")
        except (OSError, ValueError):
            url = ""  # unreadable: can't tell whose it is, so delete it to be safe
        if not url or urlsplit(url).path.lower().startswith(prefixes):
            path.unlink(missing_ok=True)
            removed += 1
    return removed
