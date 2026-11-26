# Milestones and slices

The whole project as a list of small, self-contained pieces of work.

- A **milestone** is a stage of the project with a demo at the end.
- A **slice** is one piece of work: one GitHub issue, one branch, one pull request. Anyone can take any slice whose `depends` are done, with whatever tool they use (Claude Code, the Claude chatbot, or by hand). See README "How we work".
- Weeks are targets for a 14-week semester. Milestones overlap on purpose.
- Unfamiliar word? See [GLOSSARY.md](GLOSSARY.md).
- **Three languages.** SkillGraph works in English, French and Arabic (Arabic is right-to-left). Rules: `docs/design/localization.md` (M2.8). Any slice that adds text users see adds it in all three languages, and any screen is checked in Arabic before it counts as done. One exception: assessment content (questions, tasks, their explanations) is in English and French only (D-020); the screens around it are in all three.

**MVP and beyond.** M0–M10 build the MVP and the graded deliverables (evaluation, deployed demo, report, presentation). M11–M16 build the rest of the product described in `docs/PROJECT_REPORT.md`: assessments, more evidence sources, opportunities at scale, the recruiter side, institutions, and the business layer. They are full milestones, not extras.
- **They run alongside M7–M10, not after them.** Their week ranges overlap on purpose. Start a slice when its `depends` are done and someone is free.
- **They never block the graded work.** No slice in M9 (evaluation) or M10 (deploy and demo) depends on them. If time runs short, the evaluation and the presentation still happen, and the presentation shows whatever of M11–M16 is merged.
- **Numbers are ids, not order.** M11 isn't "after M10"; the weeks and `depends` give the order.
- **Each of them starts with a decision or contract slice.** Do that one first; the rest build on it.
- **M17 (skills beyond software) is optional.** It starts only after the core project is done, and nothing depends on it.
- **New personal data is deleted with the account.** Any slice that adds a table holding a user's data (attempts, history, notifications, visibility, contact requests, institution links) makes it cascade from `users` and adds it to `tests/db/test_delete_user.py`, so account deletion (M3.9) keeps removing everything.

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
- `contract:yes` means the slice defines something everyone else builds on. Rasen approves it, and later changes need the contract owner's approval (D-018).

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

**Goal:** GitHub runs all checks automatically on every pull request and every push to `main`, and teammates can only change `main` through a reviewed pull request (Rasen, an org admin, can push directly; D-016).

**Why:** With four people merging work, this catches broken code before it reaches `main`, whoever wrote it and whatever tool they used.

**Read first:** GLOSSARY: CI, ruleset; decision D-002.

**Tasks**
- [ ] `.github/workflows/ci.yml` with a backend job (uv, ruff, mypy, pytest with a PostgreSQL service) and a frontend job (lint, check, test)
- [ ] Cache dependencies; run on pull requests and on pushes to `main`
- [ ] Run `python scripts/github_setup.py protect --check backend --check frontend` (org admins bypass the rule, D-016)

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
- [ ] Rasen reviews and merges each onboarding pull request (D-016)

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
- [ ] `docs/design/evidence-model.md` approved by Rasen; D-006 Decided

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
- [ ] Committed and approved by Rasen; D-012 details marked Decided

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
- [ ] A short privacy notice on the sign-up page, in all three languages: what we store (CV, GitHub data, profile), what it's used for, and that deleting the account removes all of it. Rasen approves the wording.

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
`area:frontend` `size:M` `depends:M3.3, M3.2, M3.10`

**Goal:** Pages where a user fills in and edits their profile, education, experience and projects.

**Why:** Users need a way to add information beyond their CV.

**Read first:** `docs/design/wireframes/`; profile endpoints in `openapi.json`.

**Tasks**
- [ ] Forms for each part, showing validation errors from the API
- [ ] A change-password form (M3.10)

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

### M3.10 · Change password
`area:backend` `size:S` `depends:M3.1`

**Goal:** A logged-in user can change their password.

**Why:** Real students will use the demo (M10.4), and there is no email reset in the MVP. Changing the password is the only way to recover from a weak or shared one.

**Read first:** `backend/app/api/auth.py`, `backend/app/services/accounts.py`; T-068, T-069.

**Tasks**
- [ ] `POST /auth/password` {current_password, new_password} → 204; a wrong current password answers 403 `wrong_password` (T-105); the new password follows the sign-up rules (T-069)
- [ ] The user stays logged in afterwards

**Done when**
- [ ] Tests: the new password works for login, the old one doesn't, and a wrong current password changes nothing

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
- [ ] `PATCH /skills/{id}` to hide or dispute a skill, with an optional note (the note needs a new column and migration). Only the caller's own skills; status and confidence don't change. Re-running the build keeps these corrections.

**Done when**
- [ ] Building twice gives identical results (test); API tests pass; hiding or disputing another user's skill answers 404 (test)

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

### M4.10 · Manual projects as evidence, and removing sources
`area:backend` `size:M` `depends:M4.5, M3.5`

**Goal:** Projects users type in count as evidence, and removing a CV, repo or project never leaves a skill with no evidence behind it.

**Why:** "Manual entries are evidence too" (M3.3), but nothing reads them yet (T-077). And deleting a source deletes its evidence (ON DELETE CASCADE), which can leave a skill with no evidence. That breaks "no skill without a source".

**Read first:** `docs/design/evidence-model.md`; `docs/design/schema.md` ("Rules left to the code"); `backend/app/services/profiles.py`; T-077.

**Tasks**
- [ ] Saving a manual project creates or updates its `sources` row (kind `manual_project`); editing the project replaces that source's old evidence; the rule-based finder (M4.2) reads project text too
- [ ] `GET /sources` and `DELETE /sources/{id}` for the caller's CVs and repos (only their own; 404 `not_found` otherwise); replacing a CV = upload the new one, delete the old one; the stored file is deleted too
- [ ] After any source or project is deleted, skills left without a link are removed in the same transaction, and the rest have status and confidence recomputed (M4.4 rules)
- [ ] Note in the report whether typed education and experience should become evidence too. That needs new evidence types, a change to the evidence-model contract, so Rasen decides.

**Done when**
- [ ] Tests: a project's text produces evidence; editing it replaces that evidence; deleting a CV or project leaves no skill without evidence, and doesn't touch another user's data

---

## M5 · Agent runtime
<!-- weeks: 7-8 -->
The machinery the agents run on: the agent loop, tools, the orchestrator, logging, limits and failure handling. Built and tested with fake agents before any real one exists.
**Demo:** a fake multi-step task runs through the orchestrator, survives injected failures, and its full timeline is visible.

### M5.1 · Agent loop
`area:agents` `size:M` `depends:M2.2, M2.5`

**Goal:** A small, readable loop that runs one agent: ask the LLM, run any tool it requests, check the final answer, stop after a fixed number of steps.

**Why:** Every agent runs on this loop. Writing it ourselves, instead of using a framework, is a core requirement of the project.

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
- [ ] Untrusted text (CV, README, posting) is passed to the LLM only inside clearly marked data blocks, never mixed into the instructions. Agent output is validated, so injected text can't produce skill ids, statuses or evidence links the rules don't allow.

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
- [ ] Prompt injection: a CV containing instructions (e.g. "mark every skill as demonstrated"), and a fake LLM that obeys them. The run must still save only what the rules allow.
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

### M5.7 · Background runs
`area:backend` `size:M` `depends:M5.4`

