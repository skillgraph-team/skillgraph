"""System A's judgement of one evidence link (M4.4): `supports` or `weak`, with a reason
code, following docs/design/evidence-model.md section 3.2 with fixed rules and no AI.
The agents (Systems B and C) make the same judgement their own way (M6.3).

`judge(type, quote, location)` looks only at this one piece of evidence:

- **Skills list, summary:** supports (`named_in_list` / `named_in_summary`), unless the
  sentence says the person wants to learn it or is looking for it ("interested in",
  "looking for", « souhaite apprendre », « à la recherche d' ») → weak `wants_to_learn`.
- **CV experience or project, manual project:** weak `vague_mention` when the sentence is
  vague or passive ("familiar with", « notions de », a bare "Technologies: …" line);
  otherwise supports `concrete_work` when it says what was done (an action verb like
  "built", "wrote", « développé », « mise en place »); otherwise weak `vague_mention`.
- **Education, dependency, README:** always weak (`education_only`, `dependency_only`,
  `readme_only`): context only.
- **Repo language:** supports `language_share_ok` only if the share is ≥ 10 %, the repo is
  owned by the person and isn't a fork; otherwise weak `forked_repo`, `not_owned_repo` or
  `language_share_low`, checked in that order. **Repo code:** supports
  `code_uses_skill` unless forked or not owned.
- **Certificate:** supports `certificate_match` (the finder only links a skill the
  certificate names). **User added:** supports `added_by_user`. **Assessment:**
  supports `assessment_passed` if `location["passed"]`, else weak `assessment_failed`.

The phrase lists are matched after `normalize` (no accents, lowercase), as whole words.
They are English and French only (D-030).
"""

from typing import Any

from pydantic import BaseModel

from app.db.values import EvidenceType, Judgement
from app.skills.normalize import normalize
from app.skills.status_rules import language_link_ok


def _phrases(text: str) -> tuple[str, ...]:
    """One phrase per line, normalized like the quotes are."""
    return tuple(normalize(line) for line in text.strip().splitlines() if line.strip())


WANTS_TO_LEARN = _phrases(
    """
    interested in
    want to learn
    wants to learn
    would like to learn
    eager to learn
    keen to learn
    looking to learn
    currently learning
    looking for
    seeking
    souhaite apprendre
    envie d'apprendre
    j'aimerais apprendre
    intéressé par
    intéressée par
    en cours d'apprentissage
    à la recherche d'
    à la recherche de
    recherche un stage
    """
)

VAGUE = _phrases(
    """
    familiar with
    familiarity with
    exposure to
    exposed to
    basic knowledge
    knowledge of
    introduction to
    acquainted with
    awareness of
    tech stack
    technical stack
    technologies used
    tools used
    notions de
    notions en
    connaissances en
    connaissance de
    sensibilisation
    familiarisé avec
    familiarisée avec
    initiation à
    découverte de
    environnement technique
    stack technique
    technologies utilisées
    outils utilisés
    """
)

STARTS_VAGUE = _phrases(
    """
    technologies
    tools
    stack
    outils
    environnement
    """
)
"""A sentence that only lists tools, like "Technologies: React, Node.js"."""

ACTION_VERBS = _phrases(
    """
    built
    build
    building
    developed
    developing
    implemented
    created
    designed
    wrote
    written
    deployed
    automated
    tested
    migrated
    integrated
    trained
    analyzed
    analysed
    optimized
    optimised
    refactored
    configured
    maintained
    programmed
    coded
    shipped
    launched
    set up
    contributed
    développé
    développée
    développement d'
    développement de
    conçu
    conçue
    conception d'
    conception de
    réalisé
    réalisée
    réalisation d'
    réalisation de
    implémenté
    implémentée
    créé
    créée
    création d'
    création de
    mis en place
    mise en place
    déployé
    déployée
    écrit
    écrite
    automatisé
    testé
    intégré
    entraîné
    optimisé
    """
)


class Judged(BaseModel):
    judgement: Judgement
    reason_code: str


def _has(quote_key: str, phrases: tuple[str, ...]) -> bool:
    padded = f" {quote_key} "
    return any(f" {phrase} " in padded for phrase in phrases)


def _judged(judgement: Judgement, reason_code: str) -> Judged:
    return Judged(judgement=judgement, reason_code=reason_code)


def judge(type_: EvidenceType, quote: str, location: dict[str, Any]) -> Judged:
    key = normalize(quote)
    match type_:
        case "cv_skills_list" | "cv_summary":
            if _has(key, WANTS_TO_LEARN):
                return _judged("weak", "wants_to_learn")
            reason = "named_in_list" if type_ == "cv_skills_list" else "named_in_summary"
            return _judged("supports", reason)
        case "cv_experience" | "cv_project" | "manual_project":
            if _has(key, VAGUE) or key.split(" ", 1)[0] in STARTS_VAGUE:
                return _judged("weak", "vague_mention")
            if _has(key, ACTION_VERBS):
                return _judged("supports", "concrete_work")
            return _judged("weak", "vague_mention")
        case "cv_education":
            return _judged("weak", "education_only")
        case "repo_dependency":
            return _judged("weak", "dependency_only")
        case "repo_readme":
            return _judged("weak", "readme_only")
        case "repo_language" | "repo_code":
            if location.get("is_fork") is True:
                return _judged("weak", "forked_repo")
            if location.get("owned") is False:
                return _judged("weak", "not_owned_repo")
            if type_ == "repo_code":
                return _judged("supports", "code_uses_skill")
            if language_link_ok(location):
                return _judged("supports", "language_share_ok")
            return _judged("weak", "language_share_low")
        case "certificate":
            return _judged("supports", "certificate_match")
        case "user_added":
            return _judged("supports", "added_by_user")
        case "assessment":
            if location.get("passed") is True:
                return _judged("supports", "assessment_passed")
            return _judged("weak", "assessment_failed")
