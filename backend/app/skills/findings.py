"""What every finder returns (M4.2, M4.3): one `Finding` per piece of a source that names
skills. A service turns each finding into an `evidence` row
(app/services/evidence_records.py); the skill ids go to the linking step (M4.5).
"""

from typing import Any

from pydantic import BaseModel

from app.db.values import EvidenceType, SourceLanguage


class Finding(BaseModel):
    type: EvidenceType
    quote: str
    """The exact text, at most 300 characters, never translated."""
    location: dict[str, Any]
    """Where it is: CV section and line, or repo, file path and line (evidence model §6)."""
    language: SourceLanguage
    skill_ids: list[str]
    """The skills it names, in the order they appear, without repeats."""