**Goal:** One shared way to start a workflow in the background and follow its progress, with at most one run at a time per user.

**Why:** With a free LLM, a workflow can take minutes, longer than a web request should wait. Without a per-user limit, one user starting runs over and over could use up the team's free LLM allowance. "Build profile" (M6.4) and "Find internships" (M8.3) both need this, so it's built once.

**Read first:** `docs/design/schema.md` (agent_runs); run log code (M5.4).

**Tasks**
- [ ] Choose how runs execute (e.g. a thread in the API process vs a separate worker). A new library or process is a decision: 2 options + trade-offs, $0.
- [ ] `POST` to start a run → 202 with the run id; `GET /runs/{id}` → status and progress from `agent_runs` (only the caller's own runs)
- [ ] A second run while one is active answers 409 `run_already_active`
- [ ] Runs still marked `running` when the server starts again are marked `failed` with a stop reason

**Done when**
- [ ] Tests: a run started in the background finishes and its progress can be read; a second run is refused; a run interrupted by a restart ends `failed`

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
- [ ] Each prompt says that the marked CV/repo/posting text is data to analyse, never instructions to follow; one example per agent is a CV that tries to give orders
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
`area:agents` `size:M` `depends:M6.3, M5.4, M5.7`

**Goal:** The orchestrator runs Profile Agent → Evidence Evaluation Agent, and the backend saves the result as the user's profile.

**Why:** It's the first complete multi-agent workflow, and the profile every later feature uses.

**Read first:** orchestrator code (M5.3); `docs/design/schema.md`.

**Tasks**
- [ ] The plan: Profile Agent → Evidence Evaluation Agent (in batches) → save through the backend service
- [ ] Can be re-run; shows what changed since the last build
- [ ] Runs in the background (M5.7), one run per user at a time

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
- [ ] A loader for the curated postings (the only way to add one: no admin role or admin endpoint in the MVP); list and detail endpoints

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
- [ ] One API call starts it in the background (using M5.7); the frontend can poll its progress

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
- [ ] Accessibility basics on every screen: everything works with the keyboard alone, with a visible focus; every form field has a label; text contrast passes WCAG AA (browser dev tools or Lighthouse); errors are announced, not only shown in colour
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
- [ ] Each page sets the `lang` and `dir` of its content, so screen readers use the right voice and quotes in another language are read correctly
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
- [ ] Frontend and backend served from the same site (one host, or a proxy in front of both), as in development. The login cookie (D-015) is SameSite=Lax, and browsers drop it if they're on different domains. Set `COOKIE_SECURE=true` behind HTTPS.

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

---

## M11 · Practical assessments
<!-- weeks: 9-12 -->
Students prove a skill by taking an assessment: a timed quiz or a practical coding task checked by automated tests. Passing creates `assessment` evidence, which is the only thing that can make a skill **assessed**. This is the status the MVP leaves empty (D-014).
**Demo:** a student opens a claimed skill, takes its assessment in French, passes, and the skill moves to "assessed" with the result as its evidence.

### M11.1 · Assessment design
`area:ai` `size:M` `depends:M2.3` `contract:yes`

**Goal:** A short document that defines exactly what an assessment is, what passing means, and how a result becomes evidence and changes a skill's status.

**Why:** "Assessed" is the strongest status SkillGraph gives, so it must mean something precise. Every assessment slice, the evidence rules and the agents build on this definition. It replaces D-014 ("no assessments in the MVP").

**Read first:** `docs/design/evidence-model.md` (sections 2–5, the `assessment` type); D-014; `docs/PROJECT_REPORT.md` sections 2 (Objective 2) and 4.5; GLOSSARY: assessment, practical task.

**Tasks**
- [ ] Decide D-020 (2–3 options + recommendation): which formats exist, at least (a) a timed knowledge quiz and (b) a practical task checked by automated tests; which formats can produce `assessed` and which only add confidence
- [ ] What passing means for each format (score threshold, all tests green), how many attempts and how long between them, and whether a result expires
- [ ] Be honest about cheating: assessments are unproctored. Write what they can and can't prove, and how the interface says so in plain words
- [ ] Languages: assessment content (questions, tasks, explanations) is in English and French only. With the interface in Arabic, the student picks English or French for the assessment. Add this exception to `docs/design/localization.md`
- [ ] How a result becomes evidence: an `assessment` evidence record with reason code `assessment_passed` / `assessment_failed`, pointing to the attempt; a failed attempt never lowers an existing status
- [ ] Update `docs/design/evidence-model.md` (remove the "nothing produces this in the MVP" notes, add any new reason codes) and mark D-014 "Superseded by D-020"

**Done when**
- [ ] `docs/design/assessments.md` committed, approved by Rasen; D-020 Decided; evidence model updated

### M11.2 · How to run students' code safely
`area:infra` `size:M` `depends:M11.1`

**Goal:** A tested decision on where a student's submitted code runs when a practical task is checked, without putting our server at risk and without paying anything.

**Why:** Running code written by someone else on our own server is one of the most dangerous things a web app can do: it can read secrets, attack other users or mine cryptocurrency. This has to be settled before any practical task is built.

**Read first:** `docs/design/assessments.md`; GLOSSARY: sandbox, template repository, GitHub Actions.

**Tasks**
- [ ] Decide D-021 with 2–3 options, for example: (a) the student creates a repo from our template and GitHub Actions runs the tests on GitHub's machines, and we only read the result through the GitHub API; (b) a locked-down container on our own host; (c) no code execution, quizzes only
- [ ] Spike for the recommended option in `spikes/`: one tiny task, one passing and one failing submission, and reading the result back
- [ ] Write down what a student could fake (e.g. editing the tests in their own repo) and how the design limits it (e.g. checking the test files are unchanged)

**Done when**
- [ ] `docs/spikes/code-execution.md` with the spike results committed; D-021 Decided

### M11.3 · Question bank format and first questions
`area:data` `size:L` `depends:M11.1, M4.1, M2.8, M1.7`

**Goal:** A reviewed set of quiz questions, in English and French, for the skills the curated postings ask for most.

**Why:** Quizzes are only as good as their questions. Wrong answer keys or ambiguous wording would mark people "assessed" for the wrong reasons.

**Read first:** `docs/design/assessments.md`; `docs/design/localization.md` (term list); `backend/app/skills/data/skills.csv`.

**Tasks**
- [ ] A file format under `backend/app/assessments/data/` (one file per skill): question, options, correct answer, short explanation, difficulty, in English and French
- [ ] Questions for the 20 skills most required by the curated postings (M1.7): at least 8 per skill across three difficulty levels
- [ ] Every question checked by a second member who knows the skill; French checked by a fluent speaker
- [ ] Write original questions; never copy from copyrighted question banks or certification exams
- [ ] A check that fails on a missing English or French version, a missing answer key or a duplicate question

**Done when**
- [ ] 20 skills × ≥8 questions committed, every one reviewed; the check passes

### M11.4 · Assessment tables and API
`area:backend` `size:M` `depends:M11.1, M2.4, M3.1`

**Goal:** The backend can list the assessments available for a skill, start an attempt, accept answers, grade them, and store the result.

**Why:** Grading must happen on the server. If the browser knew the answers or the timer, anyone could cheat with the browser's developer tools.

**Read first:** `docs/design/assessments.md`; `docs/design/schema.md` ("Changing the schema").

**Tasks**
- [ ] Tables for assessment definitions, attempts and answers (migration), following D-019's conventions; attempts deleted with the user
- [ ] Endpoints: list assessments for a skill, start an attempt (random draw of questions, server-side start time), submit, get the result
- [ ] The answer key is never sent to the browser; a submission after the time limit is graded as incomplete
- [ ] Attempt limits and waiting time between attempts as D-020 defines; errors as codes (`attempt_limit_reached`, `assessment_expired`)

**Done when**
- [ ] Tests: a full attempt is graded correctly; a late submission isn't accepted as a pass; the answer key never appears in any response; limits are enforced

### M11.5 · Quiz screens
`area:frontend` `size:M` `depends:M11.4, M0.7`

**Goal:** A student starts a quiz from a skill's page, answers with a visible timer, and sees the result with explanations.

**Why:** It's the part of assessments students actually touch. It has to be clear and calm, and correct right-to-left.

**Read first:** `docs/design/wireframes/`; the assessment endpoints in `openapi.json`.

**Tasks**
- [ ] "Take the assessment" on a skill's page, with the rules shown first (time, attempts, what passing means, that it's unproctored)
- [ ] Question screen with a timer and progress; results with explanations after submitting; when the next attempt is allowed
- [ ] The screens around the questions follow the interface language (all three, right-to-left in Arabic); the questions themselves are in English or French, chosen by the student before starting
- [ ] Usable with the keyboard alone

