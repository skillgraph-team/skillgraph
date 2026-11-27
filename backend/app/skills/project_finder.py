"""Finds skills in a project the user typed into their profile (M4.10).

`find_in_project(title, description, index, project_id=...)` matches the title and each
sentence of the description like CV prose (app/skills/matching.py) and returns one
`manual_project` finding per sentence naming skills. `manual_project` is a work type: the
judgement (M4.4) applies the same test as a CV project, concrete work or vague mention.

Location: `{"project_id": ..., "field": "title" | "description", "line": n}`, the line
counted inside that field. A quote's language falls back to the whole project's.
"""

from app.ingestion.language import detect_language
from app.skills.findings import Finding
from app.skills.index import SkillIndex
from app.skills.matching import cut_quote, quote_language, sentences, skills_in


def find_in_project(
    title: str, description: str, index: SkillIndex, *, project_id: str
) -> list[Finding]:
    project_language = detect_language(f"{title}\n{description}")
    findings = []
    for field, text in (("title", title), ("description", description)):
        for line_number, raw_line in enumerate(text.split("\n"), start=1):
            line = raw_line.strip()
            for _, sentence in sentences(line) if line else []:
                found = skills_in(sentence, index, in_skills_list=False)
                if not found:
                    continue
                quote = cut_quote(sentence, found[0][1])
                findings.append(
                    Finding(
                        type="manual_project",
                        quote=quote,
                        location={"project_id": project_id, "field": field, "line": line_number},
                        language=quote_language(quote, project_language),
                        skill_ids=[skill_id for skill_id, _ in found],
                    )
                )
    return findings
