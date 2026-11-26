"""Finds skills in a CV's text (M4.2, System A: fixed rules, no AI).

`find_in_cv(text, index, cv_language=...)` returns one `CvFinding` per sentence that
names at least one skill: the evidence type, the exact quote, where it is, its language
and the skill ids. It doesn't judge the finding (`supports` / `weak`): that's M4.4.

How it works:

1. **Sections.** A line is a heading when, without its bullet, it is a known heading
   ("Skills", "Compétences techniques", "Projets"…, see `HEADINGS`), alone or followed
   by `:` and text ("Skills: Python, SQL"). The heading decides the evidence type of
   the lines under it: skills → `cv_skills_list`, projects → `cv_project`, and so on.
   Text before any heading (name, contact, a one-line profile) counts as `cv_summary`.
   Sections like hobbies or references are skipped.
2. **Sentences.** Each line is split after `.` `!` `?` `;`, so a long paragraph gives one
   quote per sentence, not one per paragraph.
3. **Skills.** The sentence's words are matched against the index, longest phrase first
   ("Spring Boot" before "Spring"), without overlaps. Words that are also ordinary words
   (`AMBIGUOUS`: "go", "rest", "vue", "tableau"…) only count in a skills list, or
   elsewhere when written with a capital letter ("REST", "Go").
4. **Quote.** The sentence exactly as written. Longer than 300 characters (the evidence
   model's limit), it is cut at word boundaries around the first skill and marked `…`.
   Its language is detected; a bare list of tools ("Python, SQL") gets the CV's language.

Location is `{"section": <heading as written, or None>, "line": <1-based line number>}`.
The extracted text has no page numbers, so there is no page (T-142).
"""

import re
from typing import Any, Literal

from pydantic import BaseModel

from app.db.models.sources import QUOTE_MAX_CHARS
from app.db.values import EvidenceType, SourceLanguage
from app.ingestion.language import detect_language
from app.skills.index import AMBIGUOUS, SkillIndex
from app.skills.normalize import normalize, tokens

CvSection = Literal[
    "skills", "summary", "experience", "project", "education", "certificate", "skip"
]

SECTION_TYPES: dict[CvSection, EvidenceType | None] = {
    "skills": "cv_skills_list",
    "summary": "cv_summary",
    "experience": "cv_experience",
    "project": "cv_project",
    "education": "cv_education",
    "certificate": "certificate",
    "skip": None,
}


def _headings(section: CvSection, words: str) -> dict[str, CvSection]:
    """One heading per line of `words`, written as `normalize` writes it (no accents)."""
    return {line.strip(): section for line in words.strip().splitlines()}


HEADINGS: dict[str, CvSection] = (
    _headings(
        "skills",
        """
        skills
        skill
        technical skills
        hard skills
        it skills
        tech stack
        technologies
        tools
        programming languages
        languages
        competences
        competence
        competences techniques
        competences informatiques
        connaissances informatiques
        informatique
        outils
        langages
        langages de programmation
        langues
        """,
    )
    | _headings(
        "summary",
        """
        summary
        professional summary
        profile
        about
        about me
        objective
        profil
        resume
        objectif
        a propos
        a propos de moi
        """,
    )
    | _headings(
        "experience",
        """
        experience
        experiences
        work experience
        professional experience
        employment
        internship
        internships
        volunteering
        volunteer experience
        experience professionnelle
        experiences professionnelles
        parcours professionnel
        stage
        stages
        benevolat
        """,
    )
    | _headings(
        "project",
        """
        project
        projects
        personal projects
        academic projects
        projet
        projets
        projets personnels
        projets academiques
        projets universitaires
        """,
    )
    | _headings(
        "education",
        """
        education
        academic background
        formation
        formations
        etudes
        diplomes
        cursus
        parcours academique
        """,
    )
    | _headings(
        "certificate",
        """
        certifications
        certification
        certificates
        certificats
        certificat
        """,
    )
    | _headings(
        "skip",
        """
        interests
        hobbies
        references
        contact
        centres d interet
        centre d interet
        loisirs
        """,
    )
)

