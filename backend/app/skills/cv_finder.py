"""Finds skills in a CV's text (M4.2, System A: fixed rules, no AI).

`find_in_cv(text, index, cv_language=...)` returns one `Finding` per sentence that
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
3. **Skills.** Matched as described in app/skills/matching.py; in a skills list, short
   words that are also ordinary words ("go", "rest") count even in lowercase.
4. **Quote.** The sentence exactly as written. Longer than 300 characters (the evidence
   model's limit), it is cut at word boundaries around the first skill and marked `…`.
   Its language is detected; a bare list of tools ("Python, SQL") gets the CV's language.

Location is `{"section": <heading as written, or None>, "line": <1-based line number>}`.
The extracted text has no page numbers, so there is no page (T-142).
"""

from typing import Literal

from app.db.values import EvidenceType
from app.skills.findings import Finding
from app.skills.index import SkillIndex
from app.skills.matching import cut_quote, quote_language, sentences, skills_in
from app.skills.normalize import normalize

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


def find_in_cv(text: str, index: SkillIndex, *, cv_language: str | None) -> list[Finding]:
    findings: list[Finding] = []
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

        for start, sentence in sentences(line):
            # The heading itself ("Skills:") is quoted but not searched for skills.
            searched = sentence[max(0, rest_starts - start) :]
            found = skills_in(searched, index, in_skills_list=section == "skills")
            if not found:
                continue
            quote = cut_quote(sentence, found[0][1])
            findings.append(
                Finding(
                    type=evidence_type,
                    quote=quote,
                    location={"section": section_name, "line": line_number},
                    language=quote_language(quote, cv_language),
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