**Done when**
- [ ] A full quiz works end to end in English and in French, including with the interface in Arabic; frontend checks pass

### M11.6 · Practical tasks
`area:backend` `size:L` `depends:M11.2, M11.4, M3.6`

**Goal:** Practical tasks a student can take: they get the task, submit their solution the way D-021 defines, and the backend records pass or fail from the automated tests.

**Why:** A practical task is the strongest proof of a skill SkillGraph can offer, much closer to "can actually do it" than a quiz.

**Read first:** `docs/spikes/code-execution.md`; `docs/design/assessments.md`; GitHub import code (M3.6).

**Tasks**
- [ ] A task format: statement in English and French, starting files, tests, time allowed, the skill(s) it assesses
- [ ] At least 3 tasks for the most requested skills (e.g. Python, SQL, a REST API)
- [ ] Submission and checking exactly as D-021 decided; the submitting GitHub account must be the one on the student's profile
- [ ] Detect the tricks listed in M11.2 (e.g. changed test files) and grade them as failed with a reason code

**Done when**
- [ ] Tests (on recorded GitHub responses): a correct solution passes, a wrong one fails, a solution with edited tests fails

### M11.7 · Practical task screens
`area:frontend` `size:S` `depends:M11.6, M0.7`

**Goal:** A student reads a task, gets the starting files, submits, and follows the checking until the result appears.

**Why:** Checking can take minutes; the student needs to see what's happening instead of a frozen page.

**Read first:** `docs/design/wireframes/`; practical task endpoints in `openapi.json`.

**Tasks**
- [ ] Task page with statement, starting files link, submit step and live status (waiting, checking, passed, failed with the reason)

**Done when**
- [ ] Works end to end against recorded results; the page follows the interface language and shows the task statement in English or French; frontend checks pass

### M11.8 · Assessment results as evidence
`area:ai` `size:M` `depends:M11.4, M4.4`

**Goal:** A passed assessment creates `assessment` evidence, and the existing status and confidence rules turn it into **assessed**, in all three systems.

**Why:** This connects assessments to the rest of SkillGraph: profiles, matching and gaps start using the strongest status.

**Read first:** `docs/design/evidence-model.md`; `docs/design/assessments.md`; status rules code (M4.4).

**Tasks**
- [ ] A service turns a graded attempt into an evidence record and a link (`supports` / `weak` by result) and rebuilds the user's profile
- [ ] Update the validator: `assessed` is now allowed, but **only** when the skill has a supporting `assessment` link. Agents still never decide `assessed` on their own
- [ ] Property tests: a failed attempt never lowers a status; passing always gives `assessed`; removing the assessment evidence removes `assessed`

**Done when**
- [ ] All rule and property tests pass; a test user who passes a quiz shows the skill as assessed through the API

### M11.9 · Assessment Agent: drafting questions with human approval
`area:agents` `size:M` `depends:M11.3, M5.3`

**Goal:** An agent that drafts new quiz questions for a skill in English and French, which go live only after a person approves them.

**Why:** Writing hundreds of good questions by hand doesn't scale. The project report also asks for human approval of consequential actions: an agent-written question that marks people "assessed" is exactly that.

**Read first:** question bank format (M11.3); agent loop (M5.1); `docs/design/localization.md`.

**Tasks**
- [ ] The agent drafts questions in the M11.3 format for a given skill and difficulty, using the term list
- [ ] Drafts are stored as `pending`; a review screen (or command, for a start) lets a reviewer approve, edit or reject each one; only approved questions are ever used
- [ ] Guardrails tested: exactly one correct option, no near-duplicate of an existing question, both English and French present

**Done when**
- [ ] Tests (recorded LLM answers) pass; no `pending` question can appear in an attempt (test)

### M11.10 · Assessments in matching and recommendations
`area:ai` `size:S` `depends:M11.8, M8.2`

**Goal:** The Development Agent recommends a specific assessment when a skill is only claimed or weak, and matching treats assessed skills as the strongest evidence.

**Why:** Assessments only help students if the product points them to the right one at the right time.

**Read first:** Development Agent (M8.2); matching code (M7.3, M7.5).

**Tasks**
- [ ] Recommendations can name an available assessment for a gap; never one that doesn't exist (tested)
- [ ] The rule-based matcher and the Matching Agent's explanation account for `assessed`

**Done when**
- [ ] Tests on example profiles pass in all three languages

### M11.11 · Assessment pilot
`area:research` `size:S` `depends:M11.5, M11.8`

**Goal:** At least 5 students take real assessments and their results and feedback are written up.

**Why:** Only real attempts show whether questions are too easy, too hard or confusing.

**Read first:** `docs/research/interview-guide.md`; `docs/design/assessments.md`.

**Tasks**
- [ ] 5+ students take at least two assessments each; record pass rates and time taken per question, never names
- [ ] Remove or fix questions that almost everyone gets right or wrong, or that confused people

**Done when**
- [ ] `docs/research/assessment-pilot.md` committed; flagged questions fixed or removed

---

## M12 · More evidence sources and a living profile
<!-- weeks: 8-11 -->
Profiles built from more than a CV and GitHub: certificates (with link checks where possible), portfolio websites and LinkedIn's PDF export. The profile then keeps itself up to date and shows what changed.
**Demo:** add a certificate and a portfolio site, watch the profile update, and see "Recent profile updates" on the dashboard after a weekly re-sync.

### M12.1 · Evidence model update for new sources
`area:ai` `size:S` `depends:M2.3` `contract:yes`

**Goal:** The evidence model covers certificates as their own source (with a "link checked" flag), portfolio websites and LinkedIn PDF exports.

**Why:** Every finder, rule and agent that handles these sources must agree on their types and levels before anyone writes one.

**Read first:** `docs/design/evidence-model.md`; `docs/design/schema.md`; D-019.

**Tasks**
- [ ] New source kinds and evidence types, with levels (e.g. a portfolio project is a work type, like `manual_project`; a LinkedIn export reuses the CV types)
- [ ] Whether a checked certificate link changes anything (e.g. counts towards confidence but stays a claim), with reason codes
- [ ] Worked examples for each new source; update `docs/design/schema.md` with the columns needed
- [ ] Add the new values to `backend/app/db/values.py` with a new migration; write the CHECK changes by hand (autogenerate misses them, see schema.md "Changing the schema")

