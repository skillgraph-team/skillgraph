"""Status and confidence from a skill's evidence links (M4.4): docs/design/evidence-model.md
sections 4, 5 and 7, exactly. Used by all three systems. Rules (System A) or an agent
judge each link (`supports` / `weak`); this module turns the judged links into the
result, so no system picks a status freely.

`compute(links)` gives status, confidence and a reason:

- **Status**, the highest step reached:
  - `assessed`: an `assessment` link that supports;
  - `demonstrated`: a work-type link that supports;
  - `claimed`: a claim-type link that supports, or a weak `cv_experience` /
    `cv_project` link that isn't inferred (a vague mention is still the person's claim);
  - `unverified`: anything else, including no links at all.
- **Confidence**: count the supporting links of a work, claim or assessment type, once
  per distinct (source, type). 0 → low, 1 → medium, 2 or more → high.
- **Reason**: a code plus the evidence id, never a sentence. It's the reason code of
  the first link that set the status (or `no_evidence`). The frontend turns it into
  text in the user's language.

`validate(links, status, confidence)` is the guardrail check of section 7, for results
an agent reports. It raises `RuleViolationError` with a code.
"""

from typing import Any

from pydantic import BaseModel

from app.db.values import Confidence, EvidenceType, Judgement, Status

WORK_TYPES: frozenset[str] = frozenset(
    {"cv_experience", "cv_project", "repo_language", "repo_code", "manual_project"}
)
CLAIM_TYPES: frozenset[str] = frozenset(
    {"cv_skills_list", "cv_summary", "certificate", "user_added"}
)
CONTEXT_TYPES: frozenset[str] = frozenset({"cv_education", "repo_dependency", "repo_readme"})
ASSESSMENT_TYPE = "assessment"
VAGUE_CLAIM_TYPES: frozenset[str] = frozenset({"cv_experience", "cv_project"})
INFERRED = "inferred_from_related"

LANGUAGE_SHARE_MIN = 10.0
"""A `repo_language` link supports only from this share (%) up (section 3.2)."""

STATUS_ORDER: dict[str, int] = {"unverified": 0, "claimed": 1, "demonstrated": 2, "assessed": 3}
CONFIDENCE_ORDER: dict[str, int] = {"low": 0, "medium": 1, "high": 2}


class Link(BaseModel):
    """One judged evidence link, with what the rules need to know about its evidence."""

    evidence_id: str
    source_id: str | None
    type: EvidenceType
    judgement: Judgement
    reason_code: str
    location: dict[str, Any] = {}


class SkillReason(BaseModel):
    code: str
    evidence_id: str | None


class SkillResult(BaseModel):
    status: Status
    confidence: Confidence
    reason: SkillReason


class RuleViolationError(Exception):
    """A reported result breaks the evidence model (section 7). `code` says which rule."""

    def __init__(self, code: str, evidence_id: str | None = None) -> None:
        super().__init__(code if evidence_id is None else f"{code} ({evidence_id})")
        self.code = code
        self.evidence_id = evidence_id


def _supports(link: Link, types: frozenset[str]) -> bool:
    return link.judgement == "supports" and link.type in types


def _is_vague_claim(link: Link) -> bool:
    return (
        link.judgement == "weak" and link.type in VAGUE_CLAIM_TYPES and link.reason_code != INFERRED
    )


def compute(links: list[Link]) -> SkillResult:
    assessed = [link for link in links if _supports(link, frozenset({ASSESSMENT_TYPE}))]
    work = [link for link in links if _supports(link, WORK_TYPES)]
    claims = [link for link in links if _supports(link, CLAIM_TYPES)] + [
        link for link in links if _is_vague_claim(link)
    ]

    status: Status
    deciding: Link | None
    if assessed:
        status, deciding = "assessed", assessed[0]
    elif work:
        status, deciding = "demonstrated", work[0]
    elif claims:
        status, deciding = "claimed", claims[0]
    else:
        status = "unverified"
        deciding = links[0] if links else None

    counted = WORK_TYPES | CLAIM_TYPES | {ASSESSMENT_TYPE}
    independent = {
        (link.source_id, link.type) for link in links if _supports(link, frozenset(counted))
    }
    confidence: Confidence = (
        "low" if not independent else "medium" if len(independent) == 1 else "high"
    )
    if status == "unverified":
        confidence = "low"  # always true already; the database also checks it

    reason = (
        SkillReason(code=deciding.reason_code, evidence_id=deciding.evidence_id)
        if deciding
        else SkillReason(code="no_evidence", evidence_id=None)
    )
    return SkillResult(status=status, confidence=confidence, reason=reason)


def language_link_ok(location: dict[str, Any]) -> bool:
    """Section 3.2: share ≥ 10 %, repo owned by the person, not a fork."""
    return (
        float(location.get("share") or 0) >= LANGUAGE_SHARE_MIN
        and location.get("owned") is True
        and location.get("is_fork") is False
    )


def validate(
    links: list[Link], status: Status, confidence: Confidence, *, allow_assessed: bool = False
) -> None:
    """Section 7's guardrails. Guardrail 2 (only cite evidence given to the agent) is
    the agent runtime's job (M5), since this function only sees the links."""
    if not links:
        raise RuleViolationError("no_links")
    for link in links:
        if _supports(link, CONTEXT_TYPES):
            raise RuleViolationError("supports_on_context_type", link.evidence_id)
        if _supports(link, frozenset({"repo_language"})) and not language_link_ok(link.location):
            raise RuleViolationError("repo_language_conditions", link.evidence_id)
    if status == "assessed" and not allow_assessed:
        raise RuleViolationError("assessed_not_allowed")  # D-014: nothing is assessed in the MVP
    expected = compute(links)
    if status != expected.status:
        raise RuleViolationError("status_mismatch")
    if confidence != expected.confidence:
        raise RuleViolationError("confidence_mismatch")
