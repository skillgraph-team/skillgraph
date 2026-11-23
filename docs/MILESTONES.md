# Milestones and slices

The whole project as a list of small, self-contained pieces of work.

- A **milestone** is a stage of the project with a demo at the end.
- A **slice** is one piece of work: one GitHub issue, one branch, one pull request. Anyone can take any slice whose `depends` are done, with whatever tool they use (Claude Code, the Claude chatbot, or by hand). See README "How we work".
- Weeks are targets for a 14-week semester. Milestones overlap on purpose.
- Unfamiliar word? See [GLOSSARY.md](GLOSSARY.md).
- **Three languages.** SkillGraph works in English, French and Arabic (Arabic is right-to-left). Rules: `docs/design/localization.md` (M2.8). Any slice that adds text users see adds it in all three languages, and any screen is checked in Arabic before it counts as done.

Every slice answers five questions:
- **Goal:** what exists when it's done.
- **Why:** why the project needs it and what it unblocks.
- **Read first:** what to read or know before starting.
- **Tasks:** the steps.
- **Done when:** how anyone can check it's finished.

**Format rules** (`scripts/github_setup.py` turns this file into GitHub issues, so keep them):
- Milestone: `## M<n> · <title>`, then `<!-- weeks: a-b -->`, then its goal and demo.
- Slice: `### M<n>.<k> · <title>`, then one line of tags: `` `area:…` `size:S|M|L` `depends:…` `` and optionally `` `contract:yes` ``, then the five sections above.
- Areas: infra, backend, frontend, agents, ai, data, eval, research, docs.
- Size: S = a few hours, M = about a day, L = several days (split it if it grows).
- `contract:yes` means the slice defines something everyone else builds on. Its PR needs approval from the whole team, and later changes need the contract owner's approval.

---

## M0 · Foundation
<!-- weeks: 1-2 -->
The shared repo, the board, and empty backend and frontend apps with automatic checks and three-language support.
**Demo:** every member clones the repo, starts the app on their own machine, runs the tests, and merges a pull request; the app switches between English, French and Arabic.

### M0.1 · Create the repo, board and team access
`area:infra` `size:S` `depends:—`

**Goal:** The GitHub repo and the project board exist, every slice in this file is an issue on the board, and all four members have access.

**Why:** Everything else happens here: code, issues, reviews, progress. Without it nobody can start.

**Read first:** `docs/KICKOFF.md`; decisions D-002 and D-010 in `docs/DECISIONS.md`.

**Tasks**
- [ ] Decide D-002 (who owns the repo, public or private) and D-010 (how tasks are claimed)
- [ ] Create the repo and push these kickoff files to `main`
- [ ] Run `python scripts/github_setup.py setup --owner <owner> --repo <owner>/skillgraph` to create labels, milestones, the board and one issue per slice
- [ ] Invite the three teammates (`python scripts/github_setup.py invite <user1> <user2> <user3>`) and give them access to the board
- [ ] On the board, check the built-in workflows "Item closed → Done" and "Pull request merged → Done" are on

**Done when**
- [ ] All four members can open the board, assign themselves an issue and push a branch
- [ ] Every slice in this file has exactly one issue on the board

### M0.2 · Backend skeleton
`area:backend` `size:S` `depends:M0.1`

**Goal:** An empty but working Python web server (FastAPI) with one endpoint, `GET /health`, plus automatic code checks and tests.

**Why:** Every backend slice adds to this. Setting up structure, configuration and test tooling once, the same way for everyone, avoids four people inventing four layouts.

**Read first:** CLAUDE.md "Commands" and "Architecture"; decision D-004 (backend stack).

**Tasks**
- [ ] Confirm D-004 and record it
- [ ] Create `backend/` as a uv project with `app/main.py`, `app/config.py` (settings read from environment variables) and `GET /health` returning `{"status": "ok"}`
- [ ] Configure ruff (lint and formatting), mypy (type checks) and pytest in `pyproject.toml`; write one test for `/health`
- [ ] Update CLAUDE.md "Commands" if anything differs

**Done when**
- [ ] From a fresh clone, `uv sync`, `uv run pytest`, ruff and mypy all pass

### M0.3 · Database and migrations
`area:backend` `size:S` `depends:M0.2`

**Goal:** A PostgreSQL database running locally in Docker, connected to the backend, with migrations set up and tests that use their own separate database.

**Why:** All data (users, skills, evidence, matches) lives in this database. Migrations let everyone change the database structure the same way. A separate test database means running tests never wipes your local data.

**Read first:** GLOSSARY: migration, ORM.

**Tasks**
- [ ] `docker-compose.yml` with PostgreSQL 16 and a named volume; connection values in `.env.example`
- [ ] SQLAlchemy 2 connection and session setup; Alembic initialised with an empty first migration
- [ ] A test fixture that uses a separate test database and undoes each test's changes
- [ ] `/health` also reports whether the database is reachable

**Done when**
- [ ] `docker compose up -d db && uv run alembic upgrade head && uv run pytest` passes
- [ ] Running the tests leaves the development database untouched

### M0.4 · Frontend skeleton
`area:frontend` `size:S` `depends:M0.1`

**Goal:** An empty frontend app in TypeScript that calls the backend and shows its `/health` status, with lint, type checks and tests.

**Why:** Every screen is built on this. Choosing the framework and wiring the connection to the backend once saves every later frontend slice from doing it.

**Read first:** decision D-003 (frontend framework).

**Tasks**
- [ ] Decide D-003 and record it
- [ ] Create `frontend/` with TypeScript, a linter, a type checker and a test runner (`npm run lint`, `npm run check`, `npm test`)
- [ ] One API client module that reads the backend URL from an environment variable; a dev proxy to the backend
- [ ] A page that shows the backend's `/health` result

**Done when**
- [ ] `npm run dev` shows the backend's health status in the browser
- [ ] lint, check and test pass

### M0.5 · Continuous integration and branch protection
`area:infra` `size:S` `depends:M0.3, M0.4`

**Goal:** GitHub runs all checks automatically on every pull request, and `main` can only change through a reviewed pull request.

**Why:** With four people merging work, this catches broken code before it reaches `main`, whoever wrote it and whatever tool they used.

**Read first:** GLOSSARY: CI, ruleset; decision D-002.

**Tasks**
- [ ] `.github/workflows/ci.yml` with a backend job (uv, ruff, mypy, pytest with a PostgreSQL service) and a frontend job (lint, check, test)
- [ ] Cache dependencies; run on pull requests and on pushes to `main`
- [ ] Run `python scripts/github_setup.py protect --check backend --check frontend` if D-002 allows it; otherwise write the "always use a reviewed PR" convention in README

**Done when**
- [ ] A pull request shows both jobs green
- [ ] A pull request with a deliberately failing test shows red

### M0.6 · Everyone set up and through the full flow once
`area:docs` `size:S` `depends:M0.5`

**Goal:** All four members have the app running on their own machine and have taken one tiny change through claim → branch → pull request → review → merge.

**Why:** Setup problems should surface now, on a trivial change, not in week 8 on an important one. It also makes README trustworthy.

**Read first:** README "Getting started" and "How we work".

**Tasks**
- [ ] Each member follows README "Getting started" on their own machine and fixes whatever was wrong or missing in it
- [ ] Each member adds themselves to `docs/TEAM.md` (name, GitHub handle, strengths, what they want to learn) through their own pull request
- [ ] Each member reviews one other member's pull request

**Done when**
- [ ] Four onboarding pull requests merged
- [ ] README has no undocumented setup step

