"""Reads the skill list CSVs (app/skills/data/, see its README) and loads them into the
`skills`, `skill_aliases` and `skill_relations` tables (M4.2).

Run it after changing a CSV, and once on a new database:

    cd backend && uv run python -m app.skills.taxonomy

Loading is safe to repeat: the database ends up matching the CSVs exactly. Skills are
updated in place (their ids never change), aliases and parent links are replaced, and
skills that left the CSV are deleted. A skill that left the CSV but is still on
someone's profile or in a posting's requirements is not deleted: `SkillInUseError` is
raised before anything changes (the database would refuse anyway, T-055).

Like the services, `load_taxonomy` flushes but never commits; the command commits.
"""

import csv
from pathlib import Path

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import OpportunityRequirement, Skill, SkillAlias, SkillRelation, UserSkill

DATA_DIR = Path(__file__).resolve().parent / "data"


class SkillRow(BaseModel):
    id: str
    name_en: str
    name_fr: str
    name_ar: str
    category: str


class AliasRow(BaseModel):
    alias: str
    skill_id: str


class RelationRow(BaseModel):
    child_id: str
    parent_id: str


class Taxonomy(BaseModel):
    skills: list[SkillRow]
    aliases: list[AliasRow]
    relations: list[RelationRow]


class LoadCounts(BaseModel):
    skills: int
    aliases: int
    relations: int
    removed: int


class SkillInUseError(Exception):
    """Skills that left the CSV but are still used, so they can't be deleted.
    Raised by the command, never sent by the API, so it has no error code."""

    def __init__(self, skill_ids: list[str]) -> None:
        super().__init__(f"still used: {', '.join(skill_ids)}")
        self.skill_ids = skill_ids


def _rows[T: BaseModel](path: Path, model: type[T]) -> list[T]:
    with path.open(encoding="utf-8", newline="") as f:
        return [model.model_validate(row) for row in csv.DictReader(f)]


def read_taxonomy(data_dir: Path = DATA_DIR) -> Taxonomy:
    return Taxonomy(
        skills=_rows(data_dir / "skills.csv", SkillRow),
        aliases=_rows(data_dir / "aliases.csv", AliasRow),
        relations=_rows(data_dir / "relations.csv", RelationRow),
    )


def load_taxonomy(session: Session, data: Taxonomy | None = None) -> LoadCounts:
    data = data or read_taxonomy()
    wanted = {row.id: row for row in data.skills}
    existing = {skill.id: skill for skill in session.scalars(select(Skill))}

    removed = sorted(set(existing) - set(wanted))
    used_by_profiles = session.scalars(
        select(UserSkill.skill_id).where(UserSkill.skill_id.in_(removed))
    )
    used_by_postings = session.scalars(
        select(OpportunityRequirement.skill_id).where(OpportunityRequirement.skill_id.in_(removed))
    )
    in_use = sorted({*used_by_profiles, *(skill_id for skill_id in used_by_postings if skill_id)})
    if in_use:
        raise SkillInUseError(in_use)

    session.execute(delete(SkillAlias))
    session.execute(delete(SkillRelation))
    for skill_id in removed:
        session.delete(existing[skill_id])
    for row in data.skills:
        skill = existing.get(row.id) or Skill(id=row.id)
        skill.name_en, skill.name_fr, skill.name_ar = row.name_en, row.name_fr, row.name_ar
        skill.category = row.category
        session.add(skill)
    session.flush()
    session.add_all(SkillAlias(alias=row.alias, skill_id=row.skill_id) for row in data.aliases)
    session.add_all(
        SkillRelation(child_id=row.child_id, parent_id=row.parent_id) for row in data.relations
    )
    session.flush()
    return LoadCounts(
        skills=len(data.skills),
        aliases=len(data.aliases),
        relations=len(data.relations),
        removed=len(removed),
    )


def main() -> None:
    from app.db.session import SessionLocal  # here, so importing this module needs no database

    with SessionLocal() as session:
        counts = load_taxonomy(session)
        session.commit()
    print(
        f"skills: {counts.skills}, aliases: {counts.aliases}, "
        f"parent links: {counts.relations}, removed: {counts.removed}"
    )


if __name__ == "__main__":
    main()