**Done when**
- [ ] Evidence model and schema docs updated and approved by Rasen; the migration applies and rolls back cleanly

### M12.2 · Certificate upload and reading
`area:backend` `size:M` `depends:M12.1, M3.5`

**Goal:** A user uploads a certificate (PDF or image) and the backend extracts its title, issuer, date, credential link or id, and the skills it's about.

**Why:** Certificates are a common way students show learning, especially when they have no work experience yet.

**Read first:** `docs/design/evidence-model.md` (certificates); CV upload code (M3.5).

**Tasks**
- [ ] Upload with size and type limits; reading text from images needs an OCR library: a new dependency, so 2 options + trade-offs, $0
- [ ] Extract title, issuer, date and credential link/id; map to skills with the normalizer (M4.2)
- [ ] Tests with made-up certificates in all three languages

**Done when**
- [ ] A test certificate in each language becomes a source with correct fields and certificate evidence

### M12.3 · Certificate link check
`area:backend` `size:M` `depends:M12.2`

**Goal:** For issuers that publish credential pages, the backend opens the credential link and checks it matches the certificate (name, title), then marks it "link checked".

**Why:** Anyone can make a fake certificate PDF. A credential page on the issuer's own site is much harder to fake.

**Read first:** `docs/design/evidence-model.md`; GLOSSARY: SSRF.

**Tasks**
- [ ] A short list of supported issuers (e.g. platforms with public credential pages), each with its terms checked and recorded in DECISIONS
- [ ] Fetch only from those issuers' domains, with timeouts and size limits (no free-form URLs: SSRF)
- [ ] A check never makes a skill `assessed`; the UI says "link checked", not "verified skill"

**Done when**
- [ ] Tests on recorded pages: a matching credential passes, a mismatched name fails, an unsupported domain is refused

### M12.4 · Portfolio website import
`area:backend` `size:M` `depends:M12.1, M3.6, M3.9`

**Goal:** A user gives the address of their portfolio website, and the backend reads it and turns the projects it describes into evidence.

**Why:** Designers and front-end developers often show their work on a personal site, not on GitHub.

**Read first:** `docs/design/evidence-model.md` (portfolio type); GLOSSARY: SSRF, robots.txt.

**Tasks**
- [ ] Fetch the page (and a few linked pages on the same site) with strict limits: public addresses only (block internal and private IP ranges: SSRF), timeouts, size cap, respect robots.txt
- [ ] Ask for consent first, as for GitHub (M3.9)
- [ ] Extract project descriptions into evidence with their quotes and page addresses

**Done when**
- [ ] Tests on saved example pages pass; addresses pointing to `localhost` or private networks are refused (test)

### M12.5 · LinkedIn PDF import
`area:backend` `size:S` `depends:M12.1, M3.5`

**Goal:** A user uploads the PDF that LinkedIn's "Save to PDF" produces, and it's read like a CV with LinkedIn's known layout.

**Why:** Many students keep LinkedIn more up to date than their CV. The export is theirs to share; we never scrape LinkedIn.

**Read first:** CV upload code (M3.5); `docs/design/evidence-model.md`.

**Tasks**
- [ ] Recognize LinkedIn's export layout and map its sections (Experience, Skills, Certifications…) to the CV evidence types
- [ ] Tests with made-up exports in all three languages

**Done when**
- [ ] A made-up export produces the expected evidence; a normal CV is not mistaken for one

### M12.6 · Weekly re-sync
`area:backend` `size:M` `depends:M3.6, M5.7`

**Goal:** Once a week, each user's GitHub and portfolio sources are re-imported and their profile rebuilt, unless they turned it off.

**Why:** The project report promises "a continuously updated skills profile". A student's new repo should show up without them doing anything.

**Read first:** background runs (M5.7); GitHub import (M3.6).

**Tasks**
- [ ] Choose what starts the weekly job (e.g. a scheduler inside the backend vs a scheduled GitHub Actions call): 2 options + trade-offs, $0. Check it still runs if the free host (D-008) sleeps when idle
- [ ] A scheduled job that re-imports and rebuilds, spread out over time to stay within GitHub's and the LLM's free limits
- [ ] A per-user setting to turn it off; nothing runs for users who never gave consent

**Done when**
- [ ] Tests: a changed repo is picked up on the next run; a user who turned it off is skipped; a failed import doesn't break other users' runs

### M12.7 · Profile history
`area:backend` `size:M` `depends:M12.6, M4.5`

**Goal:** Every profile rebuild records what changed (skill added or removed, status or confidence up or down) and why, and the API returns that history.

**Why:** Users trust changes they can see explained. The report's dashboard also lists "recent profile updates".

**Read first:** profile build service (M4.5); `docs/design/schema.md`.

**Tasks**
- [ ] A table of changes per rebuild, with the cause (new source, re-sync, assessment, user correction) and the evidence behind it, as codes plus data
- [ ] `GET` history endpoint, newest first, paginated

**Done when**
- [ ] Tests: each kind of change is recorded once with its cause; deleting the account deletes the history

### M12.8 · Sources and history screens
`area:frontend` `size:M` `depends:M12.2, M12.3, M12.4, M12.5, M12.7, M0.7`

**Goal:** Users add certificates, a portfolio site and a LinkedIn export from the sources page, and see "Recent profile updates" on the dashboard.

**Why:** Without screens, the new sources only exist in tests.

**Read first:** `docs/design/wireframes/`; the new endpoints in `openapi.json`.

**Tasks**
- [ ] Add-source flows for the three new kinds, with consent where needed and clear errors
- [ ] "Recent profile updates" section on the dashboard and a full history page

**Done when**
- [ ] Each flow works end to end in all three languages; frontend checks pass

### M12.9 · Finders and agents for the new sources
`area:ai` `size:M` `depends:M12.1, M6.3, M4.4`

**Goal:** The rule-based finders and the Profile and Evidence agents handle certificates, portfolio projects and LinkedIn exports.

**Why:** New sources only help if all three systems use them, so the comparison in M9 stays fair.

**Read first:** `docs/design/evidence-model.md`; `docs/design/prompts/`.

**Tasks**
- [ ] Finders for the new types; golden examples for the agents, including French and Arabic ones
- [ ] Re-record cassettes; run the evaluation and note any change

**Done when**
- [ ] Tests pass offline; results for the new sources recorded in `eval/results/`

---

## M13 · Opportunities at scale
<!-- weeks: 10-13 -->
Opportunities stop being a hand-curated list: they come from legitimate sources and from employers who post directly, they stay fresh, and students can search them and get told about new matches.
**Demo:** an employer posts an internship, it's approved, a matching student gets a notification, and finds it again through search.

### M13.1 · Where opportunities come from
`area:research` `size:M` `depends:M1.7`

**Goal:** A decision on which sources of postings SkillGraph uses beyond hand curation, with each one's terms checked.

**Why:** Scraping job sites against their terms is a legal risk the spec rules out. We need sources we're allowed to use, ideally with local (Algerian) and remote internships.

**Read first:** `docs/SPEC.md` (non-goals); `docs/research/competitors.md`.

**Tasks**
- [ ] List candidate sources: public job APIs, RSS feeds, partner employers, university career offices; for each, coverage, format, terms and cost
- [ ] Decide D-022: which to use first (2–3 options + recommendation, $0)