### M0.7 · Three-language support in the frontend
`area:frontend` `size:M` `depends:M0.4`

**Goal:** The frontend can show every text in English, French or Arabic, switch language at any time, and flip to a right-to-left layout for Arabic.

**Why:** Adding languages after twenty screens exist means reworking all of them. Set up before the first real screen, each later screen just adds its words to three files.

**Read first:** decision D-012; GLOSSARY: localization, locale, RTL, translation key, CSS logical properties.

**Tasks**
- [ ] Add a translation library that suits the D-003 framework; translation files `frontend/src/locales/en.json`, `fr.json` and `ar.json`
- [ ] A language switcher; remember the choice; on a first visit use the browser's language if it's one of the three, otherwise English (D-012)
- [ ] Set `lang` and `dir` on the page (`dir="rtl"` for Arabic); use CSS logical properties (`margin-inline-start`, not `margin-left`) so layouts mirror by themselves
- [ ] A font that covers both Arabic and Latin letters; dates and numbers formatted with `Intl` for the current language, with Western digits (0–9)
- [ ] Make `npm run check` fail when a key is missing from any language file; translate the health page as the first example

**Done when**
- [ ] The health page works in all three languages, and Arabic shows right-to-left
- [ ] Deleting a key from `fr.json` makes `npm run check` fail

---

## M1 · Validation and ground truth
<!-- weeks: 1-3 -->
Check the problem with real students, and build the test data every later milestone is measured against. Mostly writing and data, in parallel with M0.
**Demo:** interview findings, a set of anonymized test profiles with agreed "correct answers", and a set of real internship postings.

### M1.1 · Interview guide and consent text
`area:research` `size:S` `depends:—`

**Goal:** A short interview guide for students, and a consent text for using a participant's anonymized CV and GitHub in our test set.

**Why:** Interviews tell us whether the problem is real and what students would trust. Consent is required before we use anyone's CV, even anonymized.

**Read first:** `docs/SPEC.md`.

**Tasks**
- [ ] 10–12 questions: how students show their skills today, what they'd be willing to share, what would make them trust a skill rating
- [ ] A short consent text: what we'll use, how we anonymize it, how to withdraw
- [ ] A 5-question version for a recruiter, in case one is reachable

**Done when**
- [ ] `docs/research/interview-guide.md` and `docs/research/consent.md` committed and reviewed by the team

### M1.2 · Student interviews
`area:research` `size:M` `depends:M1.1`

**Goal:** Notes from 6–10 interviews with students or recent graduates.

**Why:** Real answers replace our assumptions. They feed the spec update (M1.4) and the test profiles (M1.5).

**Read first:** `docs/research/interview-guide.md`.

**Tasks**
- [ ] Split the interviews across the team; aim for different fields and levels
- [ ] Write notes in `docs/research/interviews/`, one file per interview, with no names or contact details
- [ ] Ask each person for consent to use their CV/GitHub in the test set

**Done when**
- [ ] At least 6 interview notes committed

### M1.3 · Competitor review
`area:research` `size:S` `depends:—`

**Goal:** A comparison of 4–6 existing tools and the 3 things SkillGraph does that they don't.

**Why:** The presentation will be asked "doesn't X already do this?". This is the answer, and it keeps us from building what already exists.

**Read first:** `docs/SPEC.md`.

**Tasks**
- [ ] Review 4–6 tools: job boards with skill matching, CV analyzers, skill-assessment platforms
- [ ] Table: what each does, whether it uses evidence, whether it explains its results, price
- [ ] Write the 3 differences we can defend

**Done when**
- [ ] `docs/research/competitors.md` committed

### M1.4 · Findings and spec update
`area:research` `size:S` `depends:M1.2, M1.3`

**Goal:** A one-page summary of what we learned, and any resulting changes to the spec.

**Why:** Research is only useful if it changes what we build.

**Read first:** the interview notes, `docs/research/competitors.md`, `docs/SPEC.md`.

**Tasks**
- [ ] Summarize: top problems students described, what they will share, what would make them distrust the product
- [ ] Propose spec changes; the team agrees; update `docs/SPEC.md` and its changelog

**Done when**
- [ ] `docs/research/findings.md` committed; SPEC version bumped if it changed

### M1.5 · Test profiles
`area:data` `size:M` `depends:M1.1`

**Goal:** 15–20 anonymized student profiles (CV text plus a public GitHub username or repo summary) that every version of the system will be tested on.

**Why:** The final evaluation compares three versions of SkillGraph on the same inputs. These profiles are those inputs.

**Read first:** `docs/research/consent.md`.

**Tasks**
- [ ] Collect consented CVs and public GitHub usernames; write realistic made-up profiles to fill gaps (different fields, levels, amounts of evidence and languages: at least 5 in French and 3 in Arabic, plus some that mix languages)
- [ ] Remove names, emails, phone numbers and addresses
- [ ] Commit only the made-up profiles, under `backend/eval/data/profiles/`, with a README explaining how they were written
- [ ] Keep real, consented profiles (CV text and GitHub username) out of the repo (D-013): in the team's private folder, copied by each member into `backend/eval/data/private/profiles/` (git-ignored); the README says where to get them

**Done when**
- [ ] At least 15 profiles in total, including French and Arabic ones; nothing from a real person is committed (`git status` shows `backend/eval/data/private/` ignored)

### M1.6 · Labeling guide and correct answers
`area:data` `size:L` `depends:M1.5, M2.3`

**Goal:** For every test profile, the agreed list of its skills and each skill's correct status, written by people.

**Why:** These labels are the answer key. Every accuracy number in the final evaluation is the system's output compared with them, so they must be careful and agreed.

**Read first:** `docs/design/evidence-model.md`; GLOSSARY: evidence, status, ground truth.

**Tasks**
- [ ] Labeling guide: which skills count and how to decide each status, with examples
- [ ] French and Arabic profiles are labeled by members fluent in that language
- [ ] Two members label each profile separately; then compare, discuss disagreements and settle them; record how often they agreed at first
- [ ] Save labels as JSON in `backend/eval/data/labels/` (made-up profiles) and `backend/eval/data/private/labels/` (real profiles, never committed, D-013), with the format described in a README

**Done when**
- [ ] Every profile labeled by two people, disagreements settled, agreement rate recorded

### M1.7 · Curated postings and match labels
`area:data` `size:M` `depends:M1.5`

**Goal:** 25–40 real internship and junior job postings, plus at least 40 profile × posting pairs labeled "relevant" or "not relevant".

**Why:** Matching needs real postings to match against, and the relevance labels are the answer key for "matching precision" in the evaluation.

**Read first:** `docs/SPEC.md` (non-goals: no scraping).

**Tasks**
- [ ] Collect postings by hand from legitimate sources: text, source link, date; respect each site's terms
- [ ] Include both good and bad fits for the test profiles, and postings in French and Arabic as well as English (local postings are often in French)
- [ ] Store in `backend/eval/data/opportunities/` and as a seed file the app can load
- [ ] Label at least 40 profile × posting pairs as relevant / not relevant

**Done when**
- [ ] ≥25 postings and ≥40 labeled pairs committed

---

## M2 · Contracts and the risky spike
<!-- weeks: 3-4 -->
Agree on the definitions everyone builds on (evidence, database tables, agent messages, API), and test the biggest unknown early: can a free LLM judge evidence well enough?
**Demo:** a written comparison of free LLMs on our test profiles, and the agreed evidence model, database schema, message format and API.

### M2.1 · LLM spike: can a free model judge evidence?
`area:ai` `size:M` `depends:M1.5`

**Goal:** A measured comparison of 2–3 free LLM options on 5 test profiles, and a decision on which one we use.

