"""M2.1 spike scorer: turn saved answers into the comparison table for docs/spikes/llm.md.

Throwaway spike code. Reads every spikes/llm/results/*.jsonl and prints one Markdown table
per model, broken down by answer language, plus a per-profile line for reading by hand:

    python spikes/llm/score.py

What each column means:
- valid JSON: the answer parses and has the expected shape (skills / evidence / enums).
- recall: share of the reference's must-find skills the model listed.
- precision: share of listed skills that the reference expects or allows.
- status ok: for must-find skills it listed, the status computed from its judgements
  (D-006 rules, below) is one the reference accepts. This is the "judge evidence" score.
- quotes exact: share of quotes found word for word in the input (catches made-up quotes).
- language ok: explanations written in the requested language (rough letter/word check).
- seconds, 429s, 503s: response time, rate-limit errors and "model overloaded" errors
  (both counted whether or not a retry then worked).
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).parent))
from profiles import PROFILES  # noqa: E402
from run_spike import EVIDENCE_TYPES, skill_ids  # noqa: E402

RESULTS = Path(__file__).parent / "results"
WORK = {"repo_code", "repo_language", "cv_project", "cv_experience", "manual_project"}
CLAIM = {"cv_skills_list", "cv_summary", "certificate", "user_added"}
FR_WORDS = {
    "le",
    "la",
    "les",
    "des",
    "est",
    "une",
    "un",
    "avec",
    "dans",
    "pour",
    "du",
    "et",
    "en",
    "sur",
}
EN_WORDS = {
    "the",
    "is",
    "with",
    "and",
    "of",
    "in",
    "for",
    "a",
    "an",
    "this",
    "was",
    "shown",
    "used",
}


def status_of(evidence: list[dict]) -> str:
    """D-006 choice 4: highest step the judgements reach (no assessments in the spike)."""
    if any(e["judgement"] == "supports" and e["type"] in WORK for e in evidence):
        return "demonstrated"
    if any(e["judgement"] == "supports" and e["type"] in CLAIM for e in evidence):
        return "claimed"
    # evidence-model.md 3.2: a weak CV project/experience link still makes the skill claimed.
    if any(
        e["type"] in {"cv_project", "cv_experience"} and e.get("reason") != "inferred_from_related"
        for e in evidence
    ):
        return "claimed"
    return "unverified"


def parse(text: str) -> list[dict] | None:
    """The answer's skills, or None if it isn't valid JSON of the expected shape."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        skills = json.loads(text)["skills"]
        for s in skills:
            assert isinstance(s["skill_id"], str) and isinstance(s["explanation"], str)
            for e in s["evidence"]:
                assert e["type"] in EVIDENCE_TYPES and e["judgement"] in {"supports", "weak"}
                assert isinstance(e["quote"], str)
        return skills
    except (ValueError, KeyError, TypeError, AssertionError):
        return None


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def language_of(text: str) -> str:
    letters = [c for c in text if c.isalpha()]
    arabic = sum("؀" <= c <= "ۿ" for c in letters)
    if letters and arabic / len(letters) > 0.5:
        return "ar"
    words = re.findall(r"[a-zàâçéèêëîïôûùüÿœ]+", text.lower())
    return "fr" if sum(w in FR_WORDS for w in words) > sum(w in EN_WORDS for w in words) else "en"


def score_row(row: dict, known: set[str]) -> dict:
    profile = next(p for p in PROFILES if p["id"] == row["profile"])
    ref = profile["reference"]
    out = {
        "seconds": row["seconds"],
        "429s": row["rate_limited"],
        "503s": row.get("overloaded", 0),
        "http_ok": row["status"] == 200,
    }
    skills = parse(row["text"]) if row["status"] == 200 else None
    out["valid"] = skills is not None
    if skills is None:
        return out
    source = norm(profile["cv"] + "\n" + profile["repos"])
    listed = {s["skill_id"]: s for s in skills}
    musts = [sid for sid, r in ref.items() if r["must"]]
    found = [sid for sid in musts if sid in listed]
    quotes = [e["quote"] for s in skills for e in s["evidence"]]
    expls = [s["explanation"] for s in skills if s["explanation"].strip()]
    out.update(
        recall=len(found) / len(musts),
        precision=sum(sid in ref for sid in listed) / len(listed) if listed else 0.0,
        status_ok=sum(status_of(listed[sid]["evidence"]) in ref[sid]["ok"] for sid in found)
        / len(found)
        if found
        else 0.0,
        quotes_exact=sum(norm(q) in source for q in quotes) / len(quotes) if quotes else 0.0,
        lang_ok=sum(language_of(x) == row["lang"] for x in expls) / len(expls) if expls else 0.0,
        unknown_ids=sorted(sid for sid in listed if sid not in known),
        missed=sorted(set(musts) - set(found)),
        wrong_status=sorted(
            f"{sid}={status_of(listed[sid]['evidence'])}"
            for sid in found
            if status_of(listed[sid]["evidence"]) not in ref[sid]["ok"]
        ),
    )
    return out


def pct(values: list[float]) -> str:
    return f"{100 * sum(values) / len(values):.0f}%" if values else "–"


def table(scores: list[tuple[dict, dict]]) -> str:
    head = "| answer lang | CV lang | calls | valid JSON | recall | precision | status ok | quotes exact | language ok | median s | 429s | 503s |"
    lines = [head, "|" + "---|" * 12]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row, sc in scores:
        cv_lang = next(p["cv_language"] for p in PROFILES if p["id"] == row["profile"])
        groups[(row["lang"], cv_lang)].append(sc)
        groups[(row["lang"], "all")].append(sc)
        groups[("all", "all")].append(sc)
    order = [(a, c) for a in ("en", "fr", "ar") for c in ("en", "fr", "all")] + [("all", "all")]
    for key in order:
        g = groups.get(key)
        if not g:
            continue
        v = [s for s in g if s["valid"]]
        lines.append(
            f"| {key[0]} | {key[1]} | {len(g)} | {pct([s['valid'] for s in g])} "
            f"| {pct([s['recall'] for s in v])} | {pct([s['precision'] for s in v])} "
            f"| {pct([s['status_ok'] for s in v])} | {pct([s['quotes_exact'] for s in v])} "
            f"| {pct([s['lang_ok'] for s in v])} | {median(s['seconds'] for s in g):.1f} "
            f"| {sum(s['429s'] for s in g)} | {sum(s['503s'] for s in g)} |"
        )
    return "\n".join(lines)


def main() -> None:
    known = set(skill_ids())
    files = sorted(RESULTS.glob("*.jsonl"))
    if not files:
        sys.exit("No results yet: run run_spike.py first.")
    for f in files:
        rows = [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines() if line]
        # Keep only the latest answer per (profile, lang), so re-runs replace older ones.
        latest = {(r["profile"], r["lang"]): r for r in rows}
        scores = [(r, score_row(r, known)) for r in latest.values()]
        print(f"\n### {f.stem.replace('__', ' / ')}\n")
        print(table(scores))
        print("\nPer answer (for reading by hand):\n")
        for row, sc in scores:
            if not sc["valid"]:
                print(
                    f"- {row['profile']} {row['lang']}: INVALID (HTTP {row['status']}) {row['text'][:120]!r}"
                )
                continue
            print(
                f"- {row['profile']} {row['lang']}: missed {sc['missed'] or '-'}; "
                f"wrong status {sc['wrong_status'] or '-'}; unknown ids {sc['unknown_ids'] or '-'}"
            )


if __name__ == "__main__":
    main()

# ruff: noqa: E402, E501  (throwaway spike: long prompt strings, imports after sys.path)
