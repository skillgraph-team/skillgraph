"""The skill list (taxonomy), shared by everyone: skills, their other names, and which
skill belongs under which. Filled from `app/skills/data/*.csv` (M4.1); not personal data.
"""

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Skill(Base):
    """`id` is the readable id from skills.csv (`postgresql`, `node.js`, `c++`).
    Names in the three languages (D-019); French and Arabic come in M4.9."""

    __tablename__ = "skills"
    __table_args__ = (CheckConstraint(r"id ~ '^[a-z0-9][a-z0-9.+#_-]*$'", name="id_slug"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name_en: Mapped[str]
    name_fr: Mapped[str | None]
    name_ar: Mapped[str | None]
    category: Mapped[str | None]


class SkillAlias(Base):
    """Another name for a skill ("postgres" → postgresql). Stored lowercase, so lookups
    lowercase the text first; each alias points to exactly one skill."""

    __tablename__ = "skill_aliases"
    __table_args__ = (CheckConstraint("alias = lower(alias)", name="alias_lowercase"),)

    alias: Mapped[str] = mapped_column(String(100), primary_key=True)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True)


class SkillRelation(Base):
    """`child_id` belongs under `parent_id` (postgresql → sql → databases)."""

    __tablename__ = "skill_relations"
    __table_args__ = (CheckConstraint("child_id <> parent_id", name="not_self"),)

    child_id: Mapped[str] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    parent_id: Mapped[str] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True, index=True
    )