**Why:** The whole agent design depends on an LLM that is free, fast enough and good enough. If none is, we need to know in week 4, not week 9. French and Arabic are the biggest unknown: small free models are often much weaker in them than in English.

**Read first:** decision D-005; GLOSSARY: LLM, spike, rate limit.

**Tasks**
- [ ] Choose 2–3 options that cost nothing (free tiers of hosted APIs, a small local model via Ollama); write down their current limits and terms
- [ ] A throwaway script in `spikes/` that asks each one to list skills and judge evidence for 5 profiles (at least one French and one Arabic CV), with answers requested in each of the three languages
- [ ] Compare the answers by hand against what a person would say; measure response time, rate-limit errors and how often the output is valid JSON
- [ ] Recommend one option; decide D-005

**Done when**
- [ ] `docs/spikes/llm.md` with the comparison table, broken down by language, committed; D-005 marked Decided

### M2.2 · LLM client with record/replay
`area:ai` `size:M` `depends:M2.1, M0.2`

**Goal:** One module, `app/llm`, that every part of the code uses to talk to the LLM. It checks the answers have the right shape, and can record answers and replay them in tests.

**Why:** One door to the LLM means we can switch models in one place. Record/replay makes tests free, fast and repeatable, which matters because free models have rate limits.

**Read first:** `docs/spikes/llm.md`; GLOSSARY: structured output, cassette, record/replay.

**Tasks**
- [ ] A provider interface: send messages plus the expected output shape, get back a checked Python object; one implementation for the D-005 choice
- [ ] If the LLM returns invalid JSON: ask it once to fix it, then raise a clear error
- [ ] Record/replay: save each answer to a file named after the request; tests only replay and never use the network
- [ ] Count tokens and time for every call

**Done when**
- [ ] Tests pass with the network off
- [ ] A live call saves a new recording
- [ ] Invalid JSON leads to one repair attempt, then a clear error (tested)

### M2.3 · Evidence model
`area:ai` `size:M` `depends:—` `contract:yes`

**Goal:** A short document that defines exactly what counts as evidence, the four skill statuses, and how confidence is expressed.

**Why:** This is the heart of SkillGraph. Labels (M1.6), rules (M4.4), agents (M6) and the UI all depend on everyone meaning the same thing by "demonstrated" or "high confidence".

**Read first:** `docs/PROJECT_REPORT.md` sections 2 (Objective 2), 4.3 and 5.1 (Evidence Evaluation Agent); GLOSSARY: evidence, status, confidence.

**Tasks**
- [ ] Evidence types, e.g. mentioned in CV skills list, described in a CV project, repo language, repo dependency, repo code, certificate, assessment
- [ ] Exact rules for claimed / demonstrated / assessed / unverified, and a confidence scale (e.g. low / medium / high, with what each means)
- [ ] Worked examples, including the report's Python REST API + PostgreSQL repo
- [ ] Name the contract owner; mark D-006 Decided

**Done when**
- [ ] `docs/design/evidence-model.md` approved by all four members; D-006 Decided

### M2.4 · Database schema v1
`area:backend` `size:M` `depends:M2.3, M0.3` `contract:yes`

**Goal:** All the main database tables, created by a migration, with a diagram explaining how they connect.

**Why:** Every feature reads or writes these tables. Getting them agreed now prevents constant schema changes that break everyone's work.

**Read first:** `docs/design/evidence-model.md`; GLOSSARY: schema, migration, cascade delete.

**Tasks**
- [ ] Tables: users, profiles, sources, evidence, skills, skill_aliases, skill_relations, user_skills, user_skill_evidence, opportunities, opportunity_requirements, matches, agent_runs, agent_messages
- [ ] Also decide where these live (own tables or fields), since later slices need them: education, experience and manual projects (M3.3), GitHub consent (M3.9), gaps and recommendations (M8.1–M8.3)
- [ ] Language fields (D-012): each user's preferred language, each source's detected language, skill names in three languages
- [ ] Diagram and short notes in `docs/design/schema.md`
- [ ] Alembic migration; tests for the important constraints and for deleting a user

**Done when**
- [ ] The migration applies and rolls back cleanly
- [ ] Deleting a user removes all of their rows (test)

### M2.5 · Agent message format
`area:agents` `size:S` `depends:M0.2` `contract:yes`

**Goal:** The exact format of the messages the orchestrator and agents send each other, and the allowed status changes of a task.

**Why:** Agents written at different times by different people must understand each other. A fixed message format is what makes them a system and not a pile of prompts.

**Read first:** `docs/PROJECT_REPORT.md` section 5.3; GLOSSARY: agent, orchestrator, state machine.

**Tasks**
- [ ] `AgentMessage` model: task id, parent task id, sender, recipient, task, context, expected output shape, status, result or error, attempt number, the language to answer in, timestamps
- [ ] Task status rules: pending → running → succeeded / failed / retrying; anything else is rejected
- [ ] Name the contract owner; mark D-007 Decided

**Done when**
- [ ] Model and status-rule tests pass; D-007 Decided

### M2.6 · API contract
`area:backend` `size:S` `depends:M2.4, M2.8` `contract:yes`

**Goal:** Every backend endpoint the MVP needs, defined with its inputs and outputs (not implemented yet), and frontend types generated from that definition.

**Why:** Frontend and backend work can then happen in parallel, by different people, without guessing what the other side sends.

**Read first:** `docs/SPEC.md` "Definition of done"; GLOSSARY: endpoint, OpenAPI.

**Tasks**
- [ ] List endpoints for: auth, profile, CV upload, GitHub connect, skills, opportunities, matches, gaps, agent runs
- [ ] Define request and response models; endpoints return "501 Not Implemented" for now
- [ ] Errors are a code plus data (e.g. `{"code": "cv.too_large", "max_mb": 5}`), never an English sentence, so the frontend can show them in any language
- [ ] Export `openapi.json`; a script that generates frontend types from it

**Done when**
- [ ] `openapi.json` committed; generating frontend types works

### M2.7 · Screen sketches
`area:frontend` `size:S` `depends:M1.4`

**Goal:** Simple sketches of every screen, agreed by the team.

**Why:** Deciding layouts on paper is much faster than in code. It also forces us to decide how to explain confidence and evidence in plain language.

**Read first:** `docs/research/findings.md`, `docs/SPEC.md`.

**Tasks**
- [ ] Sketch: sign up, profile and upload, skills and evidence, opportunities, match detail, gaps and recommendations, report, agent run timeline (any tool, even paper photos)
- [ ] For skills and matches, show how the reason and evidence are explained without unexplained scores
- [ ] Sketch the skills and match screens in Arabic (right-to-left) too, and where the language switcher goes

**Done when**
- [ ] `docs/design/wireframes/` committed and reviewed by the team

### M2.8 · Language rules and term list
`area:docs` `size:S` `depends:—` `contract:yes`

**Goal:** A short guide saying which text is translated where, and SkillGraph's key terms in English, French and Arabic, so every screen and every agent uses the same words.

**Why:** With three languages and four people (plus AI) writing text, "demonstrated" could end up as three different French words and two Arabic ones. Users would be confused and the product would look unfinished.

**Read first:** decision D-012; `docs/SPEC.md`.

**Tasks**
- [ ] `docs/design/localization.md`: interface text lives in the frontend translation files; the backend sends codes plus data, never sentences; agents write directly in the user's language; quotes from CVs and repos stay in their original language and are never translated
- [ ] Term list: every key term (evidence, claimed, demonstrated, assessed, unverified, the confidence levels, match categories, gap, recommendation…) in all three languages, agreed by fluent speakers
- [ ] Style: formal or informal "you" in French (vous or tu), Modern Standard Arabic, technical names (Python, Docker) kept in Latin letters in every language

