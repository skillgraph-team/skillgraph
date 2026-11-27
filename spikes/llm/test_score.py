"""Checks that the spike scorer counts the right things (run: uv run --project backend pytest spikes/llm)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from profiles import PROFILES  # noqa: E402
from run_spike import (
    fake_answer,  # noqa: E402
    skill_ids,  # noqa: E402
)
from score import language_of, parse, score_row, status_of  # noqa: E402

KNOWN = set(skill_ids())
P1 = PROFILES[0]


def row(text: str, lang: str = "en", status: int = 200) -> dict:
    return {
        "profile": P1["id"],
        "lang": lang,
        "status": status,
        "text": text,
        "seconds": 1.0,
        "rate_limited": 0,
    }


def test_reference_skills_are_real_skill_ids() -> None:
    for p in PROFILES:
        assert set(p["reference"]) <= KNOWN, p["id"]


def test_fake_answer_scores_perfectly() -> None:
    for p in PROFILES:
        for lang in ("en", "fr", "ar"):
            r = {**row(fake_answer(p, lang), lang), "profile": p["id"]}
            sc = score_row(r, KNOWN)
            assert sc["valid"] and sc["recall"] == 1 and sc["precision"] == 1, (p["id"], lang)
            assert sc["status_ok"] == 1 and sc["quotes_exact"] == 1 and sc["lang_ok"] == 1, (
                p["id"],
                lang,
            )


def test_invalid_json_and_http_errors_count_as_invalid() -> None:
    assert not score_row(row("not json"), KNOWN)["valid"]
    assert not score_row(row('{"skills": [{"skill_id": "python"}]}'), KNOWN)["valid"]
    assert not score_row(row("rate limited", status=429), KNOWN)["valid"]


def test_json_in_a_code_fence_is_accepted() -> None:
    assert parse('```json\n{"skills": []}\n```') == []


def test_made_up_quote_and_over_claim_are_caught() -> None:
    answer = {
        "skills": [
            {
                "skill_id": "postgresql",
                "evidence": [
                    {
                        "type": "repo_code",
                        "quote": "I am a PostgreSQL expert",
                        "judgement": "supports",
                        "reason": "x",
                    }
                ],
                "explanation": "Shown in the repo.",
            },
            {
                "skill_id": "python",
                "evidence": [
                    {
                        "type": "cv_education",
                        "quote": "BSc Computer Science",
                        "judgement": "weak",
                        "reason": "x",
                    }
                ],
                "explanation": "Shown in the repo.",
            },
        ]
    }
    sc = score_row(row(json.dumps(answer)), KNOWN)
    assert sc["quotes_exact"] == 0.5
    assert sc["wrong_status"] == ["python=unverified"]
    assert sc["recall"] == 2 / 5


def test_status_rules() -> None:
    def ev(t: str, j: str, reason: str = "x") -> dict:
        return {"type": t, "judgement": j, "reason": reason}

    assert status_of([ev("repo_code", "supports")]) == "demonstrated"
    assert status_of([ev("cv_skills_list", "supports"), ev("repo_dependency", "weak")]) == "claimed"
    assert status_of([ev("cv_project", "weak")]) == "claimed"
    assert status_of([ev("cv_project", "weak", "inferred_from_related")]) == "unverified"
    assert status_of([ev("repo_language", "weak")]) == "unverified"


def test_language_check() -> None:
    assert language_of("Python est utilisé dans le projet avec FastAPI.") == "fr"
    assert language_of("Python is used in the project with FastAPI.") == "en"
    assert language_of("تظهر مهارة Python في المشروع.") == "ar"


# ruff: noqa: E402, E501  (throwaway spike: long prompt strings, imports after sys.path)
