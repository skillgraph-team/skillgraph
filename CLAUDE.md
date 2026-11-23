# Project: SkillGraph

## What this is
An evidence-based skills platform for students and recent graduates. It extracts skills from a CV and GitHub, links every skill to the evidence behind it with a status (claimed / demonstrated / assessed / unverified), matches the profile against curated internships, and explains matches and gaps. A small multi-agent system (custom agent loop, no agent framework) does the analysis, and its value is measured against a rule-based baseline and a single-agent version. It works in English, French and Arabic (Arabic is right-to-left).

Full spec: `docs/SPEC.md`. Plan: `docs/MILESTONES.md`. Decisions: `docs/DECISIONS.md`. Terms: `docs/GLOSSARY.md`. Chatbot workflow: `docs/CHAT_KIT.md`. Read those only when the current slice needs them.

## How we work (always follow)
- **One slice per session.** A slice is one GitHub issue (`M<n>.<k>`), one branch, one PR. Follow "Working on a slice" below. Don't start a second slice in the same session; suggest a fresh session (`/clear`) instead.
- **Spec before code, tests before implementation.** Restate the slice's tasks and "Done when" criteria, write or update the tests first, then implement the smallest change that passes them.
- **Run the checks, don't assume.** Use the commands below. Report actual output.
- **Never weaken, skip or delete a test to make it pass.** If a test looks wrong, say why and let the user decide.
- **No scope creep.** No drive-by refactors, no unrequested dependencies, no work from other slices. Put suggestions in the final report, not in the diff.
- **Decisions belong to the user.** Anything in `docs/DECISIONS.md` marked `Open`, or any hard-to-reverse choice (schema, protocol, library, storage), gets raised with 2 options + trade-offs + a recommendation. Record the user's choice in `docs/DECISIONS.md` with a one-line reason. Big decisions get their own session (see below).
- **Contracts have one owner.** Slices labelled `contract` (evidence model, schema, message envelope, API) define what everyone else codes against. Changing a `Decided` contract needs the owner's approval in the PR.
- **Delegation level.** At the start of a slice that touches agents, evidence evaluation or matching, ask which level the user wants: `Delegate` (you write, user reviews), `Pair` (you draft and explain the reasoning, user adjusts), `Learn-first` (user writes; you review, ask questions, point out problems).
- **Explain what you write.** The user must be able to explain everything that gets merged. Flag anything non-obvious. If asked, walk through code line by line.
- **Write for the reviewer.** Teammates may review with the chatbot and no coding agent. Every PR (and every direct push by Rasen, as an issue comment, D-016) needs a plain-language "Review guide" and "How to test it manually" section a non-author can follow.
- **Keep the codebase easy to work on by hand.** Teammates often work by pasting files into a chatbot, so prefer small files, obvious names, one clear pattern per kind of thing (endpoint, service, test), and a short docstring at the top of each module saying what it's for.
- **Same approach failed twice → stop.** Diagnose the root cause and propose a different approach instead of stacking fixes.
- **Say plainly** when something is a workaround, a guess, or untested.

## Working on a slice
The user talks normally ("let's do M2.3", "this is done", "review PR 12"). Follow these steps without being asked.

**Starting** (the user names a slice, or asks what to work on: then suggest open slices whose `depends` are done):
1. `git status`, then `git switch main && git pull`. Uncommitted changes → ask what to do first.
2. Read only that slice's section in `docs/MILESTONES.md` and the files in its "Read first". Find its issue: `gh issue list --search "<id> in:title" --json number,title,assignees`. Assigned to someone else → stop and say so. A `depends` slice still open → say which and ask.
3. Assign it (`gh issue edit <n> --add-assignee @me`), set the board status (`python scripts/github_setup.py status <id> "In Progress"`), create the branch `m<n>.<k>-short-name` (not for Rasen, who works on `main`, D-016).
4. Restate goal, tasks and "Done when" in a few lines; raise any `Open` decision it needs; ask the delegation level if it touches agents, evidence or matching. List the files and tests you plan to write, then wait for a go-ahead.

