"""M2.1 spike runner: ask one free LLM to list skills and judge evidence for the 5 test profiles.

Throwaway spike code (not part of the app; the real client is M2.2's `app/llm`).
Standard library only, so it runs with any Python 3.12+:

    python spikes/llm/run_spike.py --provider fake            # offline check of the pipeline
    python spikes/llm/run_spike.py --provider groq            # needs SPIKE_GROQ_API_KEY
    python spikes/llm/run_spike.py --provider gemini          # needs SPIKE_GEMINI_API_KEY
    python spikes/llm/run_spike.py --provider ollama          # needs Ollama running locally

Each provider gets 5 profiles x 3 answer languages = 15 calls. Every answer (raw text,
time, HTTP status, retries) is appended to spikes/llm/results/<provider>__<model>.jsonl.
Score them with `python spikes/llm/score.py`.
"""

import argparse
import http.client
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from profiles import PROFILES, Profile  # noqa: E402

RESULTS = Path(__file__).parent / "results"
SKILLS_CSV = Path(__file__).parents[2] / "backend" / "app" / "skills" / "data" / "skills.csv"

# All three speak the OpenAI chat-completions format, so one HTTP call serves all of them.
PROVIDERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "SPIKE_GROQ_API_KEY",
        "model": "llama-3.3-70b-versatile",
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "key_env": "SPIKE_GEMINI_API_KEY",
        "model": "gemini-3.8-flash",
    },
    "ollama": {
        "url": "http://localhost:11434/api/chat",
        "key_env": None,
        "model": "qwen2.5:7b",
    },
    "fake": {"url": "", "key_env": None, "model": "reference"},
}

LANG_NAMES = {"en": "English", "fr": "French", "ar": "Arabic"}

EVIDENCE_TYPES = [
    "cv_skills_list",
    "cv_summary",
    "cv_experience",
    "cv_project",
    "cv_education",
    "certificate",
    "repo_language",
    "repo_dependency",
    "repo_code",
    "repo_readme",
]

SYSTEM = """You extract skills from a student's CV and GitHub summary and judge each piece of evidence.
Rules (follow exactly):
- Use only skill ids from this list: {skill_ids}
- For each skill, list every piece of evidence. "quote" must be copied exactly from the input, at most 200 characters, never translated.
- "type" is one of: {types}
- "judgement" is "supports" or "weak":
  * cv_skills_list / cv_summary / certificate: supports if the skill is named as something the person has (any level, "notions de", "familiar with" count); weak if they only want to learn it.
  * cv_experience / cv_project: supports only if the text names the skill used in concrete work (what was built or done); weak if vague.
  * repo_language: supports only if the language is at least 10% of the repo AND the repo is owned by the person AND is not a fork.
  * repo_code: supports if code in an owned, non-fork repo really uses the skill.
  * cv_education, repo_dependency, repo_readme: always weak.
  * A skill only guessed from other skills: link the evidence it comes from, judgement weak, reason "inferred_from_related".
- "reason" is one short code, e.g. concrete_work, named_in_list, named_in_summary, vague_mention, wants_to_learn, certificate_match, language_share_ok, language_share_low, forked_repo, code_uses_skill, dependency_only, readme_only, education_only, inferred_from_related.
- "explanation" is one short sentence for the student, written in {language}.
Answer with JSON only, no other text, in this shape:
{{"skills": [{{"skill_id": "...", "evidence": [{{"type": "...", "quote": "...", "judgement": "supports", "reason": "..."}}], "explanation": "..."}}]}}"""


def skill_ids() -> list[str]:
    lines = SKILLS_CSV.read_text(encoding="utf-8").splitlines()[1:]
    return [line.split(",", 1)[0] for line in lines if line]


def messages(profile: Profile, lang: str) -> list[dict[str, str]]:
    system = SYSTEM.format(
        skill_ids=", ".join(skill_ids()),
        types=", ".join(EVIDENCE_TYPES),
        language=LANG_NAMES[lang],
    )
    user = f"CV:\n{profile['cv']}\n\nGITHUB:\n{profile['repos']}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def fake_answer(profile: Profile, lang: str) -> str:
    """A perfect-looking answer built from the reference, to check the scorer offline."""
    skills = []
    for sid, ref in profile["reference"].items():
        if not ref["must"]:
            continue
        status = sorted(ref["ok"])[0]
        etype = {"demonstrated": "cv_project", "claimed": "cv_skills_list"}.get(
            status, "cv_education"
        )
        judgement = "weak" if status == "unverified" else "supports"
        quote = profile["cv"].splitlines()[1][:50]
        skills.append(
            {
                "skill_id": sid,
                "evidence": [
                    {"type": etype, "quote": quote, "judgement": judgement, "reason": "x"}
                ],
                "explanation": {
                    "en": "Shown in the CV.",
                    "fr": "Visible dans le CV.",
                    "ar": "ظاهرة في السيرة الذاتية.",
                }[lang],
            }
        )
    return json.dumps({"skills": skills}, ensure_ascii=False)