**Done when**
- [ ] Committed and approved by all four members; D-012 details marked Decided

---

## M3 · Core platform
<!-- weeks: 5-6 -->
A working app with no AI yet: accounts, profile, CV upload, GitHub connection, dashboard, account deletion.
**Demo:** sign up, fill in a profile, upload a CV, connect a GitHub username, and see them stored; then delete the account and everything is gone.

### M3.1 · Sign-up and login (backend)
`area:backend` `size:M` `depends:M2.4`

**Goal:** Users can create an account and log in, and every private endpoint knows who is calling.

**Why:** Every other feature is per user. Getting authentication right once protects everyone's data.

**Read first:** GLOSSARY: authentication, password hashing, token.

**Tasks**
- [ ] Sign-up and login with email and password, stored with a strong password hash (argon2 or bcrypt)
- [ ] Choose token or session cookie; record the choice in DECISIONS.md
- [ ] A reusable "current user" check for protected endpoints
- [ ] Tests: wrong password, expired token, no login

**Done when**
- [ ] Protected endpoints reject anonymous requests; all tests pass

### M3.2 · Sign-up and login screens
`area:frontend` `size:S` `depends:M3.1, M0.7`

**Goal:** Sign-up, login and logout pages, and pages that only logged-in users can open.

**Why:** It's the entry point of every demo and every user test.

**Read first:** `docs/design/wireframes/`; the auth endpoints in `openapi.json`.

**Tasks**
- [ ] Sign-up and login forms with clear error messages; logout; redirect anonymous users to login

**Done when**
- [ ] The full flow works in the browser against the local backend; frontend checks pass

### M3.3 · Profile API
`area:backend` `size:S` `depends:M3.1`

**Goal:** Endpoints to create, read, update and delete a user's profile, education, experience and manually entered projects.

**Why:** Manual entries are evidence too, and the profile is what everything else attaches to.

**Read first:** `docs/design/schema.md`; existing auth code.

**Tasks**
- [ ] Endpoints for profile, education, experience and projects, and for the user's preferred language
- [ ] Every endpoint checks the data belongs to the caller

**Done when**
- [ ] Tests for each operation pass; a user cannot read or change another user's data (test)

### M3.4 · Profile screens
`area:frontend` `size:M` `depends:M3.3, M3.2`

**Goal:** Pages where a user fills in and edits their profile, education, experience and projects.

**Why:** Users need a way to add information beyond their CV.

**Read first:** `docs/design/wireframes/`; profile endpoints in `openapi.json`.

**Tasks**
- [ ] Forms for each part, showing validation errors from the API

**Done when**
- [ ] A user can create, edit and delete each item in the browser

### M3.5 · CV upload and text extraction
`area:backend` `size:M` `depends:M3.1`

**Goal:** Users upload a PDF or Word CV, and the backend stores its text as a source for skill extraction.

**Why:** The CV is the main input for skills. Everything in M4 and M6 reads this text.

**Read first:** `docs/design/schema.md` (sources); GLOSSARY: source.

**Tasks**
- [ ] Upload endpoint for PDF/DOCX with size and type limits; files stored outside any public folder
- [ ] Extract the text (pypdf, python-docx); scanned or broken files return a clear error instead of crashing
- [ ] Detect the CV's language (English, French or Arabic) and save it with the source
- [ ] Check Arabic PDFs come out readable (some extractors reverse or break Arabic letters); if pypdf fails, compare another extractor and record the choice
- [ ] Tests with made-up CV files in all three languages

**Done when**
- [ ] Uploading a test CV in each language stores readable text and the right language; bad files get clear errors (tests)

### M3.6 · GitHub import
`area:backend` `size:M` `depends:M3.1`

**Goal:** Given a GitHub username, the backend imports the user's public repositories: languages, topics, README, dependency files and how much of the code they wrote.

**Why:** Repos are the strongest evidence a student usually has. This is what makes "demonstrated" possible.

**Read first:** decision D-009; GLOSSARY: rate limit, fixture.

**Tasks**
- [ ] Decide D-009 (public username or GitHub login)
- [ ] Fetch repos, languages, topics, README and dependency files (requirements.txt, pyproject.toml, package.json, pom.xml), plus commit counts by the user
- [ ] Handle GitHub's rate limit; cache responses; optional token from `.env`
- [ ] Tests use saved example responses, never the live API

**Done when**
- [ ] Importing a test account stores its repo information; tests run offline

### M3.7 · Upload and GitHub screens
`area:frontend` `size:S` `depends:M3.5, M3.6, M3.4`

**Goal:** Users upload their CV and connect GitHub from the browser, and see their sources listed.

**Why:** Without this, the evidence pipeline can only be used from tests.

**Read first:** `docs/design/wireframes/`; upload and GitHub endpoints in `openapi.json`.

**Tasks**
- [ ] CV upload with progress and errors; GitHub connect with a clear consent message; list of sources

**Done when**
- [ ] Both flows work end to end against the local backend

### M3.8 · Dashboard layout
`area:frontend` `size:S` `depends:M3.4`

**Goal:** The main page after login, with sections for skills, opportunities, gaps and recent activity (placeholders for now).

**Why:** Later milestones fill these sections in. Agreeing the layout now keeps the app coherent.

**Read first:** `docs/design/wireframes/`.

**Tasks**
- [ ] Layout and navigation with placeholder sections

**Done when**
- [ ] Dashboard shows for a logged-in user; frontend checks pass

### M3.9 · Account and data deletion
`area:backend` `size:S` `depends:M3.5, M3.6`

**Goal:** A user can delete their account, which removes every row and file we hold about them. GitHub import asks for consent first.

**Why:** We handle CVs, which are personal data. Deletion and consent are basic obligations, and the presentation will be asked about privacy.

**Read first:** `docs/design/schema.md` (cascade deletes); SPEC constraints.

**Tasks**
- [ ] Delete-account endpoint removing database rows and stored files
- [ ] Record consent before GitHub import; the import refuses without it

**Done when**
- [ ] A test proves no rows or files remain after deletion

---

## M4 · Skills and the rule-based baseline
<!-- weeks: 6-7 -->
Turn CVs and repos into skills with evidence, using fixed rules and no AI. This is "System A" in the final comparison, and a working fallback if the agents disappoint.
**Demo:** upload a CV and import GitHub, and see every skill with its status, confidence and the evidence behind it; plus the first accuracy numbers.

### M4.1 · Skill list data
`area:data` `size:M` `depends:M1.7`

**Goal:** CSV files listing 150–300 skills, their other names, and which skills belong under which (PostgreSQL → SQL → Databases).

**Why:** "Postgres", "postgresql" and "PostgreSQL" must count as one skill, or matching fails. The parent links let a profile show broader abilities like "databases".

**Read first:** the curated postings (M1.7); GLOSSARY: taxonomy, alias.

**Tasks**
- [ ] `backend/app/skills/data/skills.csv` (id, name_en, category; French and Arabic names come in M4.9), covering every skill in the curated postings and test profiles
- [ ] `aliases.csv` (alias, skill_id): "Postgres" → postgresql, "JS" → javascript
- [ ] `relations.csv` (child_id, parent_id): postgresql → sql → databases
- [ ] A short README in that folder explaining how to add a skill

**Done when**
- [ ] Every skill required by a curated posting is present; no duplicate ids or aliases