**Done when**
- [ ] `docs/research/opportunity-sources.md` committed; D-022 Decided

### M13.2 · Roles and organizations
`area:backend` `size:M` `depends:M3.1, M2.4` `contract:yes`

**Goal:** Accounts can belong to an organization (employer, university, training center) with a role, and every endpoint checks roles the same way.

**Why:** Employers (M13), recruiters (M14) and institutions (M15) all need accounts that aren't students. One shared role system avoids three different, inconsistent ones. This replaces the MVP's "no admin role" rule in M7.1.

**Read first:** auth code (M3.1); `docs/design/schema.md`; GLOSSARY: role, audit log.

**Tasks**
- [ ] Decide D-023: roles (student, organization member, organization admin, platform admin) and what each may do; how an organization is created and verified
- [ ] Tables for organizations and memberships (migration); a reusable permission check for endpoints
- [ ] An audit log of sensitive actions (approvals, profile views by organizations)

**Done when**
- [ ] Tests: each role can do exactly what D-023 says and nothing more; audit entries are written

### M13.3 · Employer posting submission and moderation
`area:backend` `size:M` `depends:M13.2, M7.2`

**Goal:** A verified employer submits a posting; a platform admin approves or rejects it; approved postings go through the same requirement extraction as curated ones.

**Why:** The project report suggests letting organizations submit opportunities directly. Moderation keeps out scams and spam, which would destroy students' trust.

**Read first:** roles (M13.2); requirement extraction (M7.2).

**Tasks**
- [ ] Submit, edit, withdraw; statuses pending / approved / rejected / expired, with a reason code on rejection
- [ ] Approval runs requirement extraction and makes the posting visible to matching

**Done when**
- [ ] Tests: only approved postings are ever matched; only admins approve; withdrawing hides a posting

### M13.4 · Importers for the chosen sources
`area:backend` `size:L` `depends:M13.1, M7.2, M5.7`

**Goal:** Scheduled importers that bring in postings from the D-022 sources, normalize them and run requirement extraction.

**Why:** A matching platform with 30 postings isn't useful for long. Importers keep the list current without manual work.

**Read first:** `docs/research/opportunity-sources.md`; Opportunity Agent (M7.2).

**Tasks**
- [ ] One importer per chosen source, running in the background within each source's limits; the source and original link are kept on every posting
- [ ] Tests on saved responses; no live calls in tests

**Done when**
- [ ] Each importer passes its tests and imported postings show up in matching

### M13.5 · Duplicates, expiry and quality checks
`area:backend` `size:S` `depends:M13.4`

**Goal:** The same posting from two sources appears once, expired postings disappear, and incomplete ones are flagged.

**Why:** Duplicates and dead postings make the product look broken and waste students' time.

**Read first:** importers (M13.4).

**Tasks**
- [ ] Duplicate detection (same employer, title and close text), expiry dates and an "unknown expiry" rule, a minimum-quality check
- [ ] Students already matched to a removed posting see it marked as closed, not silently gone

**Done when**
- [ ] Tests: a duplicate is merged, an expired posting is hidden, a closed match is labeled

### M13.6 · Search and filters API
`area:backend` `size:S` `depends:M7.6`

**Goal:** Search postings by text and filter by skill, location, remote, kind, posting language and match category, with pagination.

**Why:** Once there are hundreds of postings, a list isn't enough.

**Read first:** opportunities and matching endpoints in `openapi.json`.

**Tasks**
- [ ] Search endpoint with filters and pagination; text search works in all three languages (normalization from M4.2)

**Done when**
- [ ] Tests for each filter and for French and Arabic search terms

### M13.7 · Search screens
`area:frontend` `size:M` `depends:M13.6, M7.7, M0.7`

**Goal:** Search and filter postings in the browser.

**Why:** It's how students will actually find opportunities once the list is long.

**Read first:** `docs/design/wireframes/`; search endpoint in `openapi.json`.

**Tasks**
- [ ] Search box, filters, results with match category, pagination; filters kept in the page address so a search can be shared

**Done when**
- [ ] Works end to end in all three languages; frontend checks pass

### M13.8 · Employer screens
`area:frontend` `size:M` `depends:M13.3, M0.7`

**Goal:** Employers create and manage their postings; platform admins see a moderation queue.

**Why:** Employers won't use an API; they need simple forms.

**Read first:** `docs/design/wireframes/`; posting endpoints.

**Tasks**
- [ ] Organization sign-up request, posting form, "my postings" with statuses; admin queue with approve / reject and a reason

**Done when**
- [ ] Both flows work end to end in all three languages

### M13.9 · Email sending
`area:backend` `size:S` `depends:M3.1`

**Goal:** The backend can send email through a free provider, with templates in three languages, and uses it for password reset.

**Why:** Notifications (M13.10) need it, and password reset is the one account feature the MVP is missing (M3.10 only changes a known password).

**Read first:** auth code (M3.1); GLOSSARY: transactional email.

**Tasks**
- [ ] Decide D-024: which email provider ($0 tier, sending limits, deliverability) vs none
- [ ] Email templates in en/fr/ar; "forgot password" flow with a one-time, expiring link
- [ ] Email verification: emails aren't checked at sign-up in the MVP (T-069), so send nothing but the verification and reset emails to an address until its owner has confirmed it. Otherwise digests could go to someone who never signed up
- [ ] In tests and development, emails are written to a file instead of sent

**Done when**
- [ ] Tests: a reset link works once and expires; no real email is sent in tests

### M13.10 · New-match notifications
`area:backend` `size:M` `depends:M13.4, M13.9, M7.5`

**Goal:** When a new posting matches a student well, they get an in-app notification and, if they chose it, a weekly email digest.

**Why:** Students won't check the site every day. Being told about a good match at the right time is a core reason to come back.

**Read first:** matching (M7.5); email sending (M13.9).

**Tasks**
- [ ] Match new postings against opted-in profiles in the background, within LLM limits (rule-based matcher first, agent only for strong candidates)
- [ ] Notifications table and API; email digest with an unsubscribe link; per-user preferences

**Done when**
- [ ] Tests: a strong new match creates one notification; preferences are respected; unsubscribing works

### M13.11 · Notification screens
`area:frontend` `size:S` `depends:M13.10, M0.7`

**Goal:** A notification bell, a notifications page, and notification preferences in settings.

**Why:** Notifications only help if they're visible and easy to control.

**Read first:** notification endpoints in `openapi.json`.

**Tasks**
- [ ] Bell with unread count, list with links to the postings, preference toggles

**Done when**
- [ ] Works end to end in all three languages; frontend checks pass

---

## M14 · Recruiter side
<!-- weeks: 11-14 -->
Employers can find students by evidenced skills, but only students who chose to be visible, only to the level they chose, and every view is logged. This is the first paying-customer side from the business model.
**Demo:** a recruiter searches for "Python, demonstrated or better", compares three opted-in candidates with evidence-based explanations, and sends a contact request that a student accepts.

### M14.1 · Privacy rules for sharing profiles
`area:docs` `size:M` `depends:M13.2` `contract:yes`

**Goal:** Clear rules for what recruiters may see, when, and how a student controls and withdraws it.

**Why:** The project report says private profile information must never go to recruiters without authorization. These rules are what every recruiter feature is checked against, and the presentation will be asked about them.

**Read first:** `docs/PROJECT_REPORT.md` section 12 (privacy); `docs/SPEC.md`; D-023.

