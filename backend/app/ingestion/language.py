"""Guesses which language a CV is written in: `en`, `fr`, `ar`, or `other` when unsure.

No library and no LLM: CVs in this app are in one of three very different languages,
so two simple signals are enough (T-084):

1. **Arabic letters.** If at least 30 % of the letters are Arabic, the CV is Arabic.
   Not 50 %: Arabic CVs are full of tool names in Latin letters (Python, PostgreSQL).
2. **Common small words.** Otherwise count words like "the", "with" (English) and
   "le", "avec" (French). The language with clearly more of them wins.

Anything else (a bare list of tools, German, too little text) gives `other`, which the
rest of the app treats as "language unknown".
"""

import re

from app.db.values import SourceLanguage

ARABIC_SHARE = 0.3
"""Share of letters that must be Arabic for the text to count as Arabic."""

MIN_WORD_HITS = 2
"""The winning language needs at least this many common words."""

WIN_RATIO = 1.5
"""...and this many times as many as the other language."""

# Only words that are NOT also common in the other language ("a", "on", "as" are
# both English and French, so they are left out).
# A plain string split into words is easier to read and edit than a long list.
ENGLISH_WORDS = frozenset(
    "the and of to in with for is are was were at by from my i we this that an "  # noqa: SIM905
    "using built where which our have has it be".split()
)
FRENCH_WORDS = frozenset(
    "le la les de des du et en un une pour avec dans sur au aux est par chez où qui "  # noqa: SIM905
    "que j l d mon ma mes nous ce cette son sa ses à été".split()
)

_WORD = re.compile(r"[^\W\d_]+")


def _is_arabic(char: str) -> bool:
    return (
        "\u0600" <= char <= "\u06ff"  # Arabic
        or "\u0750" <= char <= "\u077f"  # Arabic Supplement
        or "\ufb50" <= char <= "\ufdff"  # presentation forms A
        or "\ufe70" <= char <= "\ufeff"  # presentation forms B
    )


def detect_language(text: str) -> SourceLanguage:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return "other"
    if sum(_is_arabic(char) for char in letters) / len(letters) >= ARABIC_SHARE:
        return "ar"

    words = _WORD.findall(text.lower())
    english = sum(word in ENGLISH_WORDS for word in words)
    french = sum(word in FRENCH_WORDS for word in words)
    if english >= MIN_WORD_HITS and english >= WIN_RATIO * french:
        return "en"
    if french >= MIN_WORD_HITS and french >= WIN_RATIO * english:
        return "fr"
    return "other"