### M4.2 · Skill list loader and CV skill finder
`area:ai` `size:M` `depends:M4.1, M4.9, M3.5`

**Goal:** Load the skill list into the database, turn any spelling of a skill into its id, and find skills in CV text along with the exact sentence they came from.

**Why:** This is the first half of System A, and the normalizer is reused by every agent later.

**Read first:** `backend/app/skills/data/README.md`; `docs/design/evidence-model.md`.

**Tasks**
- [ ] Load the CSVs into the database; a function that turns text into a skill id (handles aliases, case, punctuation, French accents, and Arabic letter variants and diacritics), with tests in all three languages
- [ ] Find skills in CV text, telling apart a skills list from a project or job description
- [ ] Save each finding as evidence with the text it came from

**Done when**
- [ ] Unit tests pass; a script prints how many labeled skills were found and how many were wrong

### M4.3 · Skills from GitHub repos
`area:ai` `size:M` `depends:M4.2, M3.6`

**Goal:** Turn imported repo data (languages, dependencies, topics) into skill evidence that points to the repo and file.

**Why:** Repo evidence is what lets a skill move from "claimed" to "demonstrated".

**Read first:** `docs/design/evidence-model.md`; GitHub import code (M3.6).

**Tasks**
- [ ] Map languages, dependencies and topics to skills, giving more weight to larger, more recent repos where the user wrote most of the code
- [ ] Save evidence records pointing to the repo and file

**Done when**
- [ ] Tests on example repos produce the expected evidence

### M4.4 · Status and confidence rules
`area:ai` `size:M` `depends:M4.2, M4.3, M2.3`

**Goal:** Code that decides each skill's status and confidence from its evidence, exactly as the evidence model defines, with a plain-language reason.

**Why:** This is System A's judgement, and the agents' answers will be compared against it. It must follow the agreed rules exactly.

**Read first:** `docs/design/evidence-model.md`; GLOSSARY: property-based test.

**Tasks**
- [ ] Implement the rules: evidence → status + confidence + reason. The reason is a code plus data (e.g. `repo_dependency`, repo `shop-api`) that the frontend turns into a sentence in the user's language
- [ ] Property-based tests: more supporting evidence never lowers confidence; no evidence → unverified; only an assessment gives "assessed"

**Done when**
- [ ] All rule tests and property tests pass

### M4.5 · Build profile and skills API
`area:backend` `size:S` `depends:M4.4`

**Goal:** One call that runs the finders and rules and saves the user's skills, and an endpoint that returns them with their evidence.

**Why:** It turns the separate pieces into the feature users actually see.

**Read first:** code from M4.2–M4.4; `docs/design/schema.md`.

**Tasks**
- [ ] A service that runs extraction → rules → saves skills and evidence links; running it twice gives the same result
- [ ] `GET /skills` returning each skill with status, confidence, reason and evidence

**Done when**
- [ ] Building twice gives identical results (test); API tests pass

### M4.6 · Skills and evidence screen
`area:frontend` `size:M` `depends:M4.5, M2.7, M0.7`

**Goal:** A page listing the user's skills by status; clicking one shows the evidence and the reason in plain language. Users can flag a skill as wrong.

**Why:** "Show why, not just a score" is SkillGraph's main promise to users.

**Read first:** `docs/design/wireframes/`; `GET /skills` in `openapi.json`.

**Tasks**
- [ ] Skills grouped by status; each opens its evidence with the source text and the reason
- [ ] A way to flag a skill as wrong or add a note
- [ ] Evidence quotes shown in their original language and text direction, whatever the interface language

**Done when**
- [ ] Works end to end for a test user; frontend checks pass

### M4.7 · First evaluation script
`area:eval` `size:M` `depends:M4.2, M1.6`

**Goal:** One command that runs a version of the system on all test profiles, compares it with the labels, and writes a results table.

**Why:** We need numbers, not impressions, to know if a change helped. This script grows into the final evaluation (M9).

**Read first:** `backend/eval/data/labels/README.md`; GLOSSARY: precision, recall, F1.

**Tasks**
- [ ] `eval/run.py`: run a system on every profile; report precision, recall and F1 for skills, and accuracy for statuses
- [ ] Save results as JSON and as a markdown table in `eval/results/`

**Done when**
- [ ] The baseline's results table is produced by one command

### M4.8 · Learning resources list
`area:data` `size:S` `depends:M4.1`

**Goal:** A checked list of free learning resources per skill, which is the only place recommendations may take links from.

**Why:** LLMs invent plausible-looking links. Recommending only from this list makes that impossible.

**Read first:** `backend/app/skills/data/skills.csv`.

**Tasks**
- [ ] `backend/app/skills/data/resources.csv` (skill_id, title, url, type: course / docs / tutorial / project idea, free: yes/no, language)
- [ ] At least 2 free resources for every skill required by a curated posting; open every link to check it works
- [ ] Prefer official documentation and well-known free courses; add good free French or Arabic resources where they exist

**Done when**
- [ ] File committed; every link checked by hand

### M4.9 · Skill names and aliases in French and Arabic
`area:data` `size:M` `depends:M4.1, M2.8`

**Goal:** Every skill has a display name in English, French and Arabic, and the usual French and Arabic ways of writing it are listed as aliases.

**Why:** Many CVs and postings are in French or Arabic. If "base de données" or "قواعد البيانات" isn't recognized as "databases", matching misses obvious skills.

**Read first:** `backend/app/skills/data/README.md`; the term list in `docs/design/localization.md`.

**Tasks**
- [ ] Add `name_fr` and `name_ar` columns to `skills.csv` (tool and language names like Python stay in Latin letters)
- [ ] Add French and Arabic aliases to `aliases.csv`, including spellings with and without accents and common mixes ("dev web", "développement web")
- [ ] Check them against the French and Arabic test profiles (M1.5) and postings (M1.7)

**Done when**
- [ ] Every skill has three names, and every skill mentioned in a French or Arabic test profile or posting is found through its aliases

---

## M5 · Agent runtime
<!-- weeks: 7-8 -->
The machinery the agents run on: the agent loop, tools, the orchestrator, logging, limits and failure handling. Built and tested with fake agents before any real one exists.
**Demo:** a fake multi-step task runs through the orchestrator, survives injected failures, and its full timeline is visible.

### M5.1 · Agent loop
`area:agents` `size:M` `depends:M2.2, M2.5`

**Goal:** A small, readable loop that runs one agent: ask the LLM, run any tool it requests, check the final answer, stop after a fixed number of steps.

**Why:** Every agent runs on this loop. Writing it ourselves, instead of using a framework, is a core requirement of the project, so all four of us must be able to explain it.

**Read first:** GLOSSARY: agent, tool call, agent loop; `app/llm` (M2.2).

**Tasks**
- [ ] Agent definition: name, instructions, allowed tools, expected answer shape
- [ ] The loop, with a maximum number of steps
- [ ] Tests using a fake LLM that follows a script

**Done when**
- [ ] Tests cover: direct answer, tool use, hitting the step limit, invalid answer

### M5.2 · Tools and permissions
`area:agents` `size:M` `depends:M5.1`

**Goal:** A registry of tools agents can call, where each agent can only use the tools it was given and no tool can write to the database.

**Why:** This enforces the rule that agents read and suggest, while the backend decides what gets saved. It stops a confused agent from damaging user data.

**Read first:** CLAUDE.md "Architecture"; GLOSSARY: tool call.

**Tasks**
- [ ] Tools are typed functions with checked inputs and outputs
- [ ] Read-only tools: get profile, get evidence, get opportunity
- [ ] Each agent gets only its allowed tools

