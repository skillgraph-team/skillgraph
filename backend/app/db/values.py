"""The fixed lists of allowed values stored in the database (D-019: text + CHECK).

This is the one place these lists live. The models turn each list into a CHECK
constraint, and pydantic models can use the `Literal` types. The evidence values
come from docs/design/evidence-model.md (D-006); change them only with the owner.

Changing a list here needs a new migration (autogenerate does NOT notice CHECK changes:
write the `op.drop_constraint` / `op.create_check_constraint` lines by hand).
"""

from typing import Literal, get_args

Language = Literal["en", "fr", "ar"]
"""Languages the app works in (D-012): user's preferred language, agent output."""

SourceLanguage = Literal["en", "fr", "ar", "other"]
"""Detected language of a CV, repo text, quote or posting. Code counts as `other`."""

SourceKind = Literal["cv", "github_repo", "certificate", "manual_project"]

EvidenceType = Literal[
    "cv_skills_list",
    "cv_summary",
    "cv_experience",
    "cv_project",
    "cv_education",
    "certificate",
    "repo_language",
    "repo_dependency",
    "repo_code",
    "repo_readme",
    "manual_project",
    "user_added",
    "assessment",
]

Judgement = Literal["supports", "weak"]
Status = Literal["unverified", "claimed", "demonstrated", "assessed"]
Confidence = Literal["low", "medium", "high"]

System = Literal["rules", "single_agent", "multi_agent"]
"""Which of the three compared systems produced a result (A, B, C)."""

RunStatus = Literal["running", "succeeded", "failed", "stopped"]
"""`stopped` = a limit (steps, tokens, time) was reached (M5.4)."""

OpportunityKind = Literal["internship", "job"]
Importance = Literal["required", "nice_to_have"]


def values(literal: object) -> tuple[str, ...]:
    """The allowed strings of one of the types above, e.g. `values(Status)`."""
    return get_args(literal)