**Tasks**
- [ ] Decide D-025: visibility levels (hidden, skills only, skills with evidence summaries), what's never shared (the CV file, contact details until the student accepts), how long views are logged
- [ ] What happens when a student turns visibility off or deletes their account: what organizations keep (e.g. nothing but anonymous audit entries), and what's removed at once (contact requests, cached profile data)
- [ ] Check what Algeria's personal data protection law (Law 18-07) requires for this kind of sharing, and write down the steps we follow; note where professional advice would be needed for a real launch
- [ ] Consent text and settings wording in all three languages

**Done when**
- [ ] `docs/design/sharing.md` committed and approved by Rasen; D-025 Decided

### M14.2 · Student visibility settings
`area:backend` `size:S` `depends:M14.1`

**Goal:** Students choose their visibility level, per D-025; it's off by default, and turning it off hides them immediately.

**Why:** Opt-in with an instant off switch is the base of trust for the whole recruiter side.

**Read first:** `docs/design/sharing.md`.

**Tasks**
- [ ] Settings stored per user; endpoints to read and change them; everything recruiter-facing reads them

**Done when**
- [ ] Tests: a hidden student never appears anywhere on the recruiter side

### M14.3 · Candidate search
`area:backend` `size:M` `depends:M14.2, M13.2`

**Goal:** Recruiters search opted-in students by required skills with a minimum status and confidence, ranked by evidence.

**Why:** "Find people who have actually shown Python" is what makes SkillGraph different from keyword search on CVs.

**Read first:** `docs/design/sharing.md`; matching code (M7.3).

**Tasks**
- [ ] Search by skills with minimum status/confidence; returns only what the visibility level allows
- [ ] Every result view and profile view written to the audit log; rate limits per organization

**Done when**
- [ ] Tests: visibility levels respected; audit entries written; results ranked as specified

### M14.4 · Candidate comparison
`area:ai` `size:M` `depends:M14.3, M7.5`

**Goal:** Compare 2–5 candidates against one posting, with an explanation for each that cites their evidence.

**Why:** Recruiters need to see why one profile fits better, not just a score.

**Read first:** `docs/design/match-explanations.md`; `docs/design/sharing.md`.

**Tasks**
- [ ] Reuse the Matching Agent per candidate; a summary table of matched, missing and weak skills
- [ ] Guardrails: never a "hire / don't hire" verdict (the spec rules out automated hiring decisions); nothing about age, gender, origin or other personal traits; tested

**Done when**
- [ ] Tests (recorded answers) pass, including the guardrails

### M14.5 · Contact requests
`area:backend` `size:S` `depends:M14.2, M13.10`

**Goal:** A recruiter sends a contact request through SkillGraph; the student accepts or declines; contact details are shared only after accepting.

**Why:** Students stay in control of who can reach them.

**Read first:** `docs/design/sharing.md`; notifications (M13.10).

**Tasks**
- [ ] Request, accept, decline, expire; the student is notified; declining reveals nothing

**Done when**
- [ ] Tests: no contact detail leaks before acceptance

### M14.6 · Recruiter screens
`area:frontend` `size:L` `depends:M14.3, M14.4, M14.5, M0.7`

**Goal:** Recruiters search, open candidate profiles at their allowed level, compare candidates and send contact requests.

**Why:** It's the product a paying customer would use.

**Read first:** `docs/design/wireframes/`; recruiter endpoints in `openapi.json`.

**Tasks**
- [ ] Search with filters, candidate view, comparison view, contact request; checked in all three languages and right-to-left

**Done when**
- [ ] The demo scenario works end to end; frontend checks pass

### M14.7 · Student privacy screens
`area:frontend` `size:M` `depends:M14.2, M14.5, M0.7`

**Goal:** Students set their visibility, see which organizations viewed their profile, and answer contact requests.

**Why:** Showing students who looked at them is what makes "opt-in" trustworthy in practice.

**Read first:** `docs/design/sharing.md`.

**Tasks**
- [ ] Visibility settings with plain explanations, "who viewed my profile", contact requests inbox

**Done when**
- [ ] Works end to end in all three languages

### M14.8 · Recruiter pilot
`area:research` `size:S` `depends:M14.6`

**Goal:** 1–3 recruiters or employers try the recruiter side; their feedback and willingness to pay are written up.

**Why:** The business model depends on recruiters paying. Their reaction is evidence for the presentation, either way.

**Read first:** `docs/research/interview-guide.md` (recruiter questions).

**Tasks**
- [ ] Recruit testers, observe them using it, ask the recruiter questions and what they would pay for

**Done when**
- [ ] `docs/research/recruiter-pilot.md` committed

---

## M15 · Universities and training organizations
<!-- weeks: 12-14 -->
Institutions see anonymous, aggregate skills data for their students: what skills they have, which gaps keep appearing against real postings, and what training would help.
**Demo:** a university sees its students' most common gaps for backend internships, with numbers, and a training recommendation.

### M15.1 · Institution data rules
`area:docs` `size:S` `depends:M14.1` `contract:yes`

**Goal:** Rules for how students link to an institution and what aggregate data institutions may see.

**Why:** Aggregates can still identify people when the group is small ("the one student in the class who…"). The rules must prevent that before any dashboard exists.

**Read first:** `docs/design/sharing.md`; GLOSSARY: minimum group size.

**Tasks**
- [ ] Decide D-026: students link with a code and explicit consent; institutions see aggregates only; minimum group size (e.g. no figure for fewer than 10 students); no individual data without the student's separate consent

**Done when**
- [ ] `docs/design/institutions.md` committed and approved by Rasen; D-026 Decided

### M15.2 · Institution accounts and student linking
`area:backend` `size:M` `depends:M15.1, M13.2`

**Goal:** An institution gets an organization account and invite codes; students link with consent and can unlink at any time.

**Why:** Linking is how an institution's data is defined, and consent is the legal and ethical basis for it.

**Read first:** `docs/design/institutions.md`; roles (M13.2).

**Tasks**
- [ ] Invite codes per institution (and per cohort, e.g. "M2 Computer Science 2026"); link and unlink endpoints

**Done when**
- [ ] Tests: linking needs consent; unlinking removes the student from every aggregate

### M15.3 · Cohort analytics
`area:backend` `size:M` `depends:M15.2, M8.1`

**Goal:** For a cohort: how many students have each skill at each status, the most common gaps against selected postings, and changes over time.

**Why:** This is the information universities said they lack in the report: which skills their students have or need.

**Read first:** `docs/design/institutions.md`; gap analysis (M8.1).

**Tasks**
- [ ] Analytics endpoints; every figure for a group below the minimum size is withheld (test)

**Done when**
- [ ] Tests on a generated cohort: correct figures; small groups hidden; no individual can be singled out by combining filters (tested on a known case)

### M15.4 · Training recommendations for a cohort
`area:ai` `size:M` `depends:M15.3, M8.2`

**Goal:** An agent turns a cohort's aggregate gaps into prioritized training suggestions, citing the figures behind each one.

**Why:** Numbers alone don't tell a department what to do next; a short, evidence-cited recommendation does.

**Read first:** cohort analytics (M15.3); Development Agent (M8.2); `backend/app/skills/data/resources.csv`.

**Tasks**
- [ ] Input is aggregates only, never individual profiles (tested); links only from the resources list

**Done when**
- [ ] Tests (recorded answers) pass in all three languages

