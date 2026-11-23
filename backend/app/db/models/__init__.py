"""All database models (tables). Import models from here: `from app.db.models import User`.

Every model must be imported below, or Alembic's autogenerate won't see it.
Diagram and notes: docs/design/schema.md.
"""

from app.db.base import Base
from app.db.models.agent_runs import AgentMessage, AgentRun
from app.db.models.opportunities import Match, Opportunity, OpportunityRequirement
from app.db.models.skills import Skill, SkillAlias, SkillRelation
from app.db.models.sources import Evidence, Source
from app.db.models.user_skills import UserSkill, UserSkillEvidence
from app.db.models.users import Education, Experience, ManualProject, Profile, User

__all__ = [
    "AgentMessage",
    "AgentRun",
    "Base",
    "Education",
    "Evidence",
    "Experience",
    "ManualProject",
    "Match",
    "Opportunity",
    "OpportunityRequirement",
    "Profile",
    "Skill",
    "SkillAlias",
    "SkillRelation",
    "Source",
    "User",
    "UserSkill",
    "UserSkillEvidence",
]