**Done when**
- [ ] An agent calling a tool it wasn't given gets a clear error (test)

### M5.3 · Orchestrator
`area:agents` `size:L` `depends:M5.2`

**Goal:** The component that turns a request into a plan of agent tasks, runs them in order, passes results between them, retries failures a limited number of times, and combines everything into one result.

**Why:** Coordination is what makes this a multi-agent system. It's the most important piece to explain at the presentation.

**Read first:** `docs/PROJECT_REPORT.md` section 5.2; GLOSSARY: orchestrator, retry with backoff.

**Tasks**
- [ ] A plan is an ordered list of steps (which agent, which task, which earlier results it needs)
- [ ] Steps exchange messages in the agreed format (M2.5)
- [ ] Limited retries with increasing waits; if an optional step fails, the result says so instead of the whole run crashing

**Done when**
- [ ] Tests with fake agents cover: success, retry then success, a required step failing, an optional step failing

### M5.4 · Run log and limits
`area:agents` `size:M` `depends:M5.3, M2.4`

**Goal:** Every agent run is saved step by step (time, tokens, errors), and every run has hard limits on LLM calls, tokens and time.

**Why:** The log lets us explain and debug any result, and it's where the evaluation's cost and latency numbers come from. Limits stop a stuck run from burning a free model's whole quota.

**Read first:** `docs/design/schema.md` (agent_runs, agent_messages).

**Tasks**
- [ ] Save runs and messages through a backend service (agents never write directly)
- [ ] Per-run limits: max LLM calls, max tokens, max time; stop with a clear reason when exceeded
- [ ] `GET /runs/{id}` returning the timeline

**Done when**
- [ ] A run that exceeds its limit stops and logs why (test)

### M5.5 · Failure tests
`area:agents` `size:M` `depends:M5.4`

**Goal:** Tests that make the fake LLM fail in every realistic way and check the system always ends in a clear, logged state.

**Why:** Free LLMs time out, hit rate limits and return nonsense. The project's objectives explicitly include recovering from failures, and this proves it.

**Read first:** GLOSSARY: fault injection.

**Tasks**
- [ ] Fake LLM that times out, returns invalid JSON, hits a rate limit, or invents skill ids
- [ ] Check that retries stay limited, every run ends in a defined state, and the log explains what happened

**Done when**
- [ ] One passing test per failure type

### M5.6 · Run timeline screen
`area:frontend` `size:S` `depends:M5.4, M0.7`

**Goal:** A page showing an agent run step by step: which agent, what status, how long, how many tokens, any errors.

**Why:** It makes the multi-agent system visible in the demo and helps everyone debug.

**Read first:** `GET /runs/{id}` in `openapi.json`; `docs/design/wireframes/`.

**Tasks**
- [ ] Timeline view of a run's steps

**Done when**
- [ ] Displays a test run correctly; frontend checks pass

---

## M6 · Profile and evidence agents
<!-- weeks: 8-9 -->
The first real agents: one finds skills in CVs and projects, one judges how well the evidence supports each skill. Then the first honest comparison with the rule-based version.
**Demo:** build a profile with the agents, see their reasons and cited evidence, and compare accuracy with System A.

### M6.1 · Prompts and example answers for the first agents
`area:ai` `size:M` `depends:M2.3, M1.6`

**Goal:** The instructions (prompts) for the Profile Agent and the Evidence Evaluation Agent, each with 6–8 example inputs and the exact answer we'd want.

**Why:** Prompts decide how the agents think, so the team should write and agree them, not leave them buried in code. The examples become tests.

**Read first:** `docs/design/evidence-model.md`; `docs/design/localization.md`; `docs/research/findings.md`; GLOSSARY: prompt, golden example.

**Tasks**
- [ ] Draft both prompts in `docs/design/prompts/`, following the evidence model; each says which language to write in, and that quotes stay in their original language
- [ ] For each agent, 6–8 examples (at least two in French and one in Arabic): input (CV excerpt or evidence bundle) → expected answer, including tricky cases: skill only listed, tiny repo, tutorial copied into a repo, vague project description
- [ ] Try the prompts in a chatbot on the examples and note where the answers went wrong

**Done when**
- [ ] Prompts and examples committed and approved by the evidence-model owner

### M6.2 · Profile Agent
`area:ai` `size:M` `depends:M5.3, M4.2, M6.1`

**Goal:** An agent that finds skills in CV text and project descriptions, maps each to the skill list, and quotes the text it came from.

**Why:** It should catch skills the rules miss (described, not named), which is the first test of whether agents add value.

**Read first:** `docs/design/prompts/`; the agent loop (M5.1).

**Tasks**
- [ ] Implement using the agreed prompt; the example answers become tests
- [ ] Reject any skill without a quoted source or with an unknown skill id
- [ ] Run the evaluation script on the test profiles

**Done when**
- [ ] Tests pass offline; its results table, broken down by language, is saved next to the baseline's

### M6.3 · Evidence Evaluation Agent
`area:ai` `size:L` `depends:M6.2, M4.4, M6.1`

**Goal:** An agent that, for each skill and its evidence, decides the status and confidence and explains why, citing the evidence it used.

**Why:** Judging evidence is SkillGraph's main idea. This agent must be careful and must never overstate a skill.

**Read first:** `docs/design/evidence-model.md`; `docs/design/prompts/`.

**Tasks**
- [ ] Implement using the agreed prompt; the example answers become tests
- [ ] Guardrails: it can never answer "assessed"; it can't cite evidence it wasn't given; weak evidence can't produce high confidence
- [ ] A test for each guardrail, and a test that reasons come back in the requested language; run the evaluation on labeled statuses

**Done when**
- [ ] Guardrail tests pass; status accuracy saved next to the baseline's

### M6.4 · "Build profile" workflow
`area:agents` `size:M` `depends:M6.3, M5.4`

**Goal:** The orchestrator runs Profile Agent → Evidence Evaluation Agent, and the backend saves the result as the user's profile.

**Why:** It's the first complete multi-agent workflow, and the profile every later feature uses.

**Read first:** orchestrator code (M5.3); `docs/design/schema.md`.

**Tasks**
- [ ] The plan: Profile Agent → Evidence Evaluation Agent (in batches) → save through the backend service
- [ ] Can be re-run; shows what changed since the last build

**Done when**
- [ ] An end-to-end test (recorded LLM answers) goes from a test user to a saved profile

### M6.5 · Agents' reasons on screen
`area:frontend` `size:S` `depends:M6.4, M4.6`

**Goal:** The skills page shows each agent's reasoning and the evidence it cited, a "rebuild profile" button, and a link to the run timeline.

**Why:** Users trust reasons they can check, not a number.

**Read first:** skills screen (M4.6); run timeline (M5.6).

**Tasks**
- [ ] Show reason and cited evidence per skill; rebuild button; link to the run

**Done when**
- [ ] Works end to end for a test user

### M6.6 · Checkpoint: rules vs agents
`area:eval` `size:S` `depends:M6.4, M4.7`

**Goal:** A short, honest comparison of the rule-based and agent-built profiles: accuracy, cost and time.

**Why:** Halfway through, we need to know if the agents help, so there's still time to change course.

**Read first:** `eval/results/`.

**Tasks**
- [ ] Run the evaluation for both; record cost and time
- [ ] Write where the agents help, where they hurt, and what to change. Improve prompts only by re-recording answers, never by editing tests

**Done when**
- [ ] `eval/results/checkpoint-m6.md` committed

---

