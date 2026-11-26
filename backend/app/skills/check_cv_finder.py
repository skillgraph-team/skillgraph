"""Checks the CV finder against the skills a person expects in one CV file (M4.2).

    cd backend && uv run python -m app.skills.check_cv_finder <cv.pdf|cv.docx> <id,id,...>

Example, with a made-up CV from the tests:

    uv run python -m app.skills.check_cv_finder tests/fixtures/cv/cv_en.pdf python,docker,kubernetes

It prints how many expected skills were found, which were missed, and which skills
were found that weren't expected ("wrong"). No database: the index is built from the
CSV files. The full evaluation over the labeled test profiles is M4.7; this is the
quick check for one file.
"""

import sys
from dataclasses import dataclass
from pathlib import Path

from app.ingestion.cv_text import read_cv
from app.ingestion.language import detect_language
from app.skills.cv_finder import find_in_cv
from app.skills.index import SkillIndex


@dataclass(frozen=True)
class CheckResult:
    expected: set[str]
    found: set[str]
    """Expected skills the finder found."""
    missed: set[str]
    """Expected skills the finder didn't find."""
    wrong: set[str]
    """Skills the finder found that weren't expected."""


def check(cv_path: Path, expected: set[str]) -> CheckResult:
    text = read_cv(cv_path.read_bytes()).text
    index = SkillIndex.from_csv()
    findings = find_in_cv(text, index, cv_language=detect_language(text))
    got = {skill_id for finding in findings for skill_id in finding.skill_ids}
    return CheckResult(expected, got & expected, expected - got, got - expected)


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        raise SystemExit(__doc__)
    expected = {skill_id.strip() for skill_id in argv[1].split(",") if skill_id.strip()}
    result = check(Path(argv[0]), expected)
    print(
        f"expected {len(result.expected)}, found {len(result.found)}, "
        f"missed {len(result.missed)}, wrong {len(result.wrong)}"
    )
    print("missed:", ", ".join(sorted(result.missed)) or "-")
    print("wrong:", ", ".join(sorted(result.wrong)) or "-")


if __name__ == "__main__":
    main(sys.argv[1:])
