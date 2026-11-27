# LLM spike (M2.1): can a free model judge evidence?

**Status:** set up, **not yet run.** The script, test profiles, reference answers and scorer are ready and checked offline. The live runs need an API key or a local model that this machine doesn't have yet (see "What's needed to finish"). D-005 stays `Open` until the table below has real numbers.

Last updated: 2026-11-27.

## The question
SkillGraph's agents (M6) need an LLM that costs nothing, answers fast enough, returns valid JSON, and judges evidence the way `docs/design/evidence-model.md` says. CVs are in English or French (D-030), and explanations must come back in English, French or Arabic. Small free models are often weaker in French and Arabic, so the table is broken down by language.

## The options (all $0)

Limits and terms change often. These were checked on 2026-11-27 and must be re-checked in each provider's console before deciding; the numbers below come from mixed, partly third-party sources.

| | Groq (free plan) | Google Gemini API (free tier) | Ollama (local) |
|---|---|---|---|
| Model tried | `llama-3.3-70b-versatile` | `gemini-2.5-flash` | `qwen2.5:7b` (fits the 6 GB laptop GPU) |
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

*Not run yet.* Paste the output of `python spikes/llm/score.py` here, one table per model, then fill in the hand notes.

| Model | valid JSON | recall | status ok | quotes exact | ar explanations ok | median s | 429s | Hand notes |
|---|---|---|---|---|---|---|---|---|
| Groq `llama-3.3-70b-versatile` | | | | | | | | |
| Gemini `gemini-2.5-flash` | | | | | | | | |
| Ollama `qwen2.5:7b` | | | | | | | | |

## Recommendation
*Pending the runs.* What would decide it: status ok and quotes exact first (they are what the evaluation measures), then valid JSON (M2.2 repairs once, so a few failures are acceptable), then Arabic and French explanations, then limits and speed. The data terms above rule out the Gemini free tier for real CVs unless the team accepts them.

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
python spikes/llm/run_spike.py --provider gemini --pause 10

# Ollama: install from ollama.com (Windows: winget install Ollama.Ollama), then
ollama pull qwen2.5:7b
python spikes/llm/run_spike.py --provider ollama --pause 0

python spikes/llm/score.py           # tables for this page
```
Keys are read from the shell only; the script never writes them anywhere. The answers are saved in `spikes/llm/results/` and committed (the profiles are made up).
