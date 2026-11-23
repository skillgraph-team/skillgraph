# Decisions

One entry per decision. Status is `Open`, `Proposed` (has a recommendation, waiting for a yes) or `Decided`. Work through one in its own session ("let's decide D-005"). Once `Decided`, change it only with a new entry that supersedes it.

Two kinds of entry:
- **D-numbers** (below): big or hard-to-reverse decisions, made by Rasen.
- **T-numbers** ([Technical choices log](#technical-choices-log), at the end): every smaller choice made while building, so nobody has to guess why the code looks the way it does. Each slice adds its own. To change one, add a new entry that replaces it.

| ID | Question | Status | Needed by |
|---|---|---|---|
| D-001 | How work is split into sessions and PRs | Decided | — |
| D-002 | Who owns the repo, and public or private | Decided | M0.1 |
| D-003 | Frontend framework | Decided | M0.4 |
| D-004 | Backend stack and tooling | Decided | M0.2 |
| D-005 | Which free LLM (hosted free tier vs local) | Open | M2.1 |
| D-006 | Evidence model: types, statuses, confidence | Decided (contract) | M2.3 |
| D-007 | Agent message envelope | Open (contract) | M2.5 |
| D-008 | Hosting for the demo | Open | M10.1 |
| D-009 | GitHub: public username only vs OAuth | Open | M3.6 |
| D-010 | How work is split and claimed | Decided | — |
| D-011 | Which tools people use | Decided | — |
| D-012 | Languages: English, French, Arabic | Decided (details Proposed) | M0.7, M2.8 |
| D-013 | Where real participants' CVs and labels live | Decided | M1.5 |
| D-014 | Is "assessed" produced in the MVP | Decided | M2.3 |
| D-015 | Login: token vs session cookie | Open | M3.1 |
| D-016 | Who reviews and merges (supersedes part of D-010) | Decided | M0.5 |
| D-017 | How much Claude Code does on its own for Rasen | Decided | — |

---

### D-001 · One slice = one issue = one branch = one PR = one session
- **Status:** Decided (Rasen)
- **Choice:** Work is split into milestones (M0–M10) and slices (`M<n>.<k>`). Each slice is done in its own fresh session, following CLAUDE.md "Working on a slice".
- **Why:** keeps each session's context small, keeps diffs reviewable, and lets four people work in parallel without stepping on each other.

### D-002 · Repo owner and visibility
- **Status:** Decided (Rasen, 2026-11-17)
- **Choice:** A. Free GitHub organization `skillgraph-team`, public repo `skillgraph-team/skillgraph`.
- **Why:** branch rulesets on `main` are enforced for free on public repos, and the code doubles as portfolio work.
- **Options:**
  - **A. Free GitHub organization + public repo.** Everyone gets access through the org; branch rulesets (require PR + review + green CI on `main`) work for free on public repos. Code is visible to anyone, which is also portfolio value.
  - **B. Private repo (personal account or free org).** Code stays private, but rulesets on private repos need a paid plan (GitHub Pro is free through the GitHub Student Developer Pack, but only covers a personal account's repos), so on a free org `main` is protected by convention only.
- **Recommendation:** A, unless the team or supervisor wants the code private.

### D-003 · Frontend framework
- **Status:** Decided (Rasen, 2026-11-23)
- **Choice:** React + Vite + TypeScript.
- **Why:** the most examples and the most teammates able to review it, which matters for chatbot-assisted work; mature translation libraries with right-to-left support (D-012). The translation library itself is chosen in M0.7.
- **Options:** React + Vite + TypeScript (largest ecosystem, most examples, most likely known by teammates) vs SvelteKit + TypeScript (less code, simpler state, smaller ecosystem).
- **Recommendation:** React + Vite + TypeScript, mainly because more of the team can review it. Whichever is chosen needs a mature translation library with right-to-left support (D-012).

### D-004 · Backend stack and tooling
- **Status:** Decided (Rasen, 2026-11-23)
- **Choice:** Python 3.12, uv, FastAPI, pydantic v2 + pydantic-settings, SQLAlchemy 2 + Alembic, PostgreSQL 16 in Docker Compose, pytest, ruff, mypy.
- **Why:** matches the project report, all free, and agents + API live in one Python codebase.

### D-005 · LLM provider
- **Status:** Open — decided by the M2.1 spike, on measured results.
- **Candidates:** a hosted free tier (check current limits and terms at decision time) vs a small local model through Ollama (needs a machine with enough RAM/GPU; slower). The provider interface means this can change later at low cost.

### D-006 · Evidence model (contract)
- **Status:** Decided (Rasen, 2026-11-23). **Contract owner: Rasen.** M2.3 writes this up in full in `docs/design/evidence-model.md` (with worked examples); teammates sign off on that write-up there (D-010, contract slices). Changes after that need a new D-entry approved by the owner.
- **Why it matters:** the database (M2.4), the hand labels (M1.6), the rules baseline (M4.4), the agents (M6) and matching all use these exact definitions; if they differ, the evaluation numbers mean nothing.
- **Choices** (all recommendations accepted):
  1. **Evidence types: a fixed, detailed list.** `cv_skills_list`, `cv_summary`, `cv_experience`, `cv_project`, `cv_education`, `certificate`, `repo_language`, `repo_dependency`, `repo_code`, `repo_readme`, `manual_project`, `user_added`, `assessment`. *Why:* the status rules work per type, and labelers never have to guess which type applies. (`assessment` exists but nothing produces it in the MVP, D-014.)
  2. **Statuses form a ladder: unverified < claimed < demonstrated < assessed.** A skill gets the highest step its evidence reaches. *Unverified* = there is a hint, but the person doesn't state the skill and no work shows it (only inferred from related skills, or only weak evidence). A skill with no evidence at all is not stored ("no skill without a source"); the rules still return `unverified` for an empty evidence list (used for job requirements). *Why:* one clear order that labelers can apply and tests can check.
  3. **A CV project or job description can make a skill demonstrated,** if it names the skill used in concrete work ("built a REST API with FastAPI"). A vague mention ("familiar with Docker") stays claimed. *Why:* students with little GitHub still get credit for real work; confidence (choice 5) keeps one CV description at medium at most.
  4. **Status follows fixed rules from the evidence; the AI only judges each piece of evidence.** Each evidence link is marked `supports` or `weak` (by rules or an agent). Then: any `assessment` → assessed; at least one supporting work-type link (`repo_code`; `repo_language` above a share threshold in a repo the person wrote that isn't a fork; a concrete `cv_project` / `cv_experience`; `manual_project`) → demonstrated; at least one supporting claim-type link (`cv_skills_list`, `cv_summary`, `certificate`, `user_added`) → claimed; otherwise → unverified. `repo_dependency`, `repo_readme` and `cv_education` alone are not enough for demonstrated. *Why:* the AI can't over-claim, a validator can reject a "demonstrated" that cites no work-type evidence, and the three systems (A, B, C) differ only in how well they judge evidence, which is what the project measures. A certificate counts as claimed (finishing a course isn't doing the work) but raises confidence.
  5. **Confidence: low / medium / high.** *High* = at least 2 independent supporting links (different sources or different types). *Medium* = exactly one supporting link. *Low* = only weak or inferred evidence; unverified is always low. More supporting evidence never lowers confidence. *Why:* people can label it consistently, it translates as a key, and LLMs report short scales more reliably than 0–100 numbers. For charts, map it to 1/2/3.
  6. **Each evidence record stores the quote itself,** copied exactly and at most ~300 characters, plus where it came from (CV section or page; repo + file path + lines; dependency file), the source's detected language (`en` / `fr` / `ar` / other) and the source id. Quotes are never translated; the UI shows them as they are, with `lang` and `dir="auto"`. *Why:* stays valid if parsing changes, and agents and explanations can cite it by id. Deleting a user deletes it.
  7. **Users can hide, dispute or add a skill, but never raise a status.** A skill the user adds becomes `user_added` evidence, so at most claimed. *Why:* keeps statuses honest; the model only needs one type and a hidden/disputed flag. Building the feature is a later slice.
- **Worked example** (report §4.3): repo `shop-api` (90% Python, FastAPI routes, `psycopg` in requirements, SQL in the code), CV lists "Python, SQL" → Python demonstrated · high; SQL demonstrated · high; REST API development demonstrated · medium; PostgreSQL demonstrated · medium (the dependency alone would be weak); backend development unverified · low (inferred only).
- **Options considered:** detailed vs broad types; unverified as "inferred only" vs "claimed but checked"; CV descriptions as demonstrated vs claimed only; status by rules vs free agent judgement; three levels vs a 0–1 number vs both; stored quote vs pointer into the source; users can't vs can edit status. Full trade-offs are in the D-006 session notes on issue #17.

### D-007 · Agent message envelope (contract)
- **Status:** Open — owner: _TBD_. Defined in M2.5.

### D-008 · Hosting
- **Status:** Open — decided in M10.1. Options: a free hosting tier (verify current limits then) vs a reproducible local demo (Docker Compose).

### D-009 · GitHub integration
- **Status:** Open — decided in M3.6.
- **Options:** public data by username (no secrets, simplest, can't see private repos) vs GitHub OAuth (proves account ownership, sees private repos, more work and a client secret to manage).
- **Recommendation:** username for the MVP; note that it doesn't prove the account belongs to the user.

### D-010 · How work is split and claimed
- **Status:** Decided (Rasen)
- **Choice:** no fixed roles and no split by tool. Anyone takes any slice whose dependencies are done, by assigning themselves on the board. Assigned = in progress, merged PR = done. A claim with no commit for 3 days can be taken over after a message in the group chat. Every PR is approved by someone other than its author. Slices marked `contract` need the whole team's approval, and later changes need the named contract owner's.
- **Why:** splitting by who has which tool added complexity without helping. What matters is that every slice is clear on its own: Goal, Why, Read first, Tasks, Done when.
- **Superseded in part by D-016** (who reviews and merges).

### D-011 · Which tools people use
- **Status:** Decided (Rasen)
- **Choice:** each member uses what they have: Rasen uses Claude Code; teammates use the Claude chatbot (with a local setup, VS Code and GitHub Desktop for code, `docs/CHAT_KIT.md`) or any other agent (`AGENTS.md`). The workflow and the rules are the same for everyone.
- **Watch:** chatbot coding is slower and more error-prone on slices that touch many files. If one stalls, anyone can pick it up or pair on it.

### D-012 · Languages: English, French and Arabic
- **Status:** Decided (Rasen) for the three languages. The details below are Proposed until M2.8 is approved.
- **Choice:** the interface, the AI's explanations and the recommendations are available in English, French and Arabic, with Arabic right-to-left. CVs, repos and postings written in any of the three are read correctly.
- **Proposed details:**
  - English is the source language and the fallback when a translation is missing.
  - On a first visit, use the browser's language if it is one of the three, otherwise English. Users can switch at any time; the choice is saved to their account.
  - Western digits (0–9) in all three languages.
  - The backend sends codes plus data; the frontend turns them into sentences. Agents write directly in the user's language. Quotes from evidence are never translated.
  - Technical names (Python, Docker, PostgreSQL) stay in Latin letters in all three languages.
- **Why:** local CVs and postings are often in French or Arabic. A skills platform that only reads and speaks English would miss much of the evidence and many of the users.
- **Risk:** small free LLMs are often much weaker in Arabic than in English. M2.1 measures this per language. If Arabic output is poor, options are: a larger free model for Arabic only, or generating in French/English with a clear note in the Arabic interface.

### D-013 · Where real participants' CVs and labels live
- **Status:** Decided (Rasen, 2026-11-23)
- **Choice:** only made-up profiles (and their labels) are committed, under `backend/eval/data/`. Real, consented CVs, their GitHub usernames and their labels live outside the repo in a private team folder, and each member copies them into `backend/eval/data/private/` (git-ignored). Evaluation results report made-up and real profiles separately, and committed results contain only scores, never text from real profiles.
- **Why:** the repo is public (D-002), and a GitHub username identifies its owner, so "anonymized" real data can't be committed safely.

### D-014 · "Assessed" in the MVP
- **Status:** Decided (Rasen, 2026-11-23)
- **Choice:** the MVP builds no assessments. "Assessed" stays in the evidence model as a status, but nothing in the MVP produces it, and rules and agents must never output it (already a guardrail in M4.4 and M6.3).
- **Why:** the report's MVP list has no assessments, and building one is a feature of its own; keeping the status in the model leaves room to add it later without a contract change.

### D-015 · Login: token vs session cookie
- **Status:** Open — decided in M3.1.
- **Options:** a signed token (JWT) sent by the frontend in a header (simple API, but storing it safely in the browser takes care) vs a server session in an HttpOnly cookie (safer by default against stolen tokens, but needs CSRF protection and same-site setup).

### D-016 · Who reviews and merges
- **Status:** Decided (Rasen, 2026-11-23). Supersedes D-010's "every PR is approved by someone other than its author".
- **Choice:** Rasen's work (done with Claude Code) is committed and pushed straight to `main`, approved by Rasen. Teammates push their work to a branch and open a PR; Rasen reviews and merges it. In M0.5, `main` is protected for everyone except org admins (Rasen): teammates need a PR with 1 approval and green CI; Rasen can push directly.
- **Why:** Rasen is the only member with a Claude Code subscription and does the reviewing; waiting for approvals on Rasen's own work would only slow the team down.
- **Watch:** Rasen's pushes get no second reviewer, so CI (M0.5) is the only automatic check on them. Teammates still need to be able to explain that code for the presentation: Claude Code posts a short summary on the slice's issue when it pushes.

### D-017 · How much Claude Code does on its own for Rasen
- **Status:** Decided (Rasen, 2026-11-23)
- **Choice:** in Rasen's sessions, Claude Code picks any unblocked slice and starts work without waiting for a go-ahead. It stops to ask only for big or hard-to-reverse decisions (2 options + trade-offs + a recommendation), and records every answer here. Every smaller choice goes in the technical choices log, and every direct push gets a plain-language summary on its issue (D-016).
- **Delegation level:** always `Delegate`. Claude Code writes all the code; Rasen doesn't write code by hand. For slices touching agents, evidence or matching, the issue summary also walks through how the logic works, step by step.
- **Why:** keep the project moving, without it turning into a black box: Rasen must still understand and be able to explain everything, so the written record (this file, the technical choices log, issue summaries) is what keeps the project understandable.

---

## Technical choices log

The smaller choices made while building, so nobody has to guess why the code looks the way it does. If you're wondering "why is it done like this?", look here first.

**How to read it.** Entries are grouped by the slice that made them, oldest first. Each one has:
- a title that states the choice in one line,
- **What**: what was done, in plain words,
- **Why**: the reason,
- **Where**: the file or setting to look at,
- sometimes **Watch out**: a limitation or a step you may need to take.

Code comments cite entries by number (e.g. "T-033"), so numbers never change. To change a choice, add a new entry and mark the old one "Replaced by T-0xx".

**Adding an entry** (every slice does this when it finishes): copy the format below, use the next free number, and put it under a heading for your slice.

```
#### T-0xx · <the choice, in one line>
- **What:** ...
- **Why:** ...
- **Where:** `path/to/file`
```

---

### M0.1 · Repo and board setup

#### T-001 · Milestones have no due dates
- **What:** GitHub milestones were created without dates. The week ranges in MILESTONES.md are targets only.
- **Why:** every slice gets done eventually.
- **Where:** GitHub milestones (setup ran without `--start-date`).

#### T-002 · There is one project board, made by hand
- **What:** the org board "SkillGraph" (#1) was created by hand. `github_setup.py` finds it by its exact title instead of creating a new one, and saves its number and ID in `scripts/github_project.json`. The board is private to the org; members have Write access.
- **Why:** the `status` command needs to know which board to update.
- **Where:** `scripts/github_project.json`.

#### T-003 · Every org member can push to the repo
- **What:** the org's default repository permission is `write`.
- **Why:** new members can push branches and assign issues without a separate invite. `main` is protected separately (D-016, T-032).
- **Where:** GitHub org settings.

#### T-004 · The setup script reads `gh` output as UTF-8
- **What:** `GH.run` decodes `gh` output as UTF-8.
- **Why:** on Windows, Python read it as cp1252, which garbled the `·` in titles. The "already exists" checks then failed, and the script tried to create milestones twice.
- **Where:** `GH.run` in `scripts/github_setup.py`. (The printing side is T-027.)

#### T-005 · Org admins can push to `main` without a PR
- **What:** the `main` ruleset lists org admins as allowed to bypass it.
- **Why:** Rasen pushes to `main` directly (D-016); everyone else needs a PR.
- **Where:** `bypass_actors` in `cmd_protect`, `scripts/github_setup.py`. Confirmed working in M0.5 (T-032).

### M0.2 · Backend skeleton

#### T-006 · The backend is an app, not a library
- **What:** `package = false` in `pyproject.toml`. Python is pinned to 3.12 (`requires-python`, `.python-version`).
- **Why:** uv installs the dependencies but doesn't try to build or publish `backend` as a package. 3.12 matches D-004.
- **Where:** `backend/pyproject.toml`.

#### T-007 · All settings come from one `.env` file in the repo root
- **What:** the backend reads the same root `.env` as Docker Compose and the frontend, wherever the server is started from. Unknown settings are ignored (`extra="ignore"`). Settings are read once and reused (`get_settings()`).
- **Why:** one place to configure everything, and other tools' settings in the same file don't crash the backend.
- **Where:** `backend/app/config.py`.

#### T-008 · `APP_ENV` only accepts `dev`, `test` or `prod`
- **What:** any other value stops the app at startup.
- **Why:** a typo fails loudly instead of silently running with the wrong setup.
- **Where:** `Settings.app_env` in `backend/app/config.py`.

#### T-009 · Backend code checks: ruff and strict mypy
- **What:** ruff checks style, likely bugs, import order, modern syntax, naming and simplifications (rule sets E, W, F, I, B, UP, N, SIM), with lines up to 100 characters, and also formats the code. mypy checks types in strict mode (with the pydantic plugin) on `app/` only; tests are not type-checked.
- **Why:** catches mistakes before review, and gives everyone one code style.
- **Where:** `[tool.ruff]` and `[tool.mypy]` in `backend/pyproject.toml`.

#### T-010 · The backend test client uses `httpx`
- **What:** tests call the API through `httpx`, even though Starlette prints a deprecation warning suggesting a newer package.
- **Why:** the suggested replacement wasn't verified yet.
- **Where:** dev dependencies in `backend/pyproject.toml`.
- **Watch out:** revisit when the warning becomes an error.

### M0.3 · Database and migrations

#### T-011 · The PostgreSQL driver is psycopg 3
- **What:** database URLs start with `postgresql+psycopg://`.
- **Why:** it's the current driver, and it ships prebuilt (no compiler needed on Windows).
- **Where:** `backend/pyproject.toml`, `.env.example`.

#### T-012 · Tests use their own database, in the same container
- **What:** `skillgraph_test` sits next to `skillgraph` and is created by `docker/postgres/init/01-create-test-database.sh` the first time the database volume is created. The settings refuse to start if `TEST_DATABASE_URL` equals `DATABASE_URL`.
- **Why:** tests can never run on (or wipe) development data.
- **Where:** `docker-compose.yml`, `backend/app/config.py`.
- **Watch out:** if your database volume is older than this script, run `docker compose down -v` once. This deletes your local data.

#### T-013 · Tests build the database with the real migrations and undo every test
- **What:** before the tests, the test database is brought up to date with `alembic upgrade head`. Each test runs inside a transaction that is rolled back afterwards; "savepoint" mode means even a `commit()` in the code under test is undone.
- **Why:** every test run also tests the migrations, and tests never see each other's data.
- **Where:** `backend/tests/conftest.py`.

#### T-014 · `/health` returns codes, not sentences
- **What:** `{"status": "ok", "database": "ok"}` with HTTP 200, or `{"status": "error", "database": "unreachable"}` with HTTP 503.
- **Why:** hosting and CI checks can see a broken database, and the frontend turns codes into text in the user's language.
- **Where:** `backend/app/main.py`.

#### T-015 · Endpoints get a database session by asking for `DbSession`
- **What:** an endpoint parameter `session: DbSession` gives it a session that is always closed after the request.
- **Why:** one pattern for every endpoint, and tests can swap in the test database. This is FastAPI's recommended `Annotated` style.
- **Where:** `backend/app/db/session.py`.

#### T-016 · How migrations are set up
- **What:** migrations live in `backend/migrations/versions/`, named date-first (`2026_11_23-<id>_<name>.py`). ruff fixes and formats each newly generated migration. The database URL comes from the settings (or the tests), not from `alembic.ini`.
- **Why:** files list in order, generated files pass the checks, and there is one source for the URL.
- **Where:** `backend/alembic.ini`, `backend/migrations/env.py`.

#### T-017 · Shell scripts keep Unix line endings
- **What:** `.gitattributes` forces LF line endings for shell scripts.
- **Why:** Git on Windows can convert them to CRLF, which breaks scripts run inside Linux containers.
- **Where:** `.gitattributes`.

#### T-018 · The local database login is `skillgraph` / `skillgraph`
- **What:** the same development defaults appear in the code, Compose and `.env.example`.
- **Why:** it's for local use only, so it isn't a secret, and setup works out of the box.
- **Where:** `docker-compose.yml`, `backend/app/config.py`.
- **Watch out:** any hosted database (M10.1) must use its own password, set through the environment.

### M0.4 · Frontend skeleton

#### T-019 · Frontend files were written by hand, not generated
- **What:** the same tools as Vite's React + TypeScript template, without its demo files (logos, counter, CSS).
- **Why:** every file in `frontend/` is used and explained.
- **Where:** `frontend/`.

#### T-020 · Frontend checks: ESLint, strict TypeScript, Vitest
- **What:**
  - `npm run lint` runs ESLint with the recommended JavaScript, TypeScript and React-hooks rules.
  - `npm run check` runs `tsc --noEmit` in strict mode, plus `noUncheckedIndexedAccess`: reading `list[i]` may give `undefined`, so you must handle that case.
  - `npm test` runs Vitest with jsdom (a fake browser in Node) and React Testing Library.
- **Why:** the same safety net as the backend (T-009).
- **Where:** `frontend/eslint.config.js`, `frontend/tsconfig.json`, `frontend/vite.config.ts`.

#### T-021 · jsdom is pinned to version 26
- **What:** the test browser jsdom stays on version 26.
- **Why:** jsdom 27 needs Node 22.12 or newer and failed on Node 22.11 (`ERR_REQUIRE_ESM`). Version 26 works on every current Node LTS.
- **Where:** `frontend/package.json`.
- **Watch out:** can be raised once everyone has Node ≥ 22.12.

#### T-022 · The browser calls `/api/...`, and Vite forwards it to the backend
- **What:** in development, a call to `/api/health` on the Vite server (port 5173) is sent to `BACKEND_URL` (default `http://localhost:8000`) with `/api` removed. The API client puts `VITE_API_BASE_URL` (default `/api`) in front of every call.
- **Why:** to the browser it's the same address as the page, so the backend needs no CORS setup. For a hosted demo (M10.1), `VITE_API_BASE_URL` can point at the backend's real address.
- **Where:** `frontend/vite.config.ts`, `frontend/src/api/client.ts`, `.env.example`.
- **Watch out:** if your `.env` was copied before M0.4, set `VITE_API_BASE_URL=/api` and add `BACKEND_URL`.

#### T-023 · The frontend reads the same root `.env` as the backend
- **What:** `envDir: ".."` in the Vite config. Only variables starting with `VITE_` reach the browser; `BACKEND_URL` is used by `vite.config.ts` only.
- **Why:** one configuration file for everything (like T-007), without leaking server settings to the browser.
- **Where:** `frontend/vite.config.ts`.

#### T-024 · Every backend call goes through `src/api/client.ts`
- **What:** one function per endpoint, each with a typed result. If the backend can't be reached, or answers with an unexpected shape, it throws `BackendUnreachableError`. A 503 from `/health` is a valid answer ("database down"), not an error.
- **Why:** pages never deal with raw HTTP, and there's one place to change how calls work.
- **Where:** `frontend/src/api/client.ts`.

#### T-025 · How a page is built
- **What:** each page is `src/pages/<Name>Page.tsx`, with its test next to it as `<Name>Page.test.tsx`. It calls the API client in a `useEffect`, cancels the call if the page closes, and keeps the outcome in one state value. Tests check a `data-state` attribute instead of the visible text.
- **Why:** one pattern to copy for every page, and tests keep passing when the text is translated.
- **Where:** `frontend/src/pages/HealthPage.tsx` (the example to copy).

#### T-026 · Health page text was English-only (temporary)
- **What:** the four messages lived in one `LABELS` object marked TEMPORARY.
- **Why:** translations didn't exist until M0.7.
- **Where:** `frontend/src/pages/HealthPage.tsx`.
- **Replaced by T-041.**

#### T-027 · The setup script always prints UTF-8
- **What:** `main()` switches the script's output to UTF-8.
- **Why:** a Windows console uses cp1252, which has no `→`, so `status` and `invite` crashed after finishing their work and reported a failure. (The reading side is T-004.)
- **Where:** `main` in `scripts/github_setup.py`.

### M0.5 · CI and branch protection

#### T-028 · CI is one workflow with two jobs, `backend` and `frontend`
- **What:** both jobs run the same commands as CLAUDE.md "Commands", on every pull request and every push to `main`. A newer push to the same branch cancels the older run.
- **Why:** CI checks exactly what you check locally. The job names are the check names the `main` ruleset requires.
- **Where:** `.github/workflows/ci.yml`.
- **Watch out:** renaming a job means updating the ruleset's required checks (see T-032).

#### T-029 · CI's database only has the test database
- **What:** CI's PostgreSQL service is created with `POSTGRES_DB=skillgraph_test`, and `TEST_DATABASE_URL` points at it.
- **Why:** tests never use `DATABASE_URL` (T-012), so CI needs no development database. Locally, `docker/postgres/init` still creates both.
- **Where:** `services.db` in `.github/workflows/ci.yml`.

#### T-030 · CI installs exactly what the lock files say
- **What:** `uv sync --locked` and `npm ci` fail if `uv.lock` or `package-lock.json` is out of date, instead of quietly updating it. Both download caches are keyed on those lock files.
- **Why:** CI tests the same versions everyone has locally, and a forgotten lock-file update is caught.
- **Where:** `.github/workflows/ci.yml`.

#### T-031 · Pinned GitHub Action versions
- **What:** `checkout@v7`, `setup-node@v7`, `setup-uv@v10.4.0`, the latest releases on 2026-11-23.
- **Why:** setup-uv has no moving `v10` tag (the first run failed with "unable to find version v10"), so it's pinned to an exact release.
- **Where:** `.github/workflows/ci.yml`.

#### T-032 · `main` is protected by the ruleset `protect-main` (id 27911752)
- **What:** created with `python scripts/github_setup.py protect --check backend --check frontend`. It requires a PR with 1 approval and green `backend` and `frontend` checks, and blocks force-pushes and deletion. Org admins bypass it (D-016, T-005).
- **Why:** teammates' work is reviewed and tested before it reaches `main`.
- **Where:** GitHub repo Settings → Rules (made by `cmd_protect` in `scripts/github_setup.py`).
- **Watch out:** running `protect` again would create a second ruleset. Edit the existing one in Settings → Rules instead.

### M0.7 · Three languages in the frontend

#### T-033 · Translation library: i18next + react-i18next + i18next-browser-languagedetector
- **What:** Rasen chose this in M0.7, over react-intl.
- **Why:** it's the most widely used and has the most examples (which helps chatbot-assisted work). It keeps texts in plain JSON, falls back to English when a text is missing, and has a ready-made plugin to detect and remember the language.
- **Where:** `frontend/src/i18n/index.ts`.

#### T-034 · How the interface language is chosen
- **What:** first the language saved in this browser (localStorage `skillgraph.language`), then the browser's language reduced to its first part (`fr-CA` → `fr`), then English. Every change is saved.
- **Why:** follows D-012. Saving it to the user's account comes once accounts exist (M3).
- **Where:** `createI18n` in `frontend/src/i18n/index.ts`.

#### T-035 · One translation setup for the app, fresh ones for tests
- **What:** `createI18n()` builds a new i18next instance. Only the app's own instance (`connectToPage: true`) connects to React and keeps `<html lang dir>` in sync. Setup is synchronous (`initAsync: false`, texts bundled into the app).
- **Why:** tests can make throwaway instances without affecting the page. Synchronous because Vite's default build target doesn't allow top-level `await`.
- **Where:** `frontend/src/i18n/index.ts`.

#### T-036 · A missing or extra translation fails `npm run check`
- **What:** `fr.json` and `ar.json` must have the same keys as `en.json` (and the other way round), and TypeScript names the missing or extra key. Keys used in code are typed too, so a typo like `t("app.nmae")` fails the check.
- **Why:** no text can be forgotten in one language, and no separate script is needed.
- **Where:** `frontend/src/i18n/resources.ts`, `frontend/src/i18n/i18next.d.ts`, `resolveJsonModule` in `tsconfig.json`.

#### T-037 · How translation keys are named
- **What:** `<page or area>.<thing>` (`health.ok`, `language.label`), nested in the JSON files. A page whose state names match its keys can use `` t(`health.${state}`) ``. Language names in the switcher are written in their own language ("Français") and live in `languages.ts`, not the locale files.
- **Why:** keys are easy to find, and language names are the same in every language.
- **Where:** `frontend/src/locales/*.json`, `frontend/src/i18n/languages.ts`.

#### T-038 · Fonts: Noto Sans + Noto Sans Arabic, self-hosted
- **What:** Rasen chose this in M0.7, over system fonts. Installed through @fontsource, weights 400 and 700. Noto Sans comes first, and Arabic letters fall through to Noto Sans Arabic. Form controls use `font: inherit`, so the language switcher gets Noto too.
- **Why:** the browser downloads only the parts of the font a page uses, and no request goes to Google's servers.
- **Where:** `frontend/src/main.tsx`, `frontend/src/index.css`.

#### T-039 · Numbers and dates go through `formatNumber` and `formatDate`
- **What:** both use `Intl` with the locale `<lang>-u-nu-latn`. Dates default to `dateStyle: "long"`.
- **Why:** digits are always 0–9, in Arabic too (D-012).
- **Where:** `frontend/src/i18n/format.ts`.

#### T-040 · Each test starts in English
- **What:** `src/test/setup.ts` (Vitest `setupFiles`) starts translations the way the app does. After each test it switches back to English and clears localStorage.
- **Why:** one test changing the language can't break the next one.
- **Where:** `frontend/src/test/setup.ts`, `frontend/vite.config.ts`.

#### T-041 · The health page is translated (replaces T-026)
- **What:** its texts are the keys `health.<state>`. The app frame (`App.tsx`) holds the header with the language switcher.
- **Why:** removes the T-026 workaround.
- **Where:** `frontend/src/pages/HealthPage.tsx`, `frontend/src/App.tsx`.
- **Watch out:** the fr/ar texts are first drafts; a native speaker checks them in M2.8.