**Finishing** (the user says it's done or asks for a PR):
1. Run every check that applies (Commands below) and show real output. Go through "Done when" item by item and say how each is shown. Anything users see: present in en, fr and ar, and works right-to-left.
2. Diff too big to review in one sitting (~400+ lines outside generated files)? Say so and propose a split.
3. Add every technical choice the slice made (library, file layout, pattern, default value, workaround) to the "Technical choices log" in `docs/DECISIONS.md`: one T-numbered entry each with what, why and where. Rasen wants no black boxes. Update CLAUDE.md only if commands, architecture or conventions changed.
4. Who merges depends on who is working (D-016; check `gh api user --jq .login`):
   - **Rasen (`rimRasen`)**: no PR. Work on `main` (skip the branch in Starting step 3), commit `<ID>: <summary>` with `Closes #<issue>` in the body, and push to `main`. Then post a comment on the issue with the plain-language **Review guide**, **How to test it manually** and **Handoff** below, so teammates can follow and explain the change.
   - **Anyone else**: commit `<ID>: <summary>`, push the branch, and open the PR with `.github/pull_request_template.md` filled in, including `Closes #<issue>`, a plain-language **Review guide** (which files matter, what each change does, every concept a non-author needs), **How to test it manually**, and a **Handoff** a fresh session could continue from. Rasen reviews and merges it.
5. Report: what changed and why, what to review closely, what's unsure or untested, out-of-scope ideas, and the next 1–3 unblocked slices with a recommendation.

**Reviewing a PR** ("review PR 12"): `gh pr view` and `gh pr diff`, check it out, run the checks and `gh pr checks`. Review against its slice's "Done when", the architecture rules, the three-language rules, and tests that were bent to pass. Report a blunt verdict with must-fix items (file and line) separate from suggestions. Post a review only after the user confirms.

**A decision** ("let's decide D-005"): no implementation code in that session. Explain the question from scratch, give 2–3 options with trade-offs (cost must be $0; search the web for anything that may have changed), recommend one, wait for the choice, record it in `docs/DECISIONS.md` and open a small PR.

## Commands
(Confirmed in M0.2; update here if they change.)
- Start database: `docker compose up -d db`
- Backend deps: `cd backend && uv sync`
- Backend run: `cd backend && uv run uvicorn app.main:app --reload`
- Backend tests: `cd backend && uv run pytest`
- Backend lint/types: `cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app`
- Migrations: `cd backend && uv run alembic upgrade head` / new: `uv run alembic revision --autogenerate -m "<msg>"`
- Frontend: `cd frontend && npm install && npm run dev` / checks: `npm run lint && npm run check && npm test`
- Eval: `cd backend && uv run python -m eval.run --system <baseline|single|multi>`

## Architecture
```
frontend/  (UI)  ->  backend/app/api  (FastAPI: auth, validation, permissions, ALL db writes)
                          |
                          v
                 backend/app/agents/runtime   (orchestrator, agent loop, messages, tools, retries, logs)
                 backend/app/agents/<name>.py (profile, evidence, opportunity, matching, development)
                          |  agents return structured results; services persist them
                          v
                 backend/app/db  (SQLAlchemy models, PostgreSQL)   backend/app/llm  (provider interface + record/replay)
backend/app/ingestion  (CV parsing, GitHub)    backend/app/skills  (taxonomy, rule-based baseline)
backend/eval  (labeled dataset, harness, results)
```
- **Agents never write to the database and never call external services directly.** They receive context, call tools the runtime gives them, and return a validated pydantic result. `app/services/*` persists results.
- **All LLM calls go through `app/llm`.** Nothing imports a provider SDK elsewhere. Tests run on recorded responses (cassettes) and never hit the network.
- **Every skill record keeps references to its evidence.** No skill without a source.
- Agent messages use the envelope in `app/agents/runtime/messages.py` (task_id, sender, recipient, task, context, expected_schema, status, result | error, language).

## Conventions
- Python 3.12, type hints everywhere, pydantic v2 for all data crossing a boundary (API, agent I/O, LLM output).
- Errors: raise domain exceptions in services; map to HTTP errors only in `app/api`. Never swallow exceptions silently.
- Agent limits are explicit: max steps, max retries, max tokens per run. No unbounded loops.
- **Three languages** (en, fr, ar; Arabic is right-to-left). No user-visible text hard-coded: interface text goes in `frontend/src/locales/{en,fr,ar}.json`, all three at once; the backend returns codes plus data, never sentences; agents write in the language passed to them; quotes from CVs and repos stay in their original language. CSS logical properties only (`margin-inline-start`, not `margin-left`). Terms and rules: `docs/design/localization.md`.
- Config from environment variables (see `.env.example`). Secrets never in code, tests, logs or commits.
- Dependencies: add only when the slice needs them, and say so in the report.
- Tests next to the code they test under `backend/tests/` mirroring `app/`. Use factories and fixtures, not real CVs of real people.
- Branches: `m<n>.<k>-short-name`. Commits: `M<n>.<k>: <imperative summary>`. PR closes its issue (`Closes #<id>`).

## Do not touch without asking
- `.env`, `.env.*` (except `.env.example`), anything under `backend/eval/data/labels/` (hand-labeled ground truth)
- Existing Alembic migrations (add new ones instead)
- Agent message envelope and evidence status definitions once marked `Decided` in `docs/DECISIONS.md` (they are team contracts)
- `.github/`, `CLAUDE.md` workflow rules, `docs/SPEC.md` (propose changes in the report)

## Current status
Milestone: M0 (Foundation). Live task status is on the GitHub Project board, not here.
Updated only when a milestone closes. Per-session handoff notes go in the PR description.
