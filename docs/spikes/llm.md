# LLM spike (M2.1): can a free model judge evidence?

**Status:** run on 2026-11-27 on two local models through Ollama (`qwen2.5:7b`, `gemma3:4b`) and on the Gemini free tier (`gemini-3.8-flash`). Groq was **not run** (no key). **D-005 decided: Ollama with `qwen2.5:7b` as the current default**; the platform stays model-agnostic (see Recommendation). Running another provider later takes two commands (see "How to run it").

Last updated: 2026-11-27.

## The question
SkillGraph's agents (M6) need an LLM that costs nothing, answers fast enough, returns valid JSON, and judges evidence the way `docs/design/evidence-model.md` says. CVs are in English or French (D-030), and explanations must come back in English, French or Arabic. Small free models are often weaker in French and Arabic, so the table is broken down by language.

## The options (all $0)

Limits and terms change often. These were checked on 2026-11-27 and must be re-checked in each provider's console before deciding; the numbers below come from mixed, partly third-party sources.

| | Groq (free plan) | Google Gemini API (free tier) | Ollama (local) |
|---|---|---|---|
| Model tried | `llama-3.3-70b-versatile` (not run: no key) | `gemini-3.8-flash` (`gemini-2.5-flash` is closed to new users: HTTP 404) | `qwen2.5:7b` and `gemma3:4b` (both fit the 6 GB laptop GPU; Ollama 0.40.18) |
| Sign-up | Account, no card | Google account, API key from AI Studio | Install Ollama, download the model (~5 GB) |
| Limits | Per organisation and per model. Third-party reports: ~30 requests/min and 1,000–14,400 requests/day depending on model; tokens/min also capped. Exact numbers: console → Settings → Limits | Per Google Cloud project. Google no longer publishes a fixed table; developers reported free Flash cut to about **20 requests/day**. Exact numbers: AI Studio's rate-limit page | None except your hardware |
| Over the limit | HTTP 429, no charge | HTTP 429, no charge | — |
| Your data | Says it doesn't train on API data and keeps no inference data by default (wording on the page is partly inconsistent) | **Free use: Google may use prompts and answers to improve its products, and human reviewers may read them;** Google says not to send personal information. Paid use is excluded. In the EEA, Switzerland and the UK, apps for users there must use the paid service | Never leaves the machine |
| Speed | Very fast (dedicated inference hardware) | Fast | Slow on a laptop GPU; depends on the machine running the demo |
| JSON mode | `response_format: json_object` | `response_format: json_object` (OpenAI-compatible endpoint) | `response_format` / JSON schema |

Why these three: one fast hosted free tier with a large open model (Groq), one big-lab hosted free tier (Gemini), and one option that needs no account and keeps CVs on the machine (Ollama). OpenRouter's free models and GitHub Models are other $0 options; they were not included to keep the spike small.

**Already worth noting:** real users' CVs are personal data. The Gemini free tier's terms (possible human review, use for product improvement, "don't send personal information") make it a poor fit for real CVs even if it scores well. That affects D-005 regardless of the numbers.

