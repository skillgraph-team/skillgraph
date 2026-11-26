"""The pieces the finders share for reading prose (M4.2, M4.3): split a line into
sentences, find the skills a sentence names, cut a quote to the evidence model's
length, and pick the quote's language.

Matching (`skills_in`): the sentence's words are matched against the skill index,
longest phrase first ("Spring Boot" before "Spring"), without overlaps. Words that are
also ordinary words (`AMBIGUOUS` in app/skills/index.py: "go", "rest", "vue"…) only
count in a skills list, or elsewhere when written with a capital letter ("REST", "Go").
"""

import re
from typing import cast

from app.db.models.sources import QUOTE_MAX_CHARS
from app.db.values import SourceLanguage
from app.ingestion.language import detect_language
from app.skills.index import AMBIGUOUS, SkillIndex
from app.skills.normalize import tokens

_SENTENCE_END = re.compile(r"(?<=[.!?;])\s+")
ELLIPSIS = "…"


def sentences(line: str) -> list[tuple[int, str]]:
    """Each sentence of `line` with where it starts. Splits after `.` `!` `?` `;`."""
    out = []
    position = 0
    for sentence in _SENTENCE_END.split(line):
        start = line.index(sentence, position)
        position = start + len(sentence)
        out.append((start, sentence))
    return out


def skills_in(text: str, index: SkillIndex, *, in_skills_list: bool) -> list[tuple[str, str]]:
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


def cut_quote(sentence: str, first_match: str) -> str:
    """The sentence, or a window of it around `first_match` if it is too long, cut at
    word boundaries and marked with `…`."""
    if len(sentence) <= QUOTE_MAX_CHARS:
        return sentence
    room = QUOTE_MAX_CHARS - 2 * len(ELLIPSIS)
    at = max(sentence.find(first_match.split()[0]), 0)
    start = max(0, min(at - room // 3, len(sentence) - room))
    end = min(len(sentence), start + room)
    if start > 0:
        start = sentence.find(" ", start) + 1 or start
    if end < len(sentence) and " " in sentence[start:end]:
        end = sentence.rfind(" ", start, end)
    window = sentence[start:end].strip()
    return (ELLIPSIS if start > 0 else "") + window + (ELLIPSIS if end < len(sentence) else "")


def quote_language(quote: str, fallback: str | None) -> SourceLanguage:
    """The quote's detected language; a bare list of tools ("Python, SQL") has none, so
    it gets the source's language instead."""
    detected = detect_language(quote)
    if detected == "other" and fallback in ("en", "fr", "ar"):
        return cast(SourceLanguage, fallback)
    return detected