### M15.5 · Institution dashboard
`area:frontend` `size:M` `depends:M15.3, M15.4, M0.7`

**Goal:** Charts and tables of a cohort's skills and gaps, the training recommendations, and an export.

**Why:** It's what an institution would actually look at and share internally.

**Read first:** `docs/design/wireframes/`; analytics endpoints.

**Tasks**
- [ ] Dashboard with charts, filters by cohort and posting set, export to PDF and CSV; withheld figures shown as "too few students"

**Done when**
- [ ] Works end to end in all three languages and right-to-left

### M15.6 · Institution pilot
`area:research` `size:S` `depends:M15.5`

**Goal:** One department or club tries the dashboard with a consenting group of students; feedback is written up.

**Why:** Shows whether institutions are a real customer group, as the business model assumes.

**Read first:** `docs/design/institutions.md`.

**Tasks**
- [ ] Find a willing teacher or club, run it with consenting students, collect feedback and whether they'd pay or partner

**Done when**
- [ ] `docs/research/institution-pilot.md` committed

---

## M16 · Product: plans, skill graph and polish
<!-- weeks: 12-14 -->
The pieces that turn a working app into a product: free and premium plans, a visual skill graph, a phone-friendly and accessible interface, a public landing page, and privacy-respecting usage numbers for the business case.
**Demo:** a visitor lands on the public page, signs up on a phone, explores their skill graph, and hits the free plan's limit with a clear upgrade option.

### M16.1 · Plans and usage limits
`area:backend` `size:M` `depends:M5.7, M13.2`

**Goal:** Free and premium plans with clear limits (e.g. agent runs per week, number of sources), enforced on the server, for students and organizations.

**Why:** The business model has a free and a premium tier. Limits also protect the team's free LLM allowance from heavy users.

**Read first:** `docs/PROJECT_REPORT.md` section 11 (business model); background runs (M5.7).

**Tasks**
- [ ] Decide D-027: what each plan includes for students and for organizations
- [ ] Plan on each account, limits checked in one place, errors as codes (`plan_limit_reached`) with the limit and reset time

**Done when**
- [ ] Tests: each limit is enforced and resets as specified

### M16.2 · Payments: what's possible
`area:research` `size:S` `depends:M16.1`

**Goal:** A decision on how upgrades are paid for, given what payment providers actually support in Algeria and that the project has no company or budget yet.

**Why:** Many international payment providers don't serve Algeria; local options have their own requirements. Building a payment flow on a provider we can't use would be wasted work.

**Read first:** M16.1 decisions.

**Tasks**
- [ ] Research local and international options (requirements, fees, test modes), checking current information
- [ ] Decide D-028 (2–3 options + recommendation), e.g. a provider in test mode for the demo, or activation codes handed out manually during the pilot

**Done when**
- [ ] `docs/research/payments.md` committed; D-028 Decided

### M16.3 · Upgrade flow
`area:frontend` `size:M` `depends:M16.2, M0.7`

**Goal:** Users see their plan and usage, and can upgrade the way D-028 decided (test mode or activation code).

**Why:** Shows the business model working end to end in the demo, without real money changing hands.

**Read first:** D-027, D-028.

**Tasks**
- [ ] Plan and usage page; upgrade flow; clear messages when a limit is reached, in all three languages
- [ ] Backend part of the upgrade (webhook or code redemption) with tests

**Done when**
- [ ] An upgrade raises the limits immediately (end-to-end test in test mode)

### M16.4 · Skill graph view
`area:frontend` `size:M` `depends:M4.5, M0.7`

**Goal:** An interactive graph of a user's profile: skills, how they group (PostgreSQL → SQL → databases), and the projects and evidence behind them.

**Why:** The report's core idea is a skills graph; a picture of it explains SkillGraph faster than any list, especially in the presentation.

**Read first:** `docs/PROJECT_REPORT.md` sections 4.1 and 5.4; skills API (M4.5).

**Tasks**
- [ ] Choose a graph drawing library ($0; 2 options + trade-offs)
- [ ] Nodes colored by status, sized by confidence; clicking a node shows its evidence; works right-to-left and has a list view for screen readers

**Done when**
- [ ] Works for test users with small and large profiles; frontend checks pass

### M16.5 · Is a graph database worth it?
`area:backend` `size:S` `depends:M14.3, M16.4`

**Goal:** A measured answer to whether SkillGraph should move skill relations to a graph database, now that recruiter search and the graph view exist.

**Why:** The report says a graph database "can be considered later if justified". This slice is the "later": decide with numbers, not fashion.

**Read first:** `docs/PROJECT_REPORT.md` section 5.4; D-019.

**Tasks**
- [ ] Time the heaviest relational queries (candidate search, graph view, cohort analytics) on generated data at 10× and 100× the demo size
- [ ] Recommend keep or switch; if switch, what it would cost to migrate

**Done when**
- [ ] `docs/spikes/graph-database.md` committed with measurements and a recommendation

### M16.6 · Phone and accessibility pass
`area:frontend` `size:M` `depends:M8.4, M9.5`

**Goal:** Every screen works on a phone-sized screen and with a keyboard and screen reader, in all three languages.

**Why:** Many students will open SkillGraph on their phone first. Accessibility is also expected of any real product.

**Read first:** `docs/design/localization.md`; GLOSSARY: accessibility.

**Tasks**
- [ ] Check every screen at phone width; fix layouts
- [ ] Keyboard navigation, visible focus, labels for screen readers, color contrast; start from the problems M9.5 found, and fix what fails

**Done when**
- [ ] A checklist per screen, each item passed, committed in `docs/qa/`

### M16.7 · Public landing page and onboarding
`area:frontend` `size:M` `depends:M3.2, M0.7`

**Goal:** A public page that explains SkillGraph to a visitor, and a guided first run after sign-up (upload a CV → connect GitHub → see your profile).

**Why:** Users who don't understand the product in the first minute leave. The landing page is also the first thing examiners and pilot users see.

**Read first:** `docs/research/findings.md`; `docs/SPEC.md` (goal).

**Tasks**
- [ ] Landing page in three languages: the problem, how evidence works, privacy promise, sign-up
- [ ] First-run steps with progress, skippable

**Done when**
- [ ] A new user reaches their first profile following only the on-screen steps (tested by someone outside the team)

### M16.8 · Usage numbers without tracking people
`area:backend` `size:S` `depends:M3.1, M13.2`

**Goal:** Counts of key product events (sign-ups, sources added, profiles built, matches opened, assessments taken) for the business case, without third-party trackers or personal data.

**Why:** The presentation needs real usage numbers to argue the startup case; students' privacy rules out ad-style tracking.

**Read first:** `docs/SPEC.md` (personal data constraints).

**Tasks**
- [ ] Event counts per day stored without user ids; an admin-only summary endpoint
- [ ] No cookies or scripts from other companies (tested by checking the page loads nothing from other domains)

**Done when**
- [ ] Tests pass; the summary shows the pilot's numbers

## M17 · Skills beyond software (optional)
<!-- weeks: 15-18 -->
**Optional, and only after the core project is done** (M0–M10 merged, plus whichever M11–M16 slices the team chose to finish). Nothing else depends on it. Today the skill list (M4.1) covers software engineering only, so a mathematics or biology student gets an empty or misleading profile. This milestone extends the skill list, test data and matching to other fields, one field at a time. **The list of fields is open:** mathematics and biology are the first two, and more (physics, chemistry, engineering, economics, and others) can join at any time later. See "Adding another field" at the end of this milestone. **Where evidence for these fields comes from** (publications, lab reports, competition results, other websites) is a separate question, decided later. Until then these fields use the sources that already exist (CV, certificates, portfolio, manual projects).
**Demo:** a biology student and a mathematics student each upload a CV in French, get a profile with skills from their field and the evidence behind them, and are matched against internships in their field.