## M7 · Opportunities and matching
<!-- weeks: 9-10 -->
Turn postings into structured requirements, then match profiles to them with explanations that cite evidence, both with rules and with an agent.
**Demo:** browse curated internships, open one, and see why you match or don't, with evidence.

### M7.1 · Opportunities in the app
`area:backend` `size:S` `depends:M1.7, M2.4`

**Goal:** The curated postings are loaded into the database and available through list and detail endpoints.

**Why:** Matching needs postings in the app, not just in data files.

**Read first:** `backend/eval/data/opportunities/`; `docs/design/schema.md`.

**Tasks**
- [ ] A loader for the curated postings; an admin-only endpoint to add one; list and detail endpoints

**Done when**
- [ ] Loaded postings are returned by the API (tests)

### M7.2 · Requirements from postings
`area:ai` `size:M` `depends:M7.1, M5.3`

**Goal:** Two ways to turn a posting's text into structured requirements (required skills, nice-to-have skills, experience, qualifications): one with rules and one with the Opportunity Agent.

**Why:** Matching compares skills with requirements, so postings must be in the same skill vocabulary as profiles.

**Read first:** skill normalizer (M4.2); agent loop (M5.1).

**Tasks**
- [ ] Rule-based extractor (for System A)
- [ ] Opportunity Agent: required vs nice-to-have skills, experience, qualifications, mapped to the skill list, for postings in any of the three languages
- [ ] Tests on example postings in all three languages

**Done when**
- [ ] Both pass their tests; the agent's output is saved through a backend service

### M7.3 · Rule-based matcher
`area:ai` `size:S` `depends:M7.2, M4.5`

**Goal:** A fixed formula that scores how well a profile covers a posting's requirements, with a template explanation.

**Why:** System A needs a matcher, and the Matching Agent must beat something simple to justify itself.

**Read first:** `docs/design/evidence-model.md`.

**Tasks**
- [ ] Score from how many required and nice-to-have skills are covered, weighted by status and confidence → category (strong / partial / weak) and score
- [ ] Explanation from a fixed template, as codes plus data so the frontend can show it in any language

**Done when**
- [ ] Tests on example pairs pass; precision on the labeled pairs recorded

### M7.4 · What a good match explanation looks like
`area:ai` `size:S` `depends:M1.7, M2.3`

**Goal:** Guidelines and 5 worked examples of the match explanations we want users to read.

**Why:** Explanations are what users see most. Agreeing on them first gives the Matching Agent a clear target and gives reviewers something to check against.

**Read first:** `docs/design/evidence-model.md`; `docs/research/findings.md`.

**Tasks**
- [ ] `docs/design/match-explanations.md`: tone, length, what must be cited, words to avoid (never imply a guarantee of being hired)
- [ ] 5 profile × posting examples with the ideal explanation, including a poor match and a borderline one, each written in English, French and Arabic

**Done when**
- [ ] Committed and reviewed by the team

### M7.5 · Matching Agent
`area:ai` `size:M` `depends:M7.3, M6.4, M7.4`

**Goal:** An agent that compares a profile with a posting, asks for a second look at weakly supported required skills, and gives a category, matched / missing / weak skills, and an explanation citing evidence.

**Why:** Matching with honest, evidence-based explanations is the user-facing payoff of the whole system.

**Read first:** `docs/design/match-explanations.md`; orchestrator code.

**Tasks**
- [ ] Compare requirements with the profile; through the orchestrator, ask the Evidence Evaluation Agent to re-check weak required skills
- [ ] Output category, matched / missing / weak skills and an explanation following the guidelines, written in the user's language
- [ ] The guideline examples become tests

**Done when**
- [ ] Tests pass offline; precision on labeled pairs recorded next to the rule-based matcher's

### M7.6 · Matching API
`area:backend` `size:S` `depends:M7.5`

**Goal:** Endpoints to run matching for a user and fetch the results.

**Why:** The frontend needs a stable way to get matches.

**Read first:** `openapi.json`; matching code.

**Tasks**
- [ ] Run and fetch endpoints, with ownership checks

**Done when**
- [ ] API tests pass

### M7.7 · Opportunities and match screens
`area:frontend` `size:M` `depends:M7.6, M2.7, M0.7`

**Goal:** A list of opportunities with each match category and top reasons, and a detail page with matched, missing and weak skills and their evidence.

**Why:** This is where a student decides what to apply for.

**Read first:** `docs/design/wireframes/`; matching endpoints in `openapi.json`.

**Tasks**
- [ ] List view and detail view

**Done when**
- [ ] Works end to end for a test user

---

## M8 · Gaps, recommendations and the full workflow
<!-- weeks: 11-12 -->
For a chosen posting, show what's missing and what to do about it, run the whole journey from the report as one workflow, and build the single-agent version for comparison.
**Demo:** one click from a student's profile to a full report: matches, gaps and concrete next steps.

### M8.1 · Gap analysis
`area:ai` `size:S` `depends:M7.5`

**Goal:** For a chosen posting, list the missing, weak and satisfied skills, most important first.

**Why:** "What should I do next?" is the question students asked most. This is the raw material for answering it.

**Read first:** matching code; `docs/design/evidence-model.md`.

**Tasks**
- [ ] Split requirements into missing / weak / satisfied; order required before nice-to-have

**Done when**
- [ ] Tests on example profiles pass

### M8.2 · Development Agent
`area:ai` `size:M` `depends:M8.1, M4.8`

**Goal:** An agent that turns each important gap into concrete next steps: a project idea that would prove the skill, a way to assess it, and resources from the checked list.

**Why:** Concrete, honest advice is what makes SkillGraph useful beyond a score.

**Read first:** `backend/app/skills/data/resources.csv`; agent loop.

**Tasks**
- [ ] Recommendations tied to a specific gap, written in the user's language, preferring resources in that language when the list has them
- [ ] Guardrail: links only from the resources list, otherwise no link

**Done when**
- [ ] Guardrail test passes; every recommendation names its gap

### M8.3 · "Find internships" workflow
`area:agents` `size:M` `depends:M8.2, M7.5`

**Goal:** The full workflow from `docs/PROJECT_REPORT.md` section 5.2, started by one request: Opportunity Agent → Matching Agent → Evidence re-check → Development Agent → one combined report.

**Why:** This is the end-to-end demonstration the project promises.

**Read first:** `docs/PROJECT_REPORT.md` section 5.2 (the example workflow); orchestrator code.

**Tasks**
- [ ] Build the plan and the combined report; the user's language is passed to every agent
- [ ] One API call starts it in the background; the frontend can poll its progress

**Done when**
- [ ] An end-to-end test (recorded LLM answers) produces a full report

### M8.4 · Report page
`area:frontend` `size:M` `depends:M8.3, M0.7`

**Goal:** One printable page with the student's skills, matches, gaps and next steps.

**Why:** It's the final thing a student takes away, and the centrepiece of the demo.

**Read first:** `docs/design/wireframes/`.

**Tasks**
- [ ] Report view with progress while the workflow runs; print-friendly (including in Arabic); link to the run timeline
- [ ] Fill the dashboard's placeholder sections (M3.8) with real data: skills, top matches, gaps, next steps

**Done when**
- [ ] Works end to end for a test user

### M8.5 · Single-agent version (System B)
`area:agents` `size:M` `depends:M8.3`

**Goal:** One agent with all the tools does the same job as the multi-agent workflow, with the same output format and the same limits.

**Why:** Without a fair single-agent version we can't say whether multiple agents were worth it, which is the project's main technical question.

**Read first:** `docs/SPEC.md` definition of done (point 5).

**Tasks**
- [ ] Implement with the same tools, output format and limits as the multi-agent version

