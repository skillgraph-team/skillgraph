"""The skill index (M4.2): every way of writing a skill, turned into a key by
`normalize`, mapped to the skill's id. `index.resolve("Postgres")` gives `"postgresql"`.

What it holds for each skill: the id, the English, French and Arabic names, and every
alias from aliases.csv. Two different skills with the same key are refused
(`SkillIndexCollisionError`), because then a word would be guessed instead of known.

Build it from the database (`load_index`, what the app uses) or straight from the CSV
files (`SkillIndex.from_csv`, for tests and scripts that run without a database).

`AMBIGUOUS` lists keys that are also ordinary English or French words ("go", "rest",
"vue", "tableau"…). The CV finder only trusts them in a skills list, or written with a
capital letter (see app/skills/cv_finder.py).
"""

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Skill, SkillAlias
from app.skills.normalize import normalize
from app.skills.taxonomy import DATA_DIR, AliasRow, SkillRow, read_taxonomy

# A plain string split into words is easier to read and edit than a long list.
# Each entry is a key as `normalize` writes it; a test checks they all exist.
AMBIGUOUS = frozenset(
    """
    go c r ai ia tal os ts tf ml db bi rag elk iam poo
    rest node dash lambda unity unreal express spring swift rails torch spark
    helm rust ruby dart oracle react vue angular flutter bash shell word excel tableau
    jest cypress postman playwright notebooks transformers snowflake looker sass tailwind
    bootstrap solidity assembly confluence embedded networking reseaux supervision
    collaboration
    """.split()  # noqa: SIM905
) | {"red hat"}  # keys with a space can't go in the split string above


class SkillIndexCollisionError(Exception):
    """Two different skills have the same key."""

    def __init__(self, key: str, first: str, second: str) -> None:
        super().__init__(f"{key!r} is both {first} and {second}")
        self.key, self.first, self.second = key, first, second


class SkillIndex:
    def __init__(self, keys: dict[str, str]) -> None:
        self._keys = keys
        self.max_words = max((len(key.split()) for key in keys), default=1)
        """The most words any key has; the CV finder never looks at longer phrases."""

    @classmethod
    def from_rows(cls, skills: Iterable[SkillRow], aliases: Iterable[AliasRow]) -> "SkillIndex":
        keys: dict[str, str] = {}

        def add(text: str | None, skill_id: str) -> None:
            key = normalize(text or "")
            if not key:
                return
            if keys.setdefault(key, skill_id) != skill_id:
                raise SkillIndexCollisionError(key, keys[key], skill_id)

        for skill in skills:
            for text in (skill.id, skill.name_en, skill.name_fr, skill.name_ar):
                add(text, skill.id)
        for alias in aliases:
            add(alias.alias, alias.skill_id)
        return cls(keys)

    @classmethod
    def from_csv(cls) -> "SkillIndex":
        data = read_taxonomy(DATA_DIR)
        return cls.from_rows(data.skills, data.aliases)

    def resolve(self, text: str) -> str | None:
        """The id of the skill `text` names, or None if it names none."""
        return self._keys.get(normalize(text))

    def resolve_key(self, key: str) -> str | None:
        """Like `resolve`, for text that is already a key."""
        return self._keys.get(key)


def load_index(session: Session) -> SkillIndex:
    """The index of the skill list as loaded in the database (app/skills/taxonomy.py)."""
    skills = [
        SkillRow(
            id=skill.id,
            name_en=skill.name_en,
            name_fr=skill.name_fr or "",
            name_ar=skill.name_ar or "",
            category=skill.category or "",
        )
        for skill in session.scalars(select(Skill))
    ]
    aliases = [
        AliasRow(alias=alias.alias, skill_id=alias.skill_id)
        for alias in session.scalars(select(SkillAlias))
    ]
    return SkillIndex.from_rows(skills, aliases)