Sources: [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), [Gemini API Additional Terms (archived Oct 2025)](https://ai.google.dev/gemini-api/terms-archive/terms_10_07_25), [forum report of the free Flash cut](https://discuss.ai.google.dev/t/do-they-really-think-we-wouldnt-notice-a-92-free-tier-quota/111262), [Groq community: free and dev tier limits](https://community.groq.com/t/what-are-the-rate-limits-for-the-groq-api-for-the-free-and-dev-tier-plans/42), [Groq: your data](https://console.groq.com/docs/your-data), [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs).

## Method
- **Profiles:** 5 made-up profiles in `spikes/llm/profiles.py`: 3 English CVs, 2 French CVs (one with an English repo). No Arabic CV, because CVs are English/French only (D-030). They cover the tricky cases from the evidence model: the report's `shop-api` example, a certificate, "interested in…", "familiar with…", "notions de…", a forked repo, a 2–3 % language share, a dependency-only and a README-only hint. M1.5's full profile set isn't done yet, so these are spike-only.
- **Reference answers:** for each profile, what a person following `docs/design/evidence-model.md` would accept: the skills that must be found, skills that are allowed (inferred or borderline), and the acceptable status for each.
- **The task (one call per profile and answer language, 15 calls per model):** list skills using only ids from `skills.csv`; for each, quote the evidence exactly, give its type, judge it `supports` or `weak` with a reason code, and write a one-sentence explanation in the requested language. The status is then computed from the judgements with the D-006 rules, so "status ok" measures the judging, which is the AI's only job in the design.
- **Scores:** valid JSON (right shape and values), recall of must-find skills, precision (listed skills the reference expects or allows), status ok, quotes found word for word in the input (catches made-up quotes), explanation in the right language (rough letter/word check), median seconds, 429 errors. Plus a hand read of the raw answers (`spikes/llm/results/*.jsonl`).
- **Settings:** temperature 0, JSON mode on, 5 s pause between calls, up to 2 retries after a 429.

## Results

Run on 2026-11-27, laptop with an RTX 4050 (6 GB), Ollama 0.40.18, 15 calls per model. Raw answers: `spikes/llm/results/`. The per-answer details (missed skills, wrong statuses, invented ids) are printed by `score.py`. "answer lang" is the language the explanations were asked in; "CV lang" is the CV's language.

### Summary

| Model | valid JSON | recall | precision | status ok | quotes exact | language ok | median s | 429s |
|---|---|---|---|---|---|---|---|---|
| Ollama `qwen2.5:7b` | **100%** | 65% | **98%** | **79%** | 97% | 91% | 23.6 | 0 |
| Ollama `gemma3:4b` | 93% | **83%** | 84% | 71% | **99%** | **97%** | **14.0** | 0 |
| Groq `llama-3.3-70b-versatile` | not run | | | | | | | |
| Gemini `gemini-3.8-flash` (free) | 73% (11 of 15 answered) | **100%** | **100%** | **100%** | **100%** | **100%** | ~95 (55–170) | 14 |

### Ollama `qwen2.5:7b`

| answer lang | CV lang | calls | valid JSON | recall | precision | status ok | quotes exact | language ok | median s | 429s |
|---|---|---|---|---|---|---|---|---|---|---|
| en | en | 3 | 100% | 70% | 100% | 85% | 92% | 100% | 29.4 | 0 |
| en | fr | 2 | 100% | 62% | 100% | 71% | 100% | 100% | 26.1 | 0 |
| en | all | 5 | 100% | 67% | 100% | 79% | 95% | 100% | 29.4 | 0 |
| fr | en | 3 | 100% | 66% | 100% | 92% | 100% | 78% | 24.5 | 0 |
| fr | fr | 2 | 100% | 56% | 92% | 55% | 100% | 67% | 17.4 | 0 |
| fr | all | 5 | 100% | 62% | 97% | 77% | 100% | 73% | 18.7 | 0 |
| ar | en | 3 | 100% | 66% | 100% | 100% | 92% | 100% | 29.0 | 0 |
| ar | fr | 2 | 100% | 67% | 94% | 48% | 100% | 100% | 21.5 | 0 |
| ar | all | 5 | 100% | 66% | 98% | 79% | 95% | 100% | 23.6 | 0 |
| all | all | 15 | 100% | 65% | 98% | 79% | 97% | 91% | 23.6 | 0 |

### Ollama `gemma3:4b`

| answer lang | CV lang | calls | valid JSON | recall | precision | status ok | quotes exact | language ok | median s | 429s |
|---|---|---|---|---|---|---|---|---|---|---|
| en | en | 3 | 100% | 93% | 91% | 75% | 100% | 100% | 16.1 | 0 |
| en | fr | 2 | 100% | 82% | 85% | 77% | 100% | 100% | 12.1 | 0 |
| en | all | 5 | 100% | 89% | 89% | 76% | 100% | 100% | 14.3 | 0 |
| fr | en | 3 | 100% | 87% | 79% | 67% | 97% | 87% | 13.3 | 0 |
| fr | fr | 2 | 100% | 82% | 85% | 77% | 100% | 100% | 12.6 | 0 |
| fr | all | 5 | 100% | 85% | 81% | 71% | 98% | 92% | 13.3 | 0 |
| ar | en | 3 | 67% | 60% | 92% | 62% | 100% | 100% | 9.9 | 0 |
| ar | fr | 2 | 100% | 86% | 72% | 68% | 100% | 100% | 15.8 | 0 |
| ar | all | 5 | 80% | 73% | 82% | 65% | 100% | 100% | 12.9 | 0 |
| all | all | 15 | 93% | 83% | 84% | 71% | 99% | 97% | 14.0 | 0 |

### Gemini `gemini-3.8-flash` (free tier)

| answer lang | CV lang | calls | valid JSON | recall | precision | status ok | quotes exact | language ok | median s | 429s | 503s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| en | en | 3 | 100% | 100% | 100% | 100% | 100% | 100% | 95.5 | 0 | 0 |
| en | fr | 2 | 50% | 100% | 100% | 100% | 100% | 100% | 59.4 | 3 | 1 |
| en | all | 5 | 80% | 100% | 100% | 100% | 100% | 100% | 91.5 | 3 | 1 |
| fr | en | 3 | 100% | 100% | 100% | 100% | 100% | 100% | 123.5 | 0 | 0 |
| fr | fr | 2 | 0% | – | – | – | – | – | 62.4 | 8 | 0 |
| fr | all | 5 | 60% | 100% | 100% | 100% | 100% | 100% | 109.0 | 8 | 0 |
| ar | en | 3 | 100% | 100% | 100% | 100% | 100% | 100% | 71.5 | 0 | 0 |
| ar | fr | 2 | 50% | 100% | 100% | 100% | 100% | 100% | 114.5 | 3 | 1 |
| ar | all | 5 | 80% | 100% | 100% | 100% | 100% | 100% | 71.5 | 3 | 1 |
| all | all | 15 | 73% | 100% | 100% | 100% | 100% | 100% | 91.5 | 14 | 2 |

The 4 missing answers: 2 timed out after 180 s, 2 got "model is experiencing high demand" (503) after 3 retries. Re-trying them hit "You exceeded your current quota" (429): the free daily limit was used up after about 25 requests (including the early 404s and retries). The scores above are for the 11 answers that came back.

### Hand notes (reading the answers)
- **`qwen2.5:7b` lists too few skills.** It often stops after the skills list plus one or two more: it missed FastAPI, PostgreSQL and REST API in the `shop-api` profile (all three languages), Power BI and Excel for the data analyst, PyTorch and Hugging Face for the data scientist. What it does list is almost always a real, expected skill (precision 98%) with the right judgement.
- **`gemma3:4b` finds more but follows the rules less.** It invents skill ids that aren't in the list (`react-dom`, `bert`, `transformers`, `psycopg`, `b2`, `licence-3-informatique`) and judges a `repo_dependency` as `supports`, which the rules forbid. It usually stops at the CV skills list, so work evidence is missed: React, CSS and Python came out `claimed` where repos and projects show them `demonstrated`. It twice got stuck in a loop on the same Arabic answer (Ollama stopped it: "token repeat limit reached"), once in the main run and again on a re-run, so that failure is repeatable at temperature 0.
- **Both misread French hedges.** Both models judged "notions de Docker" `weak` ("wants to learn") in every language, and `qwen2.5:7b` once said the person *wants to learn* scikit-learn and TensorFlow, which the CV lists as skills. French CVs score clearly lower on status (qwen 48–71%) than English ones (85–100%). The prompt needs French examples (M6).
- **Quotes are reliable.** Almost all quotes are copied word for word. The one made-up one was qwen quoting "SQL 10%" where the repo says "HTML 10%".
- **Arabic explanations read naturally** for both models. qwen once spelled React in Arabic letters wrongly ("رايت"); product names should stay in Latin letters (a prompt rule for M6). qwen wrote some English sentences when asked for French (language ok 73% for fr).
- **`gemini-3.8-flash` answers like a careful person.** In the 11 answers that came back: every must-find skill, every status right, every quote exact, in all three languages. (It never answered p5, the French data-science profile, so the hardest French case is untested on Gemini.) It handled the cases both local models got wrong: "notions de Docker" → claimed, the forked repo, the 2–3 % language shares, the dependency-only hints. Its Arabic and French explanations are natural and keep product names in Latin letters. It "thinks" before answering (about 1,000 extra tokens per call), which is why it's slow.
- **But the free tier can't carry the project:** ~20 requests a day, ~95 s per call, 4 of 15 calls failed (timeouts and "high demand"), and the terms allow Google to use and human-review the prompts. The eval alone (3 systems × 15–20 profiles, several calls each for the multi-agent system) needs hundreds of calls per run.
- **Speed (local):** 10–30 s per profile on the laptop GPU; the first call after loading a model takes about a minute. One early qwen call crashed in Ollama's GPU start-up (`CUDA error`, HTTP 500); a re-run worked, so it's counted as an Ollama hiccup and the scores use the re-run.

## Recommendation
**Use Ollama with `qwen2.5:7b` as the current default, behind M2.2's provider interface, and keep Groq as the first upgrade to try.** The platform stays model-agnostic (D-005): nothing is tuned to qwen, and it may move to paid APIs with stronger models later. The spike's script and profiles can be re-run against any provider to compare.

- **Why qwen over gemma:** the design only asks the model to *judge* evidence (D-006 choice 4), and the rule-based finders (M4.2, M4.3) already find most skills by name. qwen judges better (status ok 79% vs 71%), sticks to the id list (98% vs 84% precision), and always returns valid JSON. gemma's extra recall comes with invented ids and repeatable loops in Arabic.
- **Why local over the Gemini free tier, even though Gemini judged far better:** the free tier gives ~20 requests a day (the eval needs hundreds per run), answered only 11 of 15 calls, takes ~95 s per call, and its terms (human review, product use, "don't send personal information") rule it out for real CVs. Local costs nothing, has no limits and keeps CVs on the machine.
- **What Gemini shows:** the design works. With a strong model, judging evidence by these rules is close to perfect, so qwen's 79% is a model limit, not a design flaw. That is the case for keeping the platform model-agnostic: moving to a stronger or paid model later should improve System C with only a config change.
- **What it costs us:** 65% recall and weaker French judging, so System C may not beat the baseline by much unless M6 improves it with changes that help any model, not qwen-specific tricks: a better prompt (French examples, "list every skill", one call per source), or giving the model the finders' candidates to judge. Every machine that runs System C needs Ollama and ~5 GB for the model; tests never need it (record/replay, M2.2). The demo host (D-008) must be able to run it, or switch to a hosted provider.
- **Revisit when:** paid APIs are an option (a paid Gemini tier or similar removes the limits and the data-use terms), or someone has a Groq key. Run `python spikes/llm/run_spike.py --provider groq` and `python spikes/llm/score.py`, add the table here, and switch if it clearly judges better. With M2.2 that's a config change.

## How to run it
```bash
# Offline check (no network): should print 100% everywhere
python spikes/llm/run_spike.py --provider fake && python spikes/llm/score.py
rm spikes/llm/results/fake__reference.jsonl

# Groq: create a key at console.groq.com, then in the same shell
export SPIKE_GROQ_API_KEY=...        # PowerShell: $env:SPIKE_GROQ_API_KEY="..."
python spikes/llm/run_spike.py --provider groq

# Gemini: create a key in Google AI Studio
export SPIKE_GEMINI_API_KEY=...
python spikes/llm/run_spike.py --provider gemini --model gemini-3.8-flash --pause 10 --retries 3

# Ollama: install from ollama.com (Windows: winget install Ollama.Ollama), then
ollama pull qwen2.5:7b
python spikes/llm/run_spike.py --provider ollama --pause 0
ollama pull gemma3:4b && python spikes/llm/run_spike.py --provider ollama --model gemma3:4b --pause 0

python spikes/llm/score.py           # tables for this page
```
Keys are read from the shell only; the script never writes them anywhere. The answers are saved in `spikes/llm/results/` and committed (the profiles are made up).