def call(provider: str, model: str, msgs: list[dict[str, str]], max_retries: int) -> dict:
    """One chat call. Returns raw text, seconds, HTTP status, and how many 429s / 503s were retried."""
    cfg = PROVIDERS[provider]
    headers = {"Content-Type": "application/json"}
    if cfg["key_env"]:
        key = os.environ.get(cfg["key_env"])
        if not key:
            sys.exit(
                f"Set {cfg['key_env']} first (the key is never written to disk by this script)."
            )
        headers["Authorization"] = f"Bearer {key}"
    if provider == "ollama":
        # Ollama's own API, because the OpenAI-compatible one can't raise the context
        # window: the default (~4k tokens) would silently cut off prompt + answer.
        payload: dict = {
            "model": model,
            "messages": msgs,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 4000},
        }
    else:
        payload = {
            "model": model,
            "messages": msgs,
            "temperature": 0,
            "max_tokens": 4000,
            "response_format": {"type": "json_object"},
        }
    body = json.dumps(payload).encode()
    rate_limited = 0
    overloaded = 0  # 503 "model overloaded": the provider is busy, not our limit
    start = time.monotonic()
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(cfg["url"], data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read())
            if provider == "ollama":
                text = data["message"]["content"]
                usage = {
                    "prompt_tokens": data.get("prompt_eval_count"),
                    "completion_tokens": data.get("eval_count"),
                    "done_reason": data.get("done_reason"),
                }
            else:
                text = data["choices"][0]["message"]["content"] or ""
                usage = data.get("usage")
            return {
                "status": 200,
                "text": text,
                "seconds": time.monotonic() - start,
                "rate_limited": rate_limited,
                "overloaded": overloaded,
                "usage": usage,
            }
        except urllib.error.HTTPError as err:
            if err.code in (429, 503) and attempt < max_retries:
                rate_limited += err.code == 429
                overloaded += err.code == 503
                wait = min(float(err.headers.get("Retry-After") or 20), 60)
                print(f"  {err.code}, waiting {wait:.0f}s", flush=True)
                time.sleep(wait)
                continue
            rate_limited += err.code == 429
            overloaded += err.code == 503
            return {
                "status": err.code,
                "text": err.read().decode(errors="replace")[:500],
                "seconds": time.monotonic() - start,
                "rate_limited": rate_limited,
                "overloaded": overloaded,
            }
        except (OSError, http.client.HTTPException) as err:  # dropped connection, timeout
            return {
                "status": 0,
                "text": str(err),
                "seconds": time.monotonic() - start,
                "rate_limited": rate_limited,
                "overloaded": overloaded,
            }
    raise AssertionError("unreachable")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--provider", required=True, choices=PROVIDERS)
    parser.add_argument("--model", help="override the default model")
    parser.add_argument("--pause", type=float, default=5.0, help="seconds between calls")
    parser.add_argument("--retries", type=int, default=2, help="retries after a 429 or 503")
    parser.add_argument("--only", help="run only this profile id")
    parser.add_argument("--lang", choices=("en", "fr", "ar"), help="run only this answer language")
    args = parser.parse_args()

    model = args.model or PROVIDERS[args.provider]["model"]
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"{args.provider}__{model.replace(':', '-').replace('/', '-')}.jsonl"
    with out.open("a", encoding="utf-8") as fh:
        for profile in PROFILES:
            if args.only and profile["id"] != args.only:
                continue
            for lang in ("en", "fr", "ar"):
                if args.lang and lang != args.lang:
                    continue
                print(f"{args.provider}/{model} {profile['id']} -> {lang}", flush=True)
                if args.provider == "fake":
                    res = {
                        "status": 200,
                        "text": fake_answer(profile, lang),
                        "seconds": 0.0,
                        "rate_limited": 0,
                    }
                else:
                    res = call(args.provider, model, messages(profile, lang), args.retries)
                    time.sleep(args.pause)
                row = {
                    "provider": args.provider,
                    "model": model,
                    "profile": profile["id"],
                    "lang": lang,
                    "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    **res,
                }
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                print(f"  HTTP {res['status']} in {res['seconds']:.1f}s", flush=True)
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()

# ruff: noqa: E402, E501  (throwaway spike: long prompt strings, imports after sys.path)
