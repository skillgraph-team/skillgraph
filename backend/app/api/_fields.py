"""Input field types shared by the profile endpoints (M3.3).

- `ShortText` / `LongText`: required, trimmed, 1–200 / 1–5000 characters.
- `OptionalShortText` / `OptionalLongText`: the same but may be null; blank becomes null.
- `WebUrl`: an http:// or https:// address, so profiles can't hold `javascript:` links.
- `DateRange`: a base model that refuses an end date before the start date.

Invalid input gets FastAPI's standard 422 answer (T-067).
"""

from datetime import date
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

SHORT = 200
LONG = 5000


def _blank_to_none(value: str | None) -> str | None:
    return value or None


ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=SHORT)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=LONG)]
OptionalShortText = Annotated[
    Annotated[str, StringConstraints(strip_whitespace=True, max_length=SHORT)] | None,
    AfterValidator(_blank_to_none),
]
OptionalLongText = Annotated[
    Annotated[str, StringConstraints(strip_whitespace=True, max_length=LONG)] | None,
    AfterValidator(_blank_to_none),
]
WebUrl = Annotated[str, Field(max_length=2048, pattern=r"^https?://\S+$")]
Position = Annotated[int, Field(ge=0, le=10_000)]


class EntryIn(BaseModel):
    """Base of every entry body: unknown fields refused, optional `position`
    (left out = new entries go last, updated entries keep their place)."""

    model_config = ConfigDict(extra="forbid")

    position: Position | None = None


class DateRange(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def _end_not_before_start(self) -> Self:
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date is before start_date")
        return self