### M17.1 · Which fields, and how the skill list holds them
`area:data` `size:M` `depends:M4.1, M4.9` `contract:yes`

**Goal:** A decision on which fields come first and how one skill list holds any number of fields without making the software skills harder to find or match. The structure must let a new field be added later without changing it again.

**Why:** Every other slice in this milestone builds on it. Adding fields changes the skill list's structure (the 150–300 skill limit, the categories, which aliases are safe), and that is hard to undo once profiles and postings point at skill ids.

**Read first:** `backend/app/skills/data/README.md`; `backend/tests/skills/test_skill_data.py`; `docs/research/findings.md`; D-031.

**Tasks**
- [ ] Decide D-031 (2–3 options + recommendation): which fields first (candidates: mathematics and statistics, biology and life sciences, physics, chemistry, electrical engineering, economics and finance), based on who the users are and which internships exist for them
- [ ] How a skill says which field it belongs to: a new `field` column, a top-level `area` per field linked through `relations.csv`, or both. Skills shared by several fields (statistics, Python, technical writing) stay one skill
- [ ] New categories for non-software skills (for example `method`, `technique`, `instrument`, `theory`), with examples, added to the README table and the test's `CATEGORIES`
- [ ] Replace the single 150–300 limit with one limit per field, so the list stays curated and doesn't become a dictionary. This changes an existing test on purpose; say so in the commit and issue comment
- [ ] Rules for words that mean different things in different fields ("modelling", "regression", "R", "culture", "cell"): left out of aliases, or kept with the field needed to read them
- [ ] README: how to add a whole new field (skills, aliases, relations, names in three languages, test profiles, postings)

**Done when**
- [ ] D-031 Decided; README and test updated; every existing software skill still loads and passes the structure checks unchanged

### M17.2 · Mathematics and statistics skills
`area:data` `size:M` `depends:M17.1`

**Goal:** The skills that mathematics and statistics students' CVs and internships mention, with their other names, parent links and display names in English, French and Arabic.

**Why:** Mathematics overlaps most with what already exists (statistics, data analysis, Python, R), so it's the cheapest first field and a good test of the structure from M17.1.

**Read first:** `backend/app/skills/data/README.md` (the "add a field" part from M17.1); a few real French and English mathematics internship postings.

**Tasks**
- [ ] Skills (for example linear algebra, probability, optimisation, numerical analysis, stochastic processes, LaTeX, MATLAB), reusing existing ids where they already exist
- [ ] English and French aliases ("algèbre linéaire", "probas"); display names in en, fr and ar (D-030: no Arabic aliases needed)
- [ ] Parent links into the field's area, and into existing skills where they belong (`statistics` already sits under data)

**Done when**
- [ ] `uv run pytest tests/skills` passes; every skill in the field's test profiles and postings (M17.4) is present

### M17.3 · Biology and life sciences skills
`area:data` `size:M` `depends:M17.1`

**Goal:** The same as M17.2 for biology and life sciences: lab techniques, instruments, analysis methods and software.

**Why:** Biology is far from software, so it shows whether the structure from M17.1 really works for a different kind of skill. A lab technique is shown by very different evidence than a library is.

**Read first:** as M17.2.

**Tasks**
- [ ] Skills (for example PCR, cell culture, microscopy, Western blot, bioinformatics, sequence analysis, lab safety, good laboratory practice), reusing existing ids (Python, R, statistics)
- [ ] English and French aliases ("culture cellulaire", "biologie moléculaire"); display names in en, fr and ar
- [ ] Parent links

**Done when**
- [ ] `uv run pytest tests/skills` passes; every skill in the field's test profiles and postings (M17.4) is present

### M17.4 · Test profiles, labels and postings for the new fields
`area:eval` `size:L` `depends:M17.1, M1.6, M1.7`

**Goal:** For each new field, a few anonymised test profiles with hand-written correct answers, and curated internship postings with match labels, in the same formats as M1.5–M1.7.

**Why:** Without them nobody can tell whether the new skills are found and matched well, and the evaluation numbers would only describe software students.

**Read first:** the labeling guide from M1.6; the M1.5 and M1.7 file formats.

**Tasks**
- [ ] 4–6 profiles per field (CV text in French or English, no GitHub needed), made up or anonymised with consent
- [ ] The correct skills and statuses for each, written by people following the labeling guide (labels are ground truth: Claude doesn't write them)
- [ ] 8–12 postings per field and at least 15 profile × posting pairs labeled relevant / not relevant
- [ ] Kept apart from the original dataset, so the existing evaluation numbers stay comparable

**Done when**
- [ ] Files committed and checked by a second person; the evaluation script can run on the new fields alone or together with the rest

### M17.5 · Finding skills in non-software CVs
`area:ai` `size:M` `depends:M17.2, M17.3, M17.4, M4.2, M6.2`

**Goal:** The CV skill finder and the agents find the new fields' skills, and handle words whose meaning depends on the field.

**Why:** "Culture" in a biology CV is a lab technique; in a software CV it isn't a skill at all. Rules and prompts written with software in mind need checking on other fields.

**Read first:** `backend/app/skills/` (the finder from M4.2); the Profile Agent's prompt (M6.1); M17.1's rules for field-dependent words.

**Tasks**
- [ ] Apply the field rules from M17.1 in the finder (for example, only accept a field-dependent alias when the CV is clearly from that field)
- [ ] Check the Profile and Evidence agents' prompts and example answers on the new profiles; add examples from other fields if they help
- [ ] Run the evaluation on the new fields for System A and the agents, and record the numbers next to the software numbers

**Done when**
- [ ] Tests pass; the evaluation shows results for each new field, and the software results haven't got worse

### M17.6 · Field on the profile and in matching
`area:frontend` `size:M` `depends:M17.5, M7.7`

**Goal:** A student can say which field they study, the skills screen groups skills by field, and the opportunities list can be filtered by field.

**Why:** A biology student shouldn't scroll past software internships, and a skill list that mixes fields needs grouping to stay readable.

**Read first:** profile screens (M3.4); skills screen (M4.6); opportunities screen (M7.7); `docs/design/localization.md`.

**Tasks**
- [ ] Field of study on the profile (optional, more than one allowed), through the profile API
- [ ] Skills grouped by field on the skills screen; opportunities filtered by field
- [ ] All new text in en, fr and ar, checked right-to-left; update `docs/USER_GUIDE.md`

**Done when**
- [ ] A biology test profile sees its skills grouped and biology internships first, in all three languages

**Adding another field.** M17.1 leaves a "how to add a field" checklist in the skill list README. To add a field (say, chemistry), copy M17.3's section as a new slice, `M17.<next number> · Chemistry skills`, plus a test-data slice following M17.4, both depending on M17.1. Then run `python scripts/github_setup.py setup` to create their issues. Each field is checked by the same tests and evaluation, so fields can be added one by one and in any order, by anyone.

**Not in this milestone (decided later):** which websites and sources provide evidence for these fields (publications, ORCID, lab reports, competitions, datasets), and assessments for non-software skills (M11 is built around code).
