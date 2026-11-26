"""Turns any spelling of a skill into one lookup key (M4.2), so "Postgres", "postgres"
and "POSTGRES" all look the same, and so do "développement web" and "developpement-web".

`normalize("Node.js")` gives `"node js"`. The steps, in order:

1. Unicode NFKD, then drop the combining marks it splits off. This removes French
   accents (é → e) and, for the Arabic display names, diacritics (تشكيل) and the hamza
   on alef (أ → ا).
2. Lowercase (`casefold`, which also handles letters like ß).
3. Split into words: letters, digits, `+` and `#` stay together (`c++`, `c#`); every
   other character (`. - / ' ,` …) separates words. Words are joined with one space.

`tokens(text)` gives the same words, each next to the original text it came from, so
the CV finder can check capital letters and quote the original.
"""

import re
import unicodedata

# `\w` doesn't include combining marks, so they are listed: accents written as a
# separate mark (U+0300-036F) and the Arabic diacritics (U+0610-061A, 064B-065F, 0670).
_MARK_RANGES = [(0x0300, 0x036F), (0x0610, 0x061A), (0x064B, 0x065F), (0x0670, 0x0670)]
_MARKS = "".join(f"{chr(first)}-{chr(last)}" for first, last in _MARK_RANGES)
_WORD = re.compile(rf"[\w+#{_MARKS}]+")


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    without_marks = "".join(char for char in decomposed if not unicodedata.combining(char))
    return without_marks.casefold()


def tokens(text: str) -> list[tuple[str, str]]:
    """Each word of `text` as (original, key part). Underscores count as separators."""
    out = []
    for match in _WORD.finditer(text.replace("_", " ")):
        original = match.group()
        out.append((original, _fold(original)))
    return out


def normalize(text: str) -> str:
    return " ".join(key for _, key in tokens(text))