_BULLETS = "•·▪◦*-–—> \t"
_SENTENCE_END = re.compile(r"(?<=[.!?;])\s+")
_ELLIPSIS = "…"


class CvFinding(BaseModel):
    type: EvidenceType
    quote: str
    location: dict[str, Any]
    language: SourceLanguage
    skill_ids: list[str]


def find_in_cv(text: str, index: SkillIndex, *, cv_language: str | None) -> list[CvFinding]:
    findings: list[CvFinding] = []
    section: CvSection = "summary"
    section_name: str | None = None
    for line_number, raw_line in enumerate(text.split("\n"), start=1):
        line = raw_line.strip()
        if not line:
            continue
        heading = _heading(line)
        if heading is not None:
            section_name, section, rest_starts = heading
            if not line[rest_starts:].strip():
                continue
        else:
            rest_starts = 0
        evidence_type = SECTION_TYPES[section]
        if evidence_type is None:
            continue

        position = 0
        for sentence in _SENTENCE_END.split(line):
            start = line.index(sentence, position)
            position = start + len(sentence)
            # The heading itself ("Skills:") is quoted but not searched for skills.
            searched = sentence[max(0, rest_starts - start) :]
            found = _skills_in(searched, index, in_skills_list=section == "skills")
            if not found:
                continue
            quote = _cut(sentence, found[0][1])
            findings.append(
                CvFinding(
                    type=evidence_type,
                    quote=quote,
                    location={"section": section_name, "line": line_number},
                    language=_language(quote, cv_language),
                    skill_ids=[skill_id for skill_id, _ in found],
                )
            )
    return findings


def _heading(line: str) -> tuple[str, CvSection, int] | None:
    """(heading as written, section, where the text after it starts) or None."""
    stripped = line.lstrip(_BULLETS)
    offset = len(line) - len(stripped)
    candidate, colon, _ = stripped.partition(":")
    section = HEADINGS.get(normalize(candidate))
    if section is None:
        return None
    rest_starts = offset + len(candidate) + len(colon) if colon else len(line)
    return candidate.strip(), section, rest_starts


def _skills_in(text: str, index: SkillIndex, *, in_skills_list: bool) -> list[tuple[str, str]]:
    """(skill id, original words) for each skill named in `text`, in order, no repeats."""
    words = tokens(text)
    found: dict[str, str] = {}
    i = 0
    while i < len(words):
        for size in range(min(index.max_words, len(words) - i), 0, -1):
            phrase = words[i : i + size]
            key = " ".join(part for _, part in phrase)
            skill_id = index.resolve_key(key)
            if skill_id is None:
                continue
            original = " ".join(word for word, _ in phrase)
            if key in AMBIGUOUS and not in_skills_list and original.islower():
                continue
            found.setdefault(skill_id, original)
            i += size
            break
        else:
            i += 1
    return list(found.items())


def _cut(sentence: str, first_match: str) -> str:
    """The sentence, or a window of it around `first_match` if it is too long."""
    if len(sentence) <= QUOTE_MAX_CHARS:
        return sentence
    room = QUOTE_MAX_CHARS - 2 * len(_ELLIPSIS)
    at = max(sentence.find(first_match.split()[0]), 0)
    start = max(0, min(at - room // 3, len(sentence) - room))
    end = min(len(sentence), start + room)
    if start > 0:
        start = sentence.find(" ", start) + 1 or start
    if end < len(sentence):
        end = sentence.rfind(" ", start, end) if " " in sentence[start:end] else end
    window = sentence[start:end].strip()
    return (_ELLIPSIS if start > 0 else "") + window + (_ELLIPSIS if end < len(sentence) else "")


def _language(quote: str, cv_language: str | None) -> SourceLanguage:
    detected = detect_language(quote)
    if detected == "other" and cv_language in ("en", "fr", "ar"):
        return cv_language  # type: ignore[return-value]
    return detected
