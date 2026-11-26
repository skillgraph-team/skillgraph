"""A fake GitHub for tests (M3.6): answers from saved responses, never the network.

`FakeGitHub()` loads `test_student.json` (made-up account `test-student`). Use
`fake.client(cache_dir)` to get a real `GitHubClient` whose requests go to the fake.

- `fake.requests` lists the paths asked for, to check how many requests were made.
- `fake.override(key, status, headers)` changes one answer, e.g. to a rate-limit error.
- A request with the saved ETag in If-None-Match gets 304, as on the real GitHub.
- Any request that has no saved answer fails the test (nothing goes to the live API).
"""

import json
from pathlib import Path
from typing import Any

import httpx

from app.ingestion.github_client import GitHubClient

SAVED = Path(__file__).resolve().parent / "test_student.json"
BASE_URL = "https://api.github.com"


def key_of(request: httpx.Request) -> str:
    query = (
        "&".join(sorted(str(request.url.query, "ascii").split("&"))) if request.url.query else ""
    )
    return request.url.path + (f"?{query}" if query else "")


class FakeGitHub:
    def __init__(self) -> None:
        self.responses: dict[str, dict[str, Any]] = json.loads(SAVED.read_text(encoding="utf-8"))[
            "responses"
        ]
        self.requests: list[str] = []
        self.seen_headers: list[httpx.Headers] = []

    def override(self, key: str, status: int, headers: dict[str, str] | None = None) -> None:
        self.responses[key] = {"status": status, "headers": headers or {}, "body": None}

    def handle(self, request: httpx.Request) -> httpx.Response:
        key = key_of(request)
        self.requests.append(key)
        self.seen_headers.append(request.headers)
        if key not in self.responses:
            raise AssertionError(f"unexpected GitHub request {key} (tests never use the live API)")
        saved = self.responses[key]
        etag = saved["headers"].get("ETag")
        if etag and request.headers.get("If-None-Match") == etag:
            return httpx.Response(304, headers={"ETag": etag})
        if saved["body"] is None:
            return httpx.Response(saved["status"], headers=saved["headers"])
        return httpx.Response(saved["status"], headers=saved["headers"], json=saved["body"])

    def client(
        self,
        cache_dir: Path,
        *,
        cache_seconds: int = 3600,
        token: str | None = None,
        clock: Any = None,
    ) -> GitHubClient:
        http = httpx.Client(base_url=BASE_URL, transport=httpx.MockTransport(self.handle))
        extra = {"clock": clock} if clock else {}
        return GitHubClient(
            http, cache_dir=cache_dir, cache_seconds=cache_seconds, token=token, **extra
        )