**Done when**
- [ ] Produces a valid report for a test user (test)

### M8.6 · End-to-end tests
`area:eval` `size:M` `depends:M8.3`

**Goal:** Automated tests that go from sign-up to the final report using recorded LLM answers, running in CI.

**Why:** They catch breakage anywhere in the journey, especially when four people change things in parallel.

**Read first:** existing tests; CI workflow.

**Tasks**
- [ ] Sign-up → upload → GitHub → profile → matches → report, in replay mode, once in each language

**Done when**
- [ ] Green in CI

---

## M9 · Evaluation
<!-- weeks: 11-13 -->
The measured comparison of System A (rules), System B (one agent) and System C (multi-agent) that the project's technical claim rests on.
**Demo:** a results table and an honest answer to "was the multi-agent design worth it?".

### M9.1 · Evaluation for all three systems
`area:eval` `size:M` `depends:M8.5, M7.3`

**Goal:** One command runs any of the three systems on the test data and reports every metric from the spec.

**Why:** Same inputs and same metrics are what make the comparison fair.

**Read first:** `docs/SPEC.md` definition of done (point 5); `eval/run.py`; GLOSSARY: precision@k.

**Tasks**
- [ ] Metrics: skill precision / recall / F1, status accuracy, matching precision@k, completion rate, time, cost (tokens), failure rate, coordination overhead
- [ ] Every quality metric also broken down by language (English, French, Arabic)

**Done when**
- [ ] One command produces the full table for any system

### M9.2 · Run and record the results
`area:eval` `size:S` `depends:M9.1`

**Goal:** At least 3 runs per system, with averages and spread, committed.

**Why:** LLM output varies between runs. One run isn't evidence.

**Read first:** `eval/run.py`.

**Tasks**
- [ ] Run each system at least 3 times; compute mean and spread; commit raw results

**Done when**
- [ ] `eval/results/final.md` committed

### M9.3 · Failure-recovery experiment
`area:eval` `size:S` `depends:M9.1, M5.5`

**Goal:** Inject failures at fixed rates into Systems B and C and compare how often each still completes, and how good the results are.

**Why:** Recovering from failures is one of the project's stated objectives. This measures it.

**Read first:** failure tests (M5.5).

**Tasks**
- [ ] Run both systems with injected failures at 2–3 rates; record completion and quality

**Done when**
- [ ] Results table committed

### M9.4 · Evaluation write-up
`area:docs` `size:M` `depends:M9.2, M9.3`

**Goal:** A chapter presenting the results, with tables, charts and an honest discussion, including where the multi-agent design didn't pay off.

**Why:** This is the answer to the project's main question, for the report and the presentation.

**Read first:** `eval/results/`.

**Tasks**
- [ ] Tables and charts; what each result means; limitations

**Done when**
- [ ] `docs/evaluation.md` reviewed by the team

### M9.5 · Manual testing pass
`area:eval` `size:M` `depends:M8.4`

**Goal:** Written test scripts for every user journey, run by hand, with every problem filed as a bug.

**Why:** Automated tests miss confusing screens and odd inputs. Better we find them than our test users.

**Read first:** README; the running app.

**Tasks**
- [ ] Test scripts in `docs/qa/` for: sign up, upload, GitHub, profile, matches, gaps, report, deletion
- [ ] Run them in all three languages, including bad inputs (scanned PDF, empty GitHub, very long CV)
- [ ] File each problem as a Bug issue with steps to reproduce

**Done when**
- [ ] Every journey run once; bugs filed

### M9.6 · Language and right-to-left review
`area:frontend` `size:M` `depends:M8.4`

**Goal:** Fluent speakers have gone through every screen and every kind of AI output in French and in Arabic, and fixed what reads badly or breaks right-to-left.

**Why:** Machine-made translations and AI text often sound unnatural, and right-to-left layouts break in small ways (arrows pointing the wrong way, mixed Arabic and English text in the wrong order). Users notice immediately.

**Read first:** `docs/design/localization.md`.

**Tasks**
- [ ] Go through every screen in French and in Arabic; fix wording in the translation files, using the agreed term list
- [ ] Check right-to-left details: arrows and icons mirrored, mixed Arabic and Latin text (e.g. "Python و Docker") in the right order, numbers and dates readable
- [ ] Generate a report for a test profile in French and in Arabic; fix the prompts where the agents' language is poor (re-record the cassettes, never edit tests to pass)

**Done when**
- [ ] No untranslated text on any screen; every problem found is fixed or filed as a Bug issue

---

## M10 · Deploy and demo
<!-- weeks: 13-14 -->
A version others can use, real feedback, documentation and the final presentation.
**Demo:** the final presentation.

### M10.1 · Hosting and deployment
`area:infra` `size:M` `depends:M8.4`

**Goal:** The app runs somewhere others can use it, or as a one-command local demo.

**Why:** User feedback and the presentation need a working app that doesn't depend on one laptop's state.

**Read first:** decision D-008.

**Tasks**
- [ ] Decide D-008 (free hosting or local demo), checking current free-tier limits
- [ ] Production settings, migrations on deploy, secrets set in the host's environment

**Done when**
- [ ] A member who didn't deploy it can use it from their own machine

### M10.2 · Privacy and security check
`area:backend` `size:S` `depends:M10.1`

**Goal:** A checked list of privacy and security basics for the demo version.

**Why:** We store CVs. A leak or crash in front of users or examiners would undermine the whole project.

**Read first:** `docs/SPEC.md` constraints.

**Tasks**
- [ ] Logs contain no CV text, tokens or passwords; file access is checked; login is rate-limited; dependencies audited for known vulnerabilities

**Done when**
- [ ] Checklist in the pull request, each item verified

### M10.3 · Demo data and script
`area:data` `size:S` `depends:M10.1`

**Goal:** Three demo personas and a written demo path, with a fallback if something fails live.

**Why:** Live demos fail. A rehearsed path with a fallback (a recorded run) protects the presentation.

**Read first:** test profiles (M1.5).

**Tasks**
- [ ] 3 personas (consented or made up) that show different outcomes, with CVs in different languages
- [ ] Step-by-step demo script and a fallback recording

**Done when**
- [ ] Demo rehearsed once end to end

### M10.4 · User feedback round
`area:research` `size:S` `depends:M10.1`

**Goal:** At least 5 students use the app; their feedback is written up and the top issues fixed or documented.

**Why:** Validating with real users is part of the project's plan, and it's strong material for the presentation.

**Read first:** `docs/research/interview-guide.md`.

**Tasks**
- [ ] Recruit 5+ students; observe or collect feedback; file issues for problems

**Done when**
- [ ] `docs/research/feedback.md` committed

### M10.5 · Documentation
`area:docs` `size:M` `depends:M9.4`

**Goal:** README, architecture, agent design, evaluation summary and limitations, clear enough for someone new.

**Why:** The final report draws on it, and examiners may read the repo.

**Read first:** `docs/` as a whole.

**Tasks**
- [ ] Write or update each document; draft the matching sections of the final report

**Done when**
- [ ] A member who didn't write it can follow it from a fresh clone

### M10.6 · Presentation and rehearsal
`area:docs` `size:S` `depends:M10.3, M10.5`

**Goal:** Slides and a rehearsed presentation covering the problem, demo, architecture, results, business model and next steps.

**Why:** It's how the project is judged.

**Read first:** `docs/evaluation.md`; `docs/research/findings.md`.

**Tasks**
- [ ] Slides; each member presents a part they can explain in depth
- [ ] Two full rehearsals with timing

**Done when**
- [ ] The final rehearsal fits the time limit
