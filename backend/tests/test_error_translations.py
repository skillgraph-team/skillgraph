"""Every error code the backend sends has words on screen (docs/design/localization.md §4).

The frontend turns `{"detail": {"code": "<code>"}}` into the text at `errors.<code>`. This
test finds the codes in app/ by their usual spellings and checks en.json has each one.
fr.json and ar.json are checked against en.json by the frontend's `npm run check`.
"""

import json
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"
EN = Path(__file__).resolve().parents[2] / "frontend" / "src" / "locales" / "en.json"

# `code = "x"` (domain exceptions), `{"code": "x"` (HTTPException details), and the two
# helpers `_unauthorized("x")` / `_error(status..., "x")`.
_CODE = re.compile(
    r'code = "([a-z_]+)"|"code": "([a-z_]+)"|_unauthorized\("([a-z_]+)"\)'
    r'|_error\([^()]*, "([a-z_]+)"\)'
)


def backend_codes() -> set[str]:
    codes: set[str] = set()
    for path in APP.rglob("*.py"):
        for match in _CODE.finditer(path.read_text(encoding="utf-8")):
            codes.add(next(group for group in match.groups() if group))
    return codes


def test_the_scan_finds_the_known_codes() -> None:
    known = {"email_taken", "wrong_password", "token_expired", "file_too_large"}
    assert known <= backend_codes()


def test_every_backend_error_code_has_an_english_text() -> None:
    errors = json.loads(EN.read_text(encoding="utf-8")).get("errors", {})

    assert sorted(backend_codes() - set(errors)) == []
