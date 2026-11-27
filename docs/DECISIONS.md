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
| D-005 | Which free LLM (hosted free tier vs local) | Decided | M2.1 |
| D-006 | Evidence model: types, statuses, confidence | Decided (contract) | M2.3 |
| D-007 | Agent message envelope | Decided (contract) | M2.5 |
| D-008 | Hosting for the demo | Open | M10.1 |
| D-009 | GitHub: public username only vs OAuth | Decided | M3.6 |
| D-010 | How work is split and claimed | Decided | — |
| D-011 | Which tools people use | Decided | — |
| D-012 | Languages: English, French, Arabic | Decided | M0.7, M2.8 |
| D-013 | Where real participants' CVs and labels live | Decided | M1.5 |
| D-014 | Is "assessed" produced in the MVP | Decided | M2.3 |
| D-015 | Login: token vs session cookie | Decided | M3.1 |
| D-016 | Who reviews and merges (supersedes part of D-010) | Decided | M0.5 |
| D-017 | How much Claude Code does on its own for Rasen | Decided | — |
| D-018 | Only Rasen's review gates teammates' work; no code-explanation rules | Decided | — |
| D-019 | Database schema v1 conventions (ids, fixed values, sub-records, skill names) | Decided (contract) | M2.4 |
| D-020 | Assessments: formats, passing, how "assessed" is produced (supersedes D-014) | Open (contract) | M11.1 |
| D-021 | Where students' submitted code runs | Open | M11.2 |
| D-022 | Where opportunities come from beyond hand curation | Open | M13.1 |
| D-023 | Roles and organizations | Open (contract) | M13.2 |
| D-024 | Email provider | Open | M13.9 |
| D-025 | What recruiters may see, and student consent | Open (contract) | M14.1 |
| D-026 | Institution data: linking, aggregates, minimum group size | Open (contract) | M15.1 |
| D-027 | Free and premium plans | Open | M16.1 |
| D-028 | How upgrades are paid for | Open | M16.2 |
| D-029 | MVP plus full product: M11–M16 are full milestones | Decided | — |
| D-030 | CVs and postings: English and French only; Arabic is interface-only (narrows D-012) | Decided | — |
| D-033 | Typed education and experience: education counts only through a certificate; experience counts like CV experience | Decided (contract) | M4.11, M12.2 |

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
- **Status:** Decided (2026-11-27, by Claude Code on the M2.1 spike's measured results, under Rasen's instruction to finish the milestone; **Rasen to confirm or overturn**).
- **Choice:** **a local model through Ollama, `qwen2.5:7b`**, behind M2.2's provider interface. Groq's free tier (`llama-3.3-70b-versatile`) is the first upgrade to try once someone has a key.
- **Why:** measured on 5 test profiles × 3 answer languages (`docs/spikes/llm.md`): 100% valid JSON, 79% of statuses right, 97% of quotes word for word, 98% precision. `gemma3:4b` found more skills (83% vs 65%) but judged worse (71%), invented skill ids and got stuck in repeat loops in Arabic. Local costs nothing, has no rate limits for the eval, and keeps real CVs on the machine. The Gemini free tier allows human review of prompts and says not to send personal data, so it's out for real CVs.
- **Trade-offs accepted:** qwen misses about a third of the skills and judges French CVs worse (48–71% status ok vs 85–100% for English). M6 should make up for that with changes that help any model (clearer rules with French examples, "list every skill", judging the rule-based finders' candidates), not qwen-specific tricks. System C needs Ollama plus ~5 GB on whatever machine runs it (affects D-008). Tests never need it (record/replay).
- **Not measured:** Groq and Gemini (no API key during the spike). Running them takes two commands; switching is a config change after M2.2.
- **Model-agnostic (Rasen, 2026-11-27):** qwen is only the *current default*, not a design target. The platform must not be tuned to one model: it may move to paid APIs with stronger models later. So: provider and model come from config only (`LLM_PROVIDER`, `LLM_MODEL`); M2.2's interface must fit hosted paid APIs (keys, rate limits, costs) as well as Ollama; prompts state the rules plainly and never rely on one model's quirks; Ollama-only settings (like `num_ctx`) stay inside the Ollama provider. The eval should be able to re-run with any provider to compare.

### D-006 · Evidence model (contract)
- **Status:** Decided (Rasen, 2026-11-23). **Contract owner: Rasen.** M2.3 writes this up in full in `docs/design/evidence-model.md` (with worked examples); Rasen approves it (D-018). Changes after that need a new D-entry approved by the owner.
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
- **Status:** Decided (2026-11-24, by Claude Code under Rasen's standing instruction to keep working and take the recommended option; **Rasen to confirm or overturn**). **Contract owner: Rasen.** Code: `backend/app/agents/runtime/messages.py`.
- **Choices:**
  1. **One immutable message per task, copied at each status change.** `start()`, `succeed()`, `fail()` and `retry()` return a new copy; the run log saves each copy. *Why:* the whole life of a task can be replayed, and no code can change a message behind another's back. *Rejected:* separate request and reply messages (two shapes to keep in sync); one mutable object (history lost).
  2. **Status rules:** pending → running → succeeded / failed / retrying, and retrying → running (attempt + 1). succeeded and failed are final; any other move raises `InvalidTransitionError`.
  3. **`expected_schema` is the name of the answer model** (e.g. `evidence_judgements_v1`), not an inline JSON Schema. *Why:* short logs; the runtime looks the model up and builds the JSON Schema for the LLM when needed. *Rejected:* inline schema (huge, repeated in every log row).
  4. **Senders and recipients are a fixed list:** orchestrator, profile, evidence, opportunity, matching, development, single_agent (System B). *Why:* typos fail at once. *Rejected:* free text.
  5. **`context` and `result` are plain JSON; errors are a code + developer note + `retryable` flag.** *Why:* agents only see what they're given (no database objects), the log stores the envelope as is, and users never see raw error text.
- **Fields:** task_id, parent_task_id, sender, recipient, task, context, expected_schema, status, result | error, attempt, language, created_at, updated_at (as in SPEC).

### D-008 · Hosting
- **Status:** Open — decided in M10.1. Options: a free hosting tier (verify current limits then) vs a reproducible local demo (Docker Compose).

### D-009 · GitHub integration
- **Status:** Decided in M3.6 (2026-11-26), recommendation taken under Rasen's standing instruction (autonomous mode); Rasen can overturn it.
- **Options:** public data by username (no secrets, simplest, can't see private repos) vs GitHub OAuth (proves account ownership, sees private repos, more work and a client secret to manage).
- **Choice:** public data by username. The import reads only public repos owned by that username, without logging in to GitHub. An optional `GITHUB_TOKEN` (the server's own token, not the user's) only raises the rate limit.
- **Why:** no client secret, no OAuth app to register, nothing to store per user, $0. Private repos aren't needed for an internship profile.
- **Consequence:** it doesn't prove the account belongs to the user. Anyone could type a stranger's username. The evidence model already says so (§3.2); OAuth can be added later without changing how repos are stored.

### D-010 · How work is split and claimed
- **Status:** Decided (Rasen)
- **Choice:** no fixed roles and no split by tool. Anyone takes any slice whose dependencies are done, by assigning themselves on the board. Assigned = in progress, merged PR = done. A claim with no commit for 3 days can be taken over after a message in the group chat. Every PR is approved by someone other than its author. Slices marked `contract` need the whole team's approval, and later changes need the named contract owner's.
- **Why:** splitting by who has which tool added complexity without helping. What matters is that every slice is clear on its own: Goal, Why, Read first, Tasks, Done when.
- **Superseded in part by D-016** (who reviews and merges) **and D-018** (contracts no longer need the whole team's approval).

### D-011 · Which tools people use
- **Status:** Decided (Rasen)
- **Choice:** each member uses what they have: Rasen uses Claude Code; teammates use the Claude chatbot (with a local setup, VS Code and GitHub Desktop for code, `docs/CHAT_KIT.md`) or any other agent (`AGENTS.md`). The workflow and the rules are the same for everyone.
- **Watch:** chatbot coding is slower and more error-prone on slices that touch many files. If one stalls, anyone can pick it up or pair on it.

### D-012 · Languages: English, French and Arabic
- **Status:** Decided (Rasen) for the three languages; details Decided in M2.8 (2026-11-25, recommendations taken under Rasen's standing instruction; Rasen approves the M2.8 commit). Full rules and term list: `docs/design/localization.md` (contract, owner Rasen). **Narrowed by D-030:** content (CVs, postings) only needs English and French.
- **Choice:** the interface, the AI's explanations and the recommendations are available in English, French and Arabic, with Arabic right-to-left. CVs, repos and postings written in any of the three are read correctly.
- **Details:**
  - English is the source language and the fallback when a translation is missing.
  - On a first visit, use the browser's language if it is one of the three, otherwise English. Users can switch at any time; the choice is saved to their account.
  - Western digits (0–9) in all three languages.
  - The backend sends codes plus data; the frontend turns them into sentences. Agents write directly in the user's language. Quotes from evidence are never translated.
  - Technical names (Python, Docker, PostgreSQL) stay in Latin letters in all three languages.
  - French uses "vous". Arabic is Modern Standard Arabic and avoids assuming the user's gender (verbal nouns for actions, impersonal messages). *Why:* a career tool shown to employers reads better formal; MSA works across every Arabic-speaking country.
  - Assessment content is the one exception: English and French only (D-020).
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
- **Later:** assessments are now planned in M11 (D-029). This entry stays in force until D-020 is Decided in M11.1, which supersedes it.

### D-015 · Login: token vs session cookie
- **Status:** Decided (2026-11-24, by Claude Code under Rasen's standing instruction to keep working and take the recommended option; **Rasen to confirm or overturn**).
- **Choice:** **a signed token (JWT) carried in an HttpOnly, SameSite=Lax cookie** (Secure in production). The token holds the user id and expires after `LOGIN_LIFETIME_HOURS` (24 h). There's no session table.
- **Why:** browser scripts can't read the cookie, so an XSS bug can't steal the login (the weak point of a token in a header). SameSite=Lax blocks cross-site form and fetch requests, which covers CSRF for our JSON API without extra tokens. No new table or migration. The frontend already calls the API on the same origin through the Vite proxy, so cookies just work.
- **Options considered:** (1) JWT in an `Authorization` header: simple API, but the frontend must store the token somewhere scripts can read; (2) server-side session in a cookie: logout can revoke at once, but needs a sessions table and a database lookup for each request; (3) **chosen**: JWT in a cookie, a mix of both.
- **Trade-off accepted:** logging out deletes the cookie, but a copied token stays valid until it expires. If revocation becomes necessary (e.g. "log out everywhere"), add a per-user token version later.
- **Libraries:** `pwdlib[argon2]` (argon2id password hashes) and `PyJWT` (tokens), the pair the current FastAPI docs use. *Rejected:* `passlib` (unmaintained) and `python-jose` (unmaintained).

### D-016 · Who reviews and merges
- **Status:** Decided (Rasen, 2026-11-23). Supersedes D-010's "every PR is approved by someone other than its author".
- **Choice:** Rasen's work (done with Claude Code) is committed and pushed straight to `main`, approved by Rasen. Teammates push their work to a branch and open a PR; Rasen reviews and merges it. In M0.5, `main` is protected for everyone except org admins (Rasen): teammates need a PR with 1 approval and green CI; Rasen can push directly.
- **Why:** Rasen is the only member with a Claude Code subscription and does the reviewing; waiting for approvals on Rasen's own work would only slow the team down.
- **Watch:** Rasen's pushes get no second reviewer, so CI (M0.5) is the only automatic check on them. Claude Code posts a short summary on the slice's issue when it pushes. (The earlier requirement that teammates be able to explain that code was removed by D-018.)

### D-017 · How much Claude Code does on its own for Rasen
- **Status:** Decided (Rasen, 2026-11-23)
- **Choice:** in Rasen's sessions, Claude Code picks any unblocked slice and starts work without waiting for a go-ahead. It stops to ask only for big or hard-to-reverse decisions (2 options + trade-offs + a recommendation), and records every answer here. Every smaller choice goes in the technical choices log, and every direct push gets a plain-language summary on its issue (D-016).
- **Delegation level:** always `Delegate`. Claude Code writes all the code; Rasen doesn't write code by hand. For slices touching agents, evidence or matching, the issue summary also walks through how the logic works, step by step.
- **Why:** keep the project moving, without it turning into a black box: Rasen must still understand and be able to explain everything, so the written record (this file, the technical choices log, issue summaries) is what keeps the project understandable.

### D-018 · Only Rasen's review gates teammates' work
- **Status:** Decided (Rasen, 2026-11-23). Supersedes D-010's "slices marked `contract` need the whole team's approval" and D-016's "teammates still need to be able to explain that code".
- **Choice:** the only thing a teammate's work has to pass is Rasen's PR review (plus green CI). There are no rules that anyone must be able to explain the code. Contracts (evidence model, schema, message format, API, language rules) are owned and approved by Rasen; they don't need the whole team's sign-off. The PR "Review guide" and Rasen's issue summaries stay, as the record of how things work, for whoever wants it.
- **Why:** this is a startup project: what matters is the product. Technical details are there to understand how it works underneath, not something every member has to master, and extra approvals only slow teammates down.

### D-019 · Database schema v1 conventions (contract)
- **Status:** Decided (Rasen, 2026-11-23). **Contract owner: Rasen.** Full write-up: `docs/design/schema.md`.
- **Choices** (all recommendations accepted):
  1. **Row ids are UUIDs.** Skills keep the readable text id from skills.csv (`postgresql`). *Why:* ids in URLs can't be guessed or counted, and they exist before saving, so agents can cite evidence ids. *Rejected:* integers (short, but guessable).
  2. **Fixed value lists are text columns with a CHECK**, listed once in `app/db/values.py`. *Why:* adding or removing a value is a simple migration. *Rejected:* PostgreSQL ENUM types (hard to change).
  3. **Mixed storage for sub-records:** education, experience and manual projects get their own tables; gaps and recommendations are JSON on `matches`; GitHub consent is a timestamp on `profiles`. *Why:* the first three are edited one at a time and a manual project is an evidence source, while gaps and recommendations are computed and read as a whole. *Rejected:* all tables (more migrations for data rewritten in one go); all JSON (no ids, no checks).
  4. **Skill names in three columns:** `name_en`, `name_fr`, `name_ar`. *Why:* matches the skills.csv plan and needs no join. *Rejected:* a translations table (any number of languages, but joins and easy-to-miss gaps).

### D-020 · Assessments (contract)
- **Status:** Open — decided in M11.1. Will supersede D-014 ("no assessments in the MVP") once Decided.
- **Already set (Rasen, 2026-11-25):** assessment content is in English and French only, not Arabic. With the interface in Arabic, the student picks English or French for the assessment.
- **Question:** which assessment formats exist (at least a timed quiz and a practical task checked by tests), which of them can produce `assessed` and which only add confidence, what passing means, attempt limits, expiry, and how honest the product is about unproctored tests.

### D-021 · Where students' submitted code runs
- **Status:** Open — decided in M11.2, after a spike.
- **Options to compare:** (a) GitHub Actions in a repo the student creates from our template, with us reading only the result; (b) a locked-down container on our own host; (c) no code execution (quizzes only). Must cost $0 and never run untrusted code next to our secrets.

### D-022 · Where opportunities come from
- **Status:** Open — decided in M13.1.
- **Constraint:** only sources whose terms allow it (no scraping against terms, SPEC non-goal). Candidates: public job APIs, RSS feeds, partner employers, university career offices, direct employer submissions (M13.3).

### D-023 · Roles and organizations (contract)
- **Status:** Open — decided in M13.2. Replaces M7.1's "no admin role in the MVP" once Decided.
- **Question:** the roles (student, organization member, organization admin, platform admin), what each may do, and how an organization is created and verified. Used by M13–M16.

### D-024 · Email provider
- **Status:** Open — decided in M13.9.
- **Question:** a free email provider (sending limits, deliverability, sign-up requirements) or no email. Used for password reset and notification digests.

### D-025 · What recruiters may see (contract)
- **Status:** Open — decided in M14.1.
- **Question:** visibility levels, what is never shared (CV file, contact details before acceptance), how long profile views are logged, and what Algeria's personal data law (Law 18-07) requires.

### D-026 · Institution data (contract)
- **Status:** Open — decided in M15.1.
- **Question:** how students link to an institution (code + consent), what aggregates institutions see, and the minimum group size below which no figure is shown.

### D-027 · Free and premium plans
- **Status:** Open — decided in M16.1.
- **Question:** what the free and premium plans include, for students and for organizations; limits also protect the free LLM allowance.

### D-028 · How upgrades are paid for
- **Status:** Open — decided in M16.2, after checking current options.
- **Question:** which payment options actually work for a team in Algeria with no company yet; fallbacks are a provider's test mode for the demo or activation codes during pilots.

### D-029 · MVP plus full product
- **Status:** Decided (Rasen, 2026-11-25)
- **Choice:** the plan covers the whole product from the project report, not only the MVP. M11–M16 (assessments, more evidence sources, opportunities at scale, recruiter side, institutions, plans and polish) are full milestones, scheduled alongside M7–M10.
- **Guard:** nothing in M9 (evaluation) or M10 (deploy and demo) depends on M11–M16, so the graded work can't be held up by them.
- **Why:** working with a strong coding agent makes a larger scope realistic; the report describes these parts, and the startup case is stronger with them.

### D-030 · Content languages: English and French only
- **Status:** Decided (Rasen, 2026-11-25). Narrows D-012.
- **Choice:** Arabic is a small addition for the interface only: the interface text, the AI's explanations and the recommendations stay available in en, fr and ar, right-to-left included. CVs, repos and postings only need to work in English and French. No slice spends effort on Arabic CVs (skill extraction, Arabic eval profiles, Arabic postings).
- **Why:** Arabic isn't a professional language for this audience; their CVs and job postings are in French or English.
- **What already exists:** M3.5 was built before this decision and handles Arabic CVs (language `ar`, Arabic test files). That code stays: it's small, tested and costs nothing to keep. An Arabic CV still uploads and is tagged `ar`; nothing later has to support it.
- **Spec:** `docs/SPEC.md` updated to match (approved by Rasen, 2026-11-26).

### D-031 · Which fields beyond software, and how the skill list holds them
- **Status:** Open — decided in M17.1 (optional milestone, after the core project). Builds on D-032.
- **Question:** which non-software fields to add first (mathematics, biology, physics, chemistry, engineering, economics…; the list stays open, more fields can join later), and how one skill list holds any number of fields: a `field` column or a top-level area per field, new categories, a size limit per field, words whose meaning depends on the field. Where evidence for these fields comes from is a separate, later decision.

### D-032 · First version: software engineering only
- **Status:** Decided (Rasen, 2026-11-26)
- **Choice:** the primary, first version of SkillGraph (M0–M16) is for software engineering: its skill list, test profiles, postings, assessments and evaluation all cover software engineering. Mathematics, biology and other fields come in M17, an optional milestone after the core project.
- **Why:** one field done well gives a working product and a clean evaluation; a structure designed in M17.1 then lets other fields join one at a time.

### D-033 · Typed education and experience as evidence (contract)
- **Status:** Decided (Rasen, 2026-11-27). Extends the evidence model (D-006). **Contract owner: Rasen.** Raised by M4.10.
- **Question:** projects typed into the profile count as evidence (M4.10). Should typed education and experience entries count too?
- **Choice:**
  1. **Education counts only when a certificate backs it.** The user uploads a diploma or course certificate and links it to the education entry. The certificate is the evidence, with the existing type `certificate`: a claim type, so at most *claimed*, but it raises confidence. A typed education entry without a certificate is not evidence.
  2. **Typed experience counts exactly like CV experience** (option B, chosen 2026-11-27 over "not evidence" and "claim only"). It uses the same evidence type, `cv_experience`, with a location saying it was typed in the app. A concrete description ("built a REST API with FastAPI") is work evidence; a vague one ("familiar with Docker") is a claim. One entry gives at most medium confidence, like one CV entry. An internship or work certificate (*attestation de stage*), once certificate upload exists, is `certificate` evidence and raises confidence.
- **Why:** education: anyone can type a degree, so a certificate is what can be checked. Experience: code written for an employer is almost never public (the company owns it, private repos, confidentiality agreements), so asking for repos would leave most real work experience unbacked. A CV's experience section already counts as work (D-006, choice 3); the same words typed into the app shouldn't count for less. The first proposal, "experience is backed only by repos and projects", was dropped for these reasons.
- **Consequences:** M4.11 reads typed experience as evidence, like M4.10 did for projects. It needs a source kind for a typed experience entry, which is a schema change for that slice to propose. M12.2 accepts certificates for education entries and for experience entries. CV sections are unchanged.

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

### M2.3 · Evidence model

These fill in details D-006 left open. They are part of the contract in `docs/design/evidence-model.md`; changing one needs the owner (Rasen).

#### T-043 · A repo language counts as work at 10 % or more
- **What:** a `repo_language` link can only be `supports` if the language is ≥ 10 % of the repo's bytes (GitHub's share), the repo is owned by the person's GitHub username, and it isn't a fork.
- **Why:** D-006 asked for "a share threshold" without a number. 10 % drops incidental files (a build script, a bit of CSS) but keeps real second languages.
- **Where:** `docs/design/evidence-model.md` §3.2, §9.6.
- **Watch out:** a guess, not measured. Revisit after M1.6 labels if it disagrees with labelers.

#### T-044 · Forked or not-owned repos never support a skill
- **What:** the owned-and-not-a-fork condition applies to `repo_code` too, not only `repo_language`.
- **Why:** code in someone else's project isn't the person's work.
- **Where:** evidence model §3.2, §9.4.

#### T-045 · Dependency, README and education links are always weak
- **What:** `repo_dependency`, `repo_readme` and `cv_education` never raise status or confidence; a validator rejects `supports` on them.
- **Why:** D-006 says they aren't enough for demonstrated, and its worked example keeps PostgreSQL at medium despite `psycopg` in `requirements.txt`. Making them always weak is the reading that matches the example and is simplest to check.
- **Where:** evidence model §2, §3.2, §7.

#### T-046 · A vague mention in a CV job or project is claimed · low
- **What:** a `cv_experience` / `cv_project` link marked `weak` (and not inferred) still makes the skill claimed, but adds nothing to confidence.
- **Why:** D-006 choice 3 says "familiar with Docker" stays claimed; choice 5 says weak evidence gives low confidence. This satisfies both.
- **Where:** evidence model §4, §5, §9.3.

#### T-047 · "Independent" means a different (source, type) pair
- **What:** confidence counts supporting links once per distinct (source, type). So a CV skills list plus a concrete CV project is high, even from one CV.
- **Why:** this follows D-006 choice 5 ("different sources or different types") literally.
- **Where:** evidence model §5, §9.2.
- **Watch out:** a CV alone can reach demonstrated · high. If that turns out to be too generous, change it to "different sources" only.

#### T-048 · Links carry a reason code from a fixed starting list
- **What:** each link has a code such as `concrete_work`, `forked_repo`, `inferred_from_related`. M4.4 and M6.3 may add codes but never reuse one with a new meaning.
- **Why:** the backend returns codes, not sentences (three languages); the UI translates them.
- **Where:** evidence model §3.4.

### M2.4 · Database schema v1

#### T-049 · Every constraint has a predictable name
- **What:** `Base.metadata` has a naming convention, so names look like `ck_evidence_type`, `uq_users_email`, `fk_<table>_<columns>_<target>`.
- **Why:** later migrations can drop or change a constraint by name without looking it up in the database.
- **Where:** `backend/app/db/base.py`.

#### T-050 · Models: one file per area; allowed values in one list
- **What:** `app/db/models/{users,sources,skills,user_skills,opportunities,agent_runs}.py`, all re-exported from `app/db/models/__init__.py`. The allowed values are `Literal` types in `app/db/values.py`; `one_of("status", Status)` turns one into a CHECK. Shared column types (`uuid_pk`, `created_at`, `user_ref`) are in `app/db/models/_columns.py`.
- **Why:** small files for chatbot-pasting; pydantic models can reuse the same `Literal` types later, so the lists can't drift apart.
- **Where:** `backend/app/db/`.
- **Watch out:** autogenerate doesn't notice a changed CHECK list. Write those migration lines by hand (see `docs/design/schema.md`).

#### T-051 · A link can only join a skill and evidence of the same user
- **What:** `user_skill_evidence` stores `user_id` and uses it in both foreign keys (to `user_skills (id, user_id)` and `evidence (id, user_id)`).
- **Why:** a bug in an agent or service can never make one person's profile cite another person's CV. The database refuses.
- **Where:** `backend/app/db/models/user_skills.py`.

#### T-052 · The 300-character quote limit is enforced by the database
- **What:** `CHECK (char_length(quote) <= 300)`. Code that cuts quotes must fit the `…` inside the 300.
- **Why:** turns the evidence model's "~300" into one exact number everyone can test against.
- **Where:** `backend/app/db/models/sources.py` (`QUOTE_MAX_CHARS`).

#### T-053 · A manual project's source points to the project, not the other way round
- **What:** `sources.manual_project_id` (unique, ON DELETE CASCADE), required exactly when `kind = 'manual_project'`.
- **Why:** deleting a project then also deletes its source and evidence, and every evidence record still has a normal `source_id`.
- **Where:** `backend/app/db/models/sources.py`.

#### T-054 · Deletes rely on the database, and there are no ORM relationships yet
- **What:** every personal table cascades from `users` in PostgreSQL. Models declare no `relationship()`s yet.
- **Why:** deleting the account works the same from SQL, the ORM or an admin tool. Relationships get added when a slice needs them.
- **Where:** all models.
- **Watch out:** when adding a `relationship()` to a parent, use `passive_deletes=True`, or SQLAlchemy may try to set children's foreign keys to NULL instead of letting the database delete them.

#### T-055 · Deleting a skill is refused while it's used; deleting a run keeps its results
- **What:** `user_skills.skill_id` and `opportunity_requirements.skill_id` are ON DELETE RESTRICT. `agent_run_id` on `user_skills` and `matches` is ON DELETE SET NULL.
- **Why:** reloading the skill list can't silently wipe profiles, and clearing old run logs doesn't delete a user's results.
- **Where:** `backend/app/db/models/user_skills.py`, `opportunities.py`.

#### T-056 · Messages keep the whole envelope as JSON until D-007
- **What:** `agent_messages.envelope` is JSONB, plus columns for ordering and listing (`sequence`, `sender`, `recipient`, `task`, `status`, `attempt`, tokens, duration). No CHECK on `status` yet.
- **Why:** the envelope is still open (M2.5); this works whatever it becomes. M2.5 can add columns in a new migration.
- **Where:** `backend/app/db/models/agent_runs.py`.

#### T-057 · Emails are stored lowercase
- **What:** `CHECK (email = lower(email))` plus a unique rule. Signup code must lowercase the email first.
- **Why:** `Ana@x.com` and `ana@x.com` can't become two accounts. Simpler than the `citext` extension.
- **Where:** `backend/app/db/models/users.py`.

#### T-058 · A test checks that the models and the migrations agree
- **What:** `test_models_match_the_migrations` runs Alembic's `compare_metadata` against the migrated test database and expects no difference. The migration test also checks the exact table list after upgrade, and that downgrade leaves only `alembic_version`. `migrations/env.py` now imports `app.db.models`, so autogenerate sees every table.
- **Why:** catches a model change without a migration.
- **Where:** `backend/tests/test_migrations.py`, `backend/migrations/env.py`.
- **Watch out:** it doesn't compare CHECK contents (see T-050).

#### T-059 · Test rows come from small factory functions
- **What:** `tests/db/factories.py` has one `make_<table>(session, …, **overrides)` per table, with made-up defaults. Constraint tests wrap each bad insert in a savepoint (`assert_rejected`), so a test can check several rules.
- **Why:** one clear pattern, no new dependency (no factory_boy).
- **Where:** `backend/tests/db/`.

### M2.5 · Agent message format

#### T-060 · Messages are frozen pydantic models; every transition re-validates
- **What:** `AgentMessage` and `TaskError` use `frozen=True, extra="forbid"`. A transition builds the new copy with `model_validate(...)`, not `model_copy(...)`, which would skip the checks.
- **Why:** a message can't end up "succeeded without a result" or "failed without an error", whatever code produced it.
- **Where:** `backend/app/agents/runtime/messages.py`.

#### T-061 · Task, schema and error names are snake_case codes
- **What:** `task`, `expected_schema` and `TaskError.code` must match `^[a-z][a-z0-9_]*$`. Schema names end in a version (`_v1`).
- **Why:** they're identifiers, not sentences (three-language rule); a version suffix lets an answer shape change without breaking old logs.
- **Where:** `backend/app/agents/runtime/messages.py`.

#### T-062 · The retry counter goes up when a retrying task starts again
- **What:** `retry()` keeps `attempt`; the next `start()` makes it `attempt + 1` and clears the error. The maximum number of attempts is a runtime limit (M5.3 / M5.4), not part of the message.
- **Why:** `attempt` always says which try the current run is.
- **Where:** `backend/app/agents/runtime/messages.py`.

#### T-063 · Two classes are called `AgentMessage`
- **What:** `app.agents.runtime.messages.AgentMessage` (the envelope) and `app.db.models.AgentMessage` (the log table row). The service that saves messages (M5.4) should import one under another name, e.g. `from app.db.models import AgentMessage as AgentMessageRow`.
- **Why:** both names come from the spec and the slice task lists; renaming the table model would be a drive-by change.
- **Where:** see above.

#### T-064 · Language codes come from `app/db/values.py`
- **What:** the envelope's `language` uses the same `Language` type as the database.
- **Why:** one list of languages in the whole backend. It's a plain constants module, so importing it doesn't give agents database access.
- **Where:** `backend/app/agents/runtime/messages.py`.

### M3.1 · Sign-up and login (backend)

#### T-065 · Auth code is split into blocks, a service and endpoints
- **What:**
  - `app/auth/`: `passwords.py` (argon2), `tokens.py` (JWT create/read), `cookies.py` (cookie settings). No database or HTTP code.
  - `app/services/accounts.py`: `sign_up`, `log_in`, raising `EmailTakenError` / `InvalidCredentialsError`.
  - `app/api/auth.py`: the endpoints.
  - `app/api/current_user.py`: the `CurrentUser` check.
- **Why:** this is the first endpoint, service and API module, so it sets the pattern: services raise domain errors and flush; endpoints map errors to HTTP and commit.
- **Where:** `backend/app/auth/`, `backend/app/services/`, `backend/app/api/`.

#### T-066 · Protect an endpoint by adding `user: CurrentUser`
- **What:** the check reads the `skillgraph_login` cookie, verifies the token and loads the user with a fresh query. Otherwise it answers 401 `not_authenticated`, `token_expired` or `token_invalid` (forged token, or the account was deleted).
- **Why:** one line per endpoint, and every failure has a code the frontend can translate.
- **Where:** `backend/app/api/current_user.py`.

#### T-067 · API errors are `{"detail": {"code": "..."}}`
- **What:** endpoints raise `HTTPException(status, detail={"code": ...})`. FastAPI's own 422 validation answer is left as it is for now.
- **Why:** the backend returns codes, not sentences (three-language rule). M2.6 (API contract) may standardise the 422 shape too.
- **Where:** `backend/app/api/`.

#### T-068 · Login gives the same answer for an unknown email and a wrong password
- **What:** both get 401 `invalid_credentials`, and an unknown email still runs a dummy password check, so it takes as long.
- **Why:** nobody can find out which emails have an account.
- **Where:** `backend/app/services/accounts.py`, `backend/app/auth/passwords.py`.

#### T-069 · Email and password rules
- **What:** the email is trimmed and lowercased, must look like `a@b.c`, at most 320 characters. The password must be 8–128 characters. The preferred language at sign-up is en/fr/ar, default en.
- **Why:** 8 characters is the usual minimum (NIST); the 128 cap stops huge inputs wasting hashing time. There's no email verification in the MVP.
- **Where:** `backend/app/api/auth.py`.

#### T-070 · New settings: `SECRET_KEY`, `LOGIN_LIFETIME_HOURS`, `COOKIE_SECURE`
- **What:**
  - `SECRET_KEY`: at least 32 characters. With `APP_ENV=prod`, the settings refuse to start if it's a known placeholder.
  - `LOGIN_LIFETIME_HOURS`: default 24.
  - `COOKIE_SECURE`: default false for http://localhost; set it to true behind HTTPS.
- **Why:** development works with no setup, and production can't run on a known key by accident.
- **Where:** `backend/app/config.py`, `.env.example`.

### M3.3 · Profile API

#### T-071 · Profile endpoints: one file per list, one shared service
- **What:** `app/api/profile.py` (`GET`/`PATCH`/`DELETE /profile`), and `education.py`, `experience.py`, `projects.py`, each with the same four endpoints (`GET` list, `POST`, `PUT /{id}`, `DELETE /{id}` under `/profile/...`). Shared input types are in `app/api/_fields.py`. All database work goes through `app/services/profiles.py`, whose functions take the model class (`Education`, `Experience`, `ManualProject`).
- **Why:** each endpoint file shows the whole pattern and can be pasted into a chatbot on its own. The ownership check is written once, in the service. A router factory would have saved about 100 lines, but it's harder to read and type-check.
- **Where:** `backend/app/api/`, `backend/app/services/profiles.py`.

#### T-072 · Another user's entry answers 404 `not_found`, not 403
- **What:** the service looks an entry up by id *and* by the caller's profile (`_owned_entry`). An id on someone else's profile is treated exactly like an id that doesn't exist.
- **Why:** 403 would confirm that the id exists. Nobody can learn anything about other users' data.
- **Where:** `backend/app/services/profiles.py`.

#### T-073 · The profile row is created empty on first use
- **What:** every profile call uses `get_or_create_profile`, so there's no "create profile" endpoint. `GET /profile` commits that empty row.
- **Why:** each user has exactly one profile (unique `user_id`), so a separate create step would only add an error case. Doing it in sign-up would have changed M3.1.
- **Where:** `backend/app/services/profiles.py`, `backend/app/api/profile.py`.

#### T-074 · `PATCH` for the profile, `PUT` for list entries
- **What:** `PATCH /profile` changes only the fields sent (null empties a text field; `preferred_language` can be left out but not set to null). `PUT` on an entry replaces every field; if `position` is left out, the entry keeps its place. New entries without a `position` go last (highest + 1). Lists are sorted by `position`, then creation time.
- **Why:** the profile is often changed one field at a time (e.g. only the language). Entries are edited as a whole form, so replacing everything avoids "is null a change or not?".
- **Where:** `backend/app/api/profile.py`, `backend/app/services/profiles.py`.

#### T-075 · `preferred_language` is edited through `/profile`
- **What:** it's stored on `users` (D-012, schema v1) but read and changed with the profile. `DELETE /profile` keeps it.
- **Why:** one screen for "about me" settings. It's an account setting, so clearing profile content shouldn't reset the interface language.
- **Where:** `backend/app/api/profile.py`, `backend/app/services/profiles.py`.

#### T-076 · Profile input rules
- **What:** text is trimmed. Names and titles: 1–200 characters. Descriptions: up to 5000 (required for projects). Blank optional text is stored as null. An end date can't be before the start date. A project `url` must start with `http://` or `https://` (max 2048). `position` is 0–10000. Unknown fields are refused (422). GitHub fields can't be edited here; they belong to M3.6 / M3.9.
- **Why:** the columns have no length limit, so the API sets one. The URL rule keeps `javascript:` links out of pages that will show them.
- **Where:** `backend/app/api/_fields.py`, the `*In` models in each endpoint file.

#### T-077 · Manual projects don't create their `sources` row yet
- **What:** saving a project only writes `manual_projects`. The `sources` row of kind `manual_project` (which turns the project into evidence) is left to the evidence slices. Deleting a project already deletes that source and its evidence, through the database cascade.
- **Why:** the slice is about storing the user's entries. Deciding when a project gets re-read as evidence (on every edit? on analysis?) belongs with the extraction code.
- **Where:** `backend/app/api/projects.py` (docstring).

### M2.8 · Language rules and term list

#### T-079 · Backend codes map to translation keys by name
- **What:** the frontend key for a backend code is a fixed group plus the code exactly as sent: `skills.status.<code>`, `skills.confidence.<code>`, `evidence.judgement.<code>`, `matches.category.<code>`, `opportunities.importance.<code>`, `errors.<code>`.
- **Why:** no mapping table to keep in sync; a new code only needs its three translations.
- **Where:** `docs/design/localization.md` §4.

#### T-080 · Statuses are translated as feminine adjectives
- **What:** `claimed` → déclarée / مُصرَّح بها, and so on, agreeing with "compétence" and «مهارة».
- **Why:** statuses are almost always shown next to a skill, so one form per language is enough and avoids gender-agreement keys.
- **Where:** `docs/design/localization.md` §5.
- **Watch out:** if a status is ever shown next to a masculine noun, it needs its own key rather than reusing these.

#### T-081 · Match category codes `strong` / `partial` / `weak` are proposed here
- **What:** the term list uses the categories from M7.3's tasks as codes, before any code defines them.
- **Why:** the words had to be agreed now; M7.3 should use these exact codes, or update §4 and §5 in its PR.
- **Where:** `docs/design/localization.md` §4, §5.

### M3.5 · CV upload and text extraction

#### T-082 · A CV's text is stored in a new `sources.text` column
- **What:** a new migration (`c5d1e7f20a94`) adds a nullable `text` column to `sources`, the plain text read from an uploaded CV, in its original language. Other kinds (repos, manual projects) leave it empty for now.
- **Why:** skill extraction (M4, M6) needs the text, and reading the file again each time is slow and repeats the extraction rules. A column is easy to query and is deleted with the source. The other options were a `.txt` file next to the upload (two places to keep in sync) or a key in `details` (JSON meant for small facts).
- **Contract note:** this extends schema v1 (contract owner: Rasen). It was decided under the autonomous-mode instruction; overturn it in review if you prefer another place.
- **Where:** `backend/app/db/models/sources.py`, `backend/migrations/versions/2026_11_25-c5d1e7f20a94_sources_text.py`, `docs/design/schema.md`.

#### T-083 · PDFs are read with pypdf, Word files with python-docx
- **What:** `pypdf` (default "plain" mode, page by page) and `python-docx` (paragraphs and tables in document order). Both are pure Python with no system packages.
- **Why:** the slice asked to check Arabic. On an Arabic PDF with shaped, right-to-left text (as Word's "Save as PDF" makes), pypdf gave every line back exactly. pdfminer.six (tried, not added) and pypdf's own `layout` mode gave every Arabic word back to front. PyMuPDF wasn't considered: its AGPL licence would apply to the whole app.
- **Watch out:** on a line that mixes Arabic with a Latin word (e.g. Arabic text, then `PostgreSQL`, then more Arabic), pypdf keeps every word intact but can move the Latin word to another place in the line. Quotes stay readable; the word order around English tool names may be off. This was tested on PDFs we generated (fpdf2 with HarfBuzz shaping), not on PDFs from Word itself, because there is no Word on the build machine. Try a real Word-made Arabic CV when one is available.
- **Where:** `backend/app/ingestion/cv_text.py`.

#### T-084 · The CV's language is guessed with two simple signals, no library
- **What:** `ar` if at least 30 % of the letters are Arabic. Otherwise count common short words (English: "the", "with"…; French: "le", "avec"…), leaving out the ones both languages use ("a", "on", "as"). The language with at least 2 hits, and 1.5 times more than the other, wins. Anything else gives `other`.
- **Why:** only three very different languages matter, and these two signals separate them reliably on CVs. A library (langdetect, lingua) would be a new dependency for a three-way choice. langdetect is also random unless seeded, and lingua is large. 30 % and not 50 %, because Arabic CVs are full of Latin tool names.
- **Watch out:** a Spanish or Italian CV may come out as `fr` (they share "de", "la", "en"). A CV that is only a list of tools gives `other`.
- **Where:** `backend/app/ingestion/language.py`.

#### T-085 · The file type is read from the bytes; limits on size, pages and unzipped size
- **What:** a PDF is recognised by `%PDF-` in its first 1024 bytes. A `.docx` is recognised as a zip file containing `word/document.xml`. The file name and the type the browser sends are ignored. Old `.doc` files are refused. Limits: `CV_MAX_BYTES` (default 5 MB), at most 20 PDF pages, and a `.docx` must not unzip to more than 50 MB.
- **Why:** names and browser types are easy to fake. The page and unzip limits stop one small upload from keeping the server busy (a "zip bomb" is a few KB that unzips to gigabytes).
- **Also:** `python-multipart` is added because FastAPI needs it to receive uploaded files.
- **Watch out:** FastAPI receives the whole upload before our size check runs, so a huge upload still travels to the server. In production, also cap the request size in the web server in front of it (M10).
- **Where:** `backend/app/ingestion/cv_text.py`, `backend/app/api/sources.py`, `backend/app/config.py`.

#### T-086 · Uploaded files live in `UPLOAD_DIR/<user id>/<source id>.<pdf|docx>`
- **What:** a new setting, `UPLOAD_DIR`, which defaults to `backend/storage/uploads` (already git-ignored and not served by anything). `sources.storage_path` holds the path relative to it, e.g. `<user id>/<source id>.pdf`. The name the browser sent is only kept as the `title` (any folders in it are cut off, at most 200 characters, `cv` if empty).
- **Why:** naming files by id means a name like `../../x.pdf` can't choose where the file goes. One folder per user makes deleting an account's files (M3.9) one folder removal. A relative path keeps working if the folder moves.
- **Watch out:** if the database commit fails after the file is written, the file stays without a row. That's rare and harmless; a clean-up job could remove such files later.
- **Where:** `backend/app/services/cv_uploads.py`, `backend/app/config.py`, `.env.example`.

#### T-087 · Each upload is a new source; earlier CVs are kept
- **What:** `POST /sources/cv` always adds a new `sources` row and never replaces an earlier one.
- **Why:** the plan (`GET /sources`, `DELETE /sources/{id}`, M4.10) defines "replace a CV" as "upload the new one, delete the old one". This slice doesn't add list or delete endpoints.
- **Where:** `backend/app/services/cv_uploads.py`.

#### T-088 · Extracted text is tidied but its words are never changed
- **What:** Unicode NFKC normalisation, which turns Arabic presentation-form letters, the one-character "fi" ligature and non-breaking spaces into plain characters. Control characters (including NUL, which PostgreSQL can't store) are removed. Each line is trimmed, runs of spaces are squeezed, and at most one empty line is kept in a row. A file with no text left gives `no_text_found`.
- **Why:** some PDF makers store Arabic as one-off letter shapes that don't match normal Arabic text in searches. NFKC fixes that without translating anything. NUL would make the database insert fail.
- **Where:** `backend/app/ingestion/cv_text.py` (`clean_text`).

#### T-089 · Upload errors: 413, 415 or 422 with a code
- **What:** `file_too_large` (413), `unsupported_file_type` (415), `file_unreadable`, `too_many_pages`, `no_text_found` (422). Broken files are caught whatever error pypdf or python-docx raises; only the error's type is logged, never the content.
- **Why:** each code tells the user what to do next (smaller file, PDF instead of `.doc`, a text PDF instead of a scan). The frontend upload slice translates them as `errors.<code>` (T-079).
- **Where:** `backend/app/api/sources.py`, `backend/app/ingestion/cv_text.py`.

#### T-090 · Test CVs are committed files, made by a script with fpdf2
- **What:** `backend/tests/fixtures/cv/` holds made-up CVs (en, fr, ar as PDF and `.docx`, plus a scanned-style picture-only PDF) and `make_cv_fixtures.py`, which makes them. `fpdf2` and `uharfbuzz` (for Arabic shaping) are dev-only dependencies, used only by that script.
- **Why:** an Arabic PDF needs a font with Arabic letters, which CI machines don't reliably have. Committing the files (about 190 KB) means tests never need fonts. The tests check the text against the exact lines in the script.
- **Where:** `backend/tests/fixtures/cv/`, `backend/pyproject.toml`.

### M3.6 · GitHub import

#### T-091 · One `sources` row per repo: README in `text`, the rest in `details`
- **What:** each imported repo is a `github_repo` source. `title` is `owner/repo`. `text` is the README, exactly as written. `language` is the README's language, or `other` without a README (code counts as `other`). `details` holds the rest as JSON:
  - owner, URL, description, fork and archived flags, default branch, last push, topics;
  - `languages` (bytes) and `language_shares` (%, one decimal);
  - `commits` (`by_user`, `total`);
  - `dependency_files` (path, content, truncated);
  - `file_list_truncated`.
- **Why:** it reuses the schema as it is (`details` was meant for "repo owner, fork flag, language shares"). The README goes in `text` because, like a CV's text, it's what skill extraction reads.
- **Where:** `backend/app/services/github_imports.py`, `backend/app/ingestion/github_repos.py` (`RepoInfo`).

#### T-092 · `httpx` for GitHub requests, injected so tests use a fake transport
- **What:** `httpx` moves from a dev to a runtime dependency (it was already in the lock file for tests). `GitHubClient` takes an `httpx.Client`. The endpoint gets the client from `get_github_client`, which tests replace with one on `httpx.MockTransport`, so no extra mocking library is needed.
- **Why:** the GitHub calls happen in the backend's ingestion layer, not in agents. Injecting the client makes "tests never use the live API" structural: the fake fails any request it has no saved answer for.
- **Where:** `backend/app/ingestion/github_client.py`, `backend/app/api/github.py`, `backend/tests/fixtures/github/fake_github.py`.

#### T-093 · GitHub answers are cached as files, for 1 hour, then re-checked with ETags
- **What:** each answer is saved as JSON in `GITHUB_CACHE_DIR` (default `backend/storage/github_cache`, git-ignored), named after a hash of the URL.
  - Within `GITHUB_CACHE_SECONDS` (default 3600) GitHub isn't asked at all.
  - After that, the request sends the saved ETag, and a 304 reuses the saved body.
  - "Nothing there" answers (404, 409, 204, 451) are cached too. Errors and rate-limit answers are not.
  - The token is never written to the cache.
- **Why:** repeated imports (a user retrying, the demo) then cost almost nothing against the rate limit. Files rather than a table: the cache holds only public data and can be deleted at any time, so it needs no migration.
- **Watch out:** the cache is per machine and is never cleaned up; old files just stay (they're small). Deleting the folder is always safe.
- **Where:** `backend/app/ingestion/github_client.py`, `backend/app/config.py`.

#### T-094 · Rate limit: fail fast with 429 and the reset time, never wait
- **What:** a 403 or 429 with `x-ratelimit-remaining: 0`, or with `Retry-After` (GitHub's "secondary" limit), raises `GitHubRateLimitError`. The API answers 429 `github_rate_limited` with `reset_at`. Nothing is retried automatically. An optional `GITHUB_TOKEN` (the server's own token, no scopes needed) raises the limit from 60 to 5000 requests an hour.
- **Why:** the limit can take up to an hour to refill; holding a request open that long helps nobody. Thanks to the cache (T-093), a retry after the reset resumes cheaply.
- **Where:** `backend/app/ingestion/github_client.py`, `backend/app/api/github.py`.

#### T-095 · At most 10 repos, owned ones only; forks only get their languages
- **What:** `GET /users/{name}/repos?type=owner&sort=pushed` keeps the `GITHUB_MAX_REPOS` most recently pushed repos (default 10).
  - Forks: only `/languages` is fetched (1 request).
  - Other repos: `/languages`, `/contributors`, `/readme`, `/git/trees` and up to 5 dependency files (4–9 requests).
- **Why:** without a token GitHub allows 60 requests an hour, and 10 repos fit in that. A fork never supports a skill (evidence model §3.2), so its README and files would cost requests for nothing. With a token, raise the limit to 20–30.
- **Watch out:** the import runs inside the request: 10 repos take a few seconds. Large accounts or a background job are a later concern.
- **Where:** `backend/app/ingestion/github_repos.py`, `backend/app/config.py`.

#### T-096 · "How much of the code they wrote" = commit counts from `/contributors`
- **What:** `commits.by_user` is the username's contributions (matched ignoring case) and `commits.total` is everyone's, from the first 100 contributors.
- **Why:** one request per repo gives both numbers. The alternatives (listing commits, or lines changed from `/stats/contributors`) cost many more requests, and `/stats` often answers 202 "computing, try later".
- **Watch out:** GitHub counts commits on the default branch only, and commits made under an email not linked to the account count as someone else's. It's a signal, not proof.
- **Where:** `backend/app/ingestion/github_repos.py`.

#### T-097 · Dependency files are found anywhere in the repo and kept exactly as written
- **What:** the full file list (`/git/trees/<branch>?recursive=1`) is searched for `requirements.txt`, `pyproject.toml`, `package.json` and `pom.xml`.
  - Folders of installed or generated code are skipped (node_modules, vendor, venv, .venv, env, site-packages, dist, build).
  - The shallowest files come first, at most 5 per repo, each cut at 100,000 characters (marked `truncated`).
  - File texts and the README are stored as they are; only NUL characters are removed.
- **Why:** many student repos keep `package.json` in a `frontend/` folder, so looking only at the root misses it. Keeping the text exact keeps line numbers right for evidence locations (`repo_dependency`: file + line).
- **Where:** `backend/app/ingestion/github_repos.py`.

#### T-098 · Importing again updates rows in place; the username is saved on the profile
- **What:** rows are matched by repo full name, ignoring case, so their ids (and later, evidence pointing at them) stay. Repos no longer listed, including all repos of a previously used username, are deleted, with their evidence (cascade). `profiles.github_username` is set on every import. GitHub is read completely before any row changes, so a failure part-way saves nothing.
- **Why:** a re-import shouldn't break links to evidence for repos that still exist.
- **Where:** `backend/app/services/github_imports.py`.

#### T-099 · Import errors and username rules
- **What:**
  - 422 for a name that breaks GitHub's rules (letters, digits and single hyphens between them, at most 39 characters); checked before any request.
  - 404 `github_user_not_found`.
  - 429 `github_rate_limited` (+ `reset_at`).
  - 502 `github_unavailable`: network failure, or any other GitHub error status, including 401 for a bad token.
- **Why:** each code tells the user what to do next (check the name, try later). The frontend translates them as `errors.<code>` (T-079).
- **Where:** `backend/app/api/github.py`.

#### T-100 · Saved GitHub answers: one JSON file for a made-up account
- **What:** `backend/tests/fixtures/github/test_student.json` holds every answer for `test-student`, keyed by path plus sorted query. Its 4 repos are:
  - `shop-api`: Python, with a README, `requirements.txt` and an `admin/package.json`;
  - `projet-bibliotheque`: Java, with a French README and a `pom.xml`;
  - `awesome-dashboard`: a fork;
  - `empty-repo`: an empty repo, answered with 204 / 404 / 409.

  `FakeGitHub` serves them, answers 304 to a matching ETag, and fails on anything unknown.
- **Why:** the answers are hand-made, but in GitHub's real format (checked against `api.github.com` with the public `octocat` account on 2026-11-26), trimmed to the fields we use. One file is easier to read and edit than dozens.
- **Where:** `backend/tests/fixtures/github/`.

### M3.9 · Account and data deletion

#### T-101 · Deleting an account asks for the password again
- **What:** `POST /account/delete {password}` answers 204 and removes the login cookie. A wrong password gets 403 `wrong_password` and nothing is deleted. It's a POST, not a DELETE, because a body on DELETE is dropped by some tools and proxies.
- **Why:** deletion can't be undone. Re-entering the password stops a login left open on a shared computer, or a stray click, from deleting an account. 403 and not 401, so the frontend doesn't treat it as "logged out".
- **Where:** `backend/app/api/account.py`, `backend/app/services/accounts.py`.

#### T-102 · Files are deleted before rows
- **What:** the order is:
  1. remove `UPLOAD_DIR/<user id>/` (all their CVs);
  2. remove the cached GitHub answers for their saved GitHub username;
  3. delete the `users` row. The database cascade removes every other personal row (schema.md).

  An old login cookie stops working at once, because each request looks the user up (M3.1).
- **Why:** if removing files fails, the error stops everything before any row is gone, so the user can try again. The other order could leave a CV on disk with no account left to delete it from.
- **Watch out:** the GitHub cache is shared. If two users imported the same username, deleting one also empties the cache for the other, which only costs a few requests on their next import.
- **Where:** `backend/app/services/accounts.py`, `backend/app/ingestion/github_client.py` (`forget_cached_user`).

#### T-103 · GitHub consent has its own endpoints; the import refuses without it
- **What:** `GET`/`PUT`/`DELETE /profile/github-consent`. `PUT` stores the time in `profiles.github_consent_at`; agreeing again keeps the first time. `POST /sources/github` answers 403 `github_consent_required` before sending any request to GitHub.
- **Why:** consent is a separate, recorded act that can be taken back (SPEC: explicit, revocable consent). Separate endpoints make "taking it back" an obvious action of its own, rather than a flag sent with each import.
- **Watch out:** only the time is stored, not which wording the user agreed to. If the consent text changes in a way that matters, add a version then.
- **Where:** `backend/app/api/github_consent.py`, `backend/app/services/github_imports.py`.

#### T-104 · Withdrawing consent deletes everything imported from GitHub
- **What:** `DELETE /profile/github-consent` deletes the user's `github_repo` sources (and their evidence, by cascade), clears the saved username and the consent time, and removes the cached answers for that username. CVs and everything else stay.
- **Why:** consent that's taken back should leave nothing behind that it allowed in.
- **Where:** `backend/app/services/github_imports.py` (`withdraw_consent`).

### M3.10 · Change password

#### T-105 · A wrong current password gets 403 `wrong_password`
- **What:** `POST /auth/password` answers 403 `wrong_password` when the current password is wrong, the same as `/account/delete` (T-101). The login cookie is untouched, so the user stays logged in. The new password follows the sign-up rules (T-069, 8–128 characters); it may equal the old one.
- **Why:** the slice first asked for 401 `invalid_credentials`, but a 401 elsewhere means "you're not logged in", and a frontend that sends users to the login page on any 401 would log them out for a typo. Changed to 403 on Rasen's request (2026-11-26).
- **Where:** `backend/app/api/auth.py`, `backend/app/services/accounts.py` (`change_password`).

#### T-106 · Other open logins stay valid after a password change
- **What:** changing the password only replaces the hash. Logins already open on other devices keep working until they expire (24 h by default).
- **Why:** tokens aren't stored on the server (D-015), so there is nothing to revoke. Ending other logins would need a per-user "password changed at" time checked against the token's `iat`: a schema change, left for later if needed.
- **Where:** `backend/app/services/accounts.py` (docstring of `change_password`).

#### T-107 · Every backend error code has text in all three languages, checked by a test
- **What:** `errors.<code>` keys in `frontend/src/locales/{en,fr,ar}.json` for all 18 codes the backend sends today (auth, CV upload, GitHub). `backend/tests/test_error_translations.py` finds the codes in `app/` by their usual spellings (`code = "..."`, `{"code": "..."}`, `_unauthorized(...)`, `_error(...)`) and fails if en.json lacks one; `npm run check` already makes fr and ar match en.
- **Why:** a new code without words would show a raw `snake_case` code on screen. The texts don't include limits that are settings (the 5 MB CV size), so they can't go out of date.
- **Where:** the locale files and the test above. Added after M3.10, on Rasen's request.

### M3.2 · Sign-up and login screens

#### T-108 · React Router for pages (`react-router` 7, declarative mode)
- **What:** `<BrowserRouter>` in `main.tsx`, `<Routes>` in `App.tsx`. Routes: `/` (home, login needed), `/login`, `/signup`, `/health`; anything else goes to `/`.
- **Why:** the alternative was a small router of our own on the History API (no dependency). React Router is the usual choice for React, so chatbots and teammates know it, and the later screens (profile, skills, matches, with ids in the URL) need nested routes and parameters we'd otherwise rebuild. Its declarative mode is just components, with no build plugin or file-based routing. Decided under autonomous mode (D-017); easy to change while there are few pages.
- **Where:** `frontend/package.json`, `frontend/src/main.tsx`, `frontend/src/App.tsx`.

#### T-125 · The sign-up privacy notice wording is approved
- **What:** the three points under "Your data" on the sign-up page (`privacy.*` in the locale files): what is stored, what it is used for (including analysis by an AI model), and that deleting the account removes it all.
- **Why:** M3.2 asks Rasen to approve the wording. Approved on 2026-11-26, and it can be edited later. Revisit it when D-005 (which LLM) is decided: a hosted service that keeps or trains on data must be named.
- **Where:** `frontend/src/locales/{en,fr,ar}.json`, `frontend/src/pages/SignUpPage.tsx`.

#### T-109 · Who is logged in: one React context filled by `GET /auth/me`
- **What:** `AuthProvider` asks `/auth/me` on start and holds `loading` / `anonymous` / `logged-in` (with the user). `useAuth()` gives that state plus `logIn`, `signUp` and `logOut`. If the backend is down at start, the state becomes `anonymous` and the login form says so when used.
- **Why:** the login cookie is HttpOnly (D-015), so the frontend can only learn who is logged in by asking. One provider means one request per page load, and no login state in localStorage.
- **Where:** `frontend/src/auth/context.ts`, `frontend/src/auth/AuthProvider.tsx`.

#### T-110 · Page guards, and the page to return to travels in router state
- **What:** `<RequireLogin>` sends anonymous visitors to `/login` with `{from: <path>}` in the router state. `<AnonymousOnly>` sends a logged-in user from `/login` or `/signup` to that path, or `/`. That redirect is also what happens right after logging in, so the forms never navigate themselves. `safeReturnPath` accepts only paths starting with one `/`.
- **Why:** state can't be set by a link from another site, unlike a `?next=` URL parameter, and the path check adds a second guard against redirecting to another site. One place doing the redirect avoids two navigations racing after login.
- **Where:** `frontend/src/auth/guards.tsx`, `frontend/src/auth/returnPath.ts`.

#### T-111 · Forms check input themselves (`noValidate`), with the backend's rules
- **What:** the browser's built-in checks are off. Sign-up checks the email shape and the 8–128 password length before sending (T-069); login only checks that both fields are filled. Email and password inputs are `dir="ltr"`, also in Arabic.
- **Why:** the browser's own messages are in the browser's language, not the interface's. Emails and passwords are Latin text, which is easier to type and check left to right.
- **Where:** `frontend/src/components/AuthForm.tsx`.

#### T-112 · `request()` and `errorKey()`: one way to call the backend and show its errors
- **What:** `request(method, path, body)` in `api/client.ts` sends JSON with the cookie. It throws `ApiError(status, code)` for an error answer: the backend's code, `invalid_input` for FastAPI's 422 without a code, otherwise `unknown`. It throws `BackendUnreachableError` when there is no answer, or a 5xx without JSON (the Vite proxy's 502 when the backend is off). `errorKey(error)` in `api/errors.ts` gives `errors.<code>`, or `errors.unknown` for a code the locale files don't have.
- **Why:** every later screen calls the backend the same way and shows errors with one line. An unexpected code never shows up raw on screen.
- **Where:** `frontend/src/api/client.ts`, `frontend/src/api/errors.ts`, `frontend/src/api/auth.ts`.

#### T-113 · The interface language follows the account (D-012)
- **What:**
  - Sign-up sends the interface's current language as `preferred_language`.
  - Logging in (or opening the app while logged in) switches the interface to the account's language.
  - While logged in, every language change is saved with `PATCH /profile`. A failed save is logged to the console and doesn't interrupt; the choice is still remembered in the browser.
- **Why:** D-012 says the choice is saved to the account. The provider listens to i18next's `languageChanged`, so the language switcher didn't need to change.
- **Where:** `frontend/src/auth/AuthProvider.tsx`.

#### T-114 · Page tests run the whole app against a pretend backend
- **What:** `src/test/fakeBackend.ts` replaces `fetch` and answers the auth endpoints like the real backend (codes, cookie-like login state, in memory). `App.test.tsx` renders the real app in a `MemoryRouter` and drives the forms with `fireEvent`.
- **Why:** it tests the real client, provider, guards and pages together, without mocking each module. No new test library was needed (`@testing-library/user-event` would be nicer, but isn't needed yet).
- **Where:** `frontend/src/test/fakeBackend.ts`, `frontend/src/App.test.tsx`.

#### T-115 · The status page moved to `/health`
- **What:** the home page `/` is now for logged-in users. The backend and database status page is at `/health`, open to anyone.
- **Why:** the status page is still useful when setting up, and must work without logging in.
- **Where:** `frontend/src/App.tsx`, `docs/USER_GUIDE.md` §4.

### M3.4 · Profile screens

#### T-116 · One list component for the three kinds, driven by a field list
- **What:** `src/profile/entryKinds.ts` lists each kind's fields (name, type short/long/date/url, required) as the backend defines them. `EntrySection` (list, add, edit, delete) and `EntryForm` (the form) are built from that list, so education, experience and projects share one pattern. Field names are typed against `profile.fields.*` in en.json, so a field without a label fails `npm run check`.
- **Why:** three copies of the same list and form would drift apart. The alternative, one component per kind, is easier to paste alone but triples every fix.
- **Where:** `frontend/src/profile/entryKinds.ts`, `frontend/src/components/EntrySection.tsx`, `frontend/src/components/EntryForm.tsx`.

#### T-117 · Mistakes show under their field, from our check first, then from the 422
- **What:** `checkEntry` runs the backend's rules before sending: required, max length, `http(s)://` link, end date not before start. If the backend still refuses, `ApiError.fields` holds FastAPI's refused fields (`loc: ["body", <field>]` → error type). `problemsFromApi` maps those to the same `profile.problems.*` keys. The date check runs on the whole body (`loc: ["body"]`, `value_error`), so it shows above the buttons.
- **Why:** the slice asks for the API's validation errors shown in the form. Checking first saves a round trip, and the 422 mapping covers anything that drifts.
- **Where:** `frontend/src/profile/fieldProblems.ts`, `frontend/src/api/client.ts` (`invalidFields`).

#### T-118 · Deleting an entry asks to confirm on the spot, not in a browser dialog
- **What:** **Delete** turns into "Delete this entry?" with **Yes, delete** and **Cancel** in the same row.
- **Why:** `window.confirm` can't be styled, and its buttons are in the browser's language, not the interface's.
- **Where:** `frontend/src/components/EntrySection.tsx`.

#### T-119 · The page loads the whole profile once and holds it
- **What:** `GET /profile` (details and all three lists) when the page opens. Each section saves its own change (POST/PUT/DELETE) and hands the new list back to the page. No reload after each change.
- **Why:** one request to open the page, and the screen shows exactly what the backend answered for each save.
- **Where:** `frontend/src/pages/ProfilePage.tsx`.

#### T-120 · Dates use the browser's date input; the list shows month and year
- **What:** `<input type="date">` (sends `yyyy-mm-dd`, the backend's format). The list shows "September 2024" via `formatDate`, read as UTC so no time zone shifts the day. No end date shows "present".
- **Why:** no date-picker library needed. The picker itself follows the browser's language, not the interface's: a known limit, fine for the MVP.
- **Where:** `frontend/src/components/EntryForm.tsx`, `frontend/src/components/EntrySection.tsx`.

### M3.7 · Upload and GitHub screens

#### T-121 · New endpoints `GET /sources` (a summary) and `DELETE /sources/{id}`
- **What:** the list gives id, kind, title, language, `url` (a repo's GitHub page) and `created_at`, newest first, by title within the same moment. It has no `text` or `details`: a repo's details hold dependency files of up to 100,000 characters each. Deleting removes a CV's file first, then the row (as T-102), and the source's evidence goes with it by cascade. Someone else's id answers 404 `not_found`.
- **Why:** the slice's "list of sources" had no endpoint. Every CV upload is kept (T-087), so a wrong upload needs a way out. A deleted repo comes back on the next import; withdrawing consent removes them all.
- **Where:** `backend/app/api/sources.py`, `backend/app/services/sources.py`, `backend/tests/api/test_source_list.py`.

#### T-122 · The CV upload uses XMLHttpRequest, for its progress bar
- **What:** `uploadCv(file, onProgress)` sends the file with XMLHttpRequest and reports the share sent. At 100% the screen says "Reading the CV…" while the backend extracts the text. Errors are parsed like every other call (`apiError()`, shared with `request()`).
- **Why:** the slice asks for upload progress, and fetch can't report upload progress in browsers yet. No upload library needed.
- **Where:** `frontend/src/api/sources.ts`, `frontend/src/components/CvUpload.tsx`.

#### T-123 · The GitHub consent text shows before any GitHub field
- **What:** without consent, the GitHub section shows only the consent text and **Allow GitHub import**. The text says what is read, that it's public data only and no password is asked, and that withdrawing deletes everything imported. The username field appears after consent. **Withdraw consent** asks to confirm on the spot, because it deletes data. The username is checked against GitHub's rule before asking the backend.
- **Why:** M3.9 made consent required, and the slice asks for "a clear consent message". The wording is Rasen's to approve, like the privacy notice.
- **Where:** `frontend/src/components/GitHubConnect.tsx`, `sources.github.consent.*` in the locale files.
- **Approved:** Rasen approved the consent wording on 2026-11-26 (it can be edited later).

### M3.8 · Dashboard layout

#### T-124 · The dashboard is a grid of four cards; recent activity uses real data
- **What:** `/` shows Skills, Opportunities and Gaps as placeholder cards, plus Recent activity: the five latest sources from `GET /sources`, or a link to `/sources` when there are none. The grid (`auto-fit`, at least 18rem per card) becomes one column on a narrow screen and mirrors in Arabic by itself. The header links (Home, Profile, Sources) are the navigation.
- **Why:** the slice asks for placeholders. Recent activity could already be real at no cost, and it gives a new user a first step. Each later milestone (M4 skills, M5 matching, M7 gaps) replaces one card's text with a component.
- **Where:** `frontend/src/pages/HomePage.tsx`, `frontend/src/index.css`.

### M4.1 · Skill list data

#### T-126 · The first skill list is built for tech internships, before the curated postings exist
- **What:** 246 skills (245 since T-138) for the internships SkillGraph targets (software, web, mobile, data, AI, cloud, DevOps, security, networks, embedded), plus a few soft skills and spoken languages that postings often ask for. 356 aliases (English and French spellings, short forms) and 258 parent links. This matches D-032 (first version: software engineering only); other fields come in M17.
- **Why:** M4.1 should cover every skill in the curated postings (M1.7) and test profiles (M1.5), but neither exists yet. Waiting would block all of M4. When M1.7 lands, check each posting's skills against the list and add what's missing. Until then the "Done when" coverage item is open, and so is issue #32.
- **Where:** `backend/app/skills/data/{skills,aliases,relations}.csv`.

#### T-127 · A fixed list of 13 categories, checked by a test rather than the database
- **What:** `area, language, framework, library, database, cloud, devops, tool, data, ai, practice, soft, spoken_language`. The README says what each is for. The test refuses any other value.
- **Why:** the screen (M4.6) can group skills by category, and a short fixed list keeps the data consistent. `skills.category` stays free text in the schema (D-019), so no migration was needed. If the UI shows categories, they'll need locale keys then.
- **Where:** `backend/app/skills/data/README.md`, `CATEGORIES` in `backend/tests/skills/test_skill_data.py`.

#### T-128 · Alias rules: lowercase with accents, never repeat the skill's own id or name, never ambiguous
- **What:** aliases are stored lowercase (the `skill_aliases` CHECK) with French accents kept (`développement web`). An alias that equals the skill's id or English name is refused, and so is one that equals a *different* skill's id or name. Words that could mean two skills are left out.
- **Why:** M4.2's normalizer matches ids and English names directly and strips accents and punctuation itself, so repeating them only adds rows that can hide typos. One alias → one skill is required by the table's primary key.
- **Where:** `backend/app/skills/data/aliases.csv`, `backend/tests/skills/test_skill_data.py`.

#### T-129 · `.NET`'s id is `dotnet`
- **What:** the skill is `dotnet` with the name `.NET`. Spellings like `.net core` and `dot net` are aliases.
- **Why:** the `skills.id` CHECK requires the first character to be a letter or digit, so `.net` can't be an id. `.net` is still found through the English name.
- **Where:** `backend/app/skills/data/skills.csv`.

#### T-130 · The CSV checks are a plain test with the standard `csv` module
- **What:** `tests/skills/test_skill_data.py` reads the files directly and checks columns, the 150–300 count, id format (same pattern as the database CHECK), duplicates, references and loops in the parent links. It doesn't touch the database.
- **Why:** M4.1 is data only. The loader comes in M4.2. Fast checks with no dependencies catch mistakes as soon as someone edits a CSV by hand.
- **Where:** `backend/tests/skills/test_skill_data.py`.

### M4.9 · Skill names in French and Arabic

#### T-131 · Every skill has all three names filled in, even when they're the same
- **What:** `skills.csv` now has `id,name_en,name_fr,name_ar,category`, and no name is empty. Technical names are copied as they are (`Python` in all three). General skills are translated (`Databases` / `Bases de données` / `قواعد البيانات`). A technical term inside an Arabic name stays in Latin letters (`تطوير Android`). A test checks that each Arabic name either contains Arabic letters or is exactly the English name, which catches an English name left untranslated by mistake.
- **Why:** the screens can show `name_<language>` without a fallback, and an empty cell can't be confused with "not translated yet". The Latin-letters rule comes from `docs/design/localization.md` section 3.
- **Where:** `backend/app/skills/data/skills.csv`, `backend/tests/skills/test_skill_data.py`.

#### T-132 · No Arabic aliases
- **What:** M4.9 asks for Arabic aliases. None were added. Arabic names are for display only.
- **Why:** D-030 (decided after M4.9 was written) says CVs and postings are read in English and French only, and no slice spends effort on Arabic skill extraction. Arabic aliases would be rows nothing uses. M4.9's text in `docs/MILESTONES.md` still mentions them; it could be updated to match D-030.
- **Where:** `backend/app/skills/data/aliases.csv`, README.

#### T-133 · French aliases are written once, with their accents; no unaccented copies
- **What:** 51 new French aliases (`dev web`, `bdd`, `sgbd`, `infonuagique`, `pack office`, `méthodologie agile`…). There's no unaccented copy (`developpement web`). 59 earlier aliases were removed because they're now a skill's French name (for example `bases de données`), which is matched anyway.
- **Why:** M4.2's normalizer has to remove accents anyway (its own task list says so), because CVs mix both spellings. Copies would double the file and could drift apart. This differs from M4.9's task text ("with and without accents"): the result is the same, but the work is done in one place. If M4.2's normalizer doesn't strip accents, add the copies then.
- **Where:** `backend/app/skills/data/aliases.csv`, README.

#### T-134 · The French and Arabic names are a first draft by Claude Code
- **What:** the names follow the term list and the style rules (French without inclusive spelling; Modern Standard Arabic without diacritics). They haven't been read by a fluent speaker yet.
- **Why:** the same review the term list in `docs/design/localization.md` section 5 already asks for. Fixing a name is a one-cell edit and doesn't change any id.
- **Where:** `backend/app/skills/data/skills.csv`.

### M4.8 · Learning resources list

#### T-135 · Every skill gets at least 2 free resources, not only the skills postings ask for
- **What:** `resources.csv` has 584 rows (526 different links) covering all 245 skills, with at least 2 free resources each. 55 are in French. None are in Arabic, because Arabic is for the interface only (D-030). A test checks the columns, the allowed values, `https://`, that every `skill_id` exists, no duplicate rows, and the 2-per-skill minimum.
- **Why:** the slice asks for 2 per skill "required by a curated posting", but the postings (M1.7) don't exist yet. Covering every skill satisfies that whatever the postings ask for. The test then makes sure a new skill can't be added without its resources.
- **Where:** `backend/app/skills/data/resources.csv`, `backend/tests/skills/test_resource_data.py`.

#### T-136 · Links were checked by a script, not opened by hand; 19 couldn't be confirmed that way
- **What:** every link was fetched with curl (browser user agent, redirects followed). 507 of 526 answered 200. Links that 404'd or redirected to the wrong page were replaced. The 19 that weren't confirmed are official pages behind bot protection or slow servers: MySQL manual (2), MathWorks, Adobe help (4), Tableau training, Salesforce docs, Oracle Dev Gym and Live SQL, Splunk training, TV5MONDE, RFI, British Council, TryHackMe (rate limit), OpenCV docs (2, redirect loop for curl), GNU Bash manual (timeout; it opened in an earlier run). Each skill that has one of them also has at least 2 confirmed links.
- **Why:** the slice says "open every link". 527 links by hand is hours of work, and a script catches dead links the same way. The 19 still need a person to open them in a browser.
- **Where:** list in the M4.8 issue comment.
- **Watch out:** links rot. A committed link checker (for example a monthly CI job) would be a separate slice.

#### T-137 · Redirecting links keep their stable address; "free to audit" counts as free
- **What:** a link that redirects to a versioned page (`/en/stable/` → `/en/6.1/`, `?view=…`) keeps the stable address. edX and Coursera courses you can take for free without the certificate are marked `free=yes`. `language` is the language the resource is written in.
- **Why:** the stable address keeps working when a new version comes out. Students care whether they can learn without paying, not whether the certificate is free.
- **Where:** `backend/app/skills/data/resources.csv`, README.

#### T-138 · Arabic is not a skill on the list
- **What:** the `arabic` spoken-language skill (added in M4.1) was removed from `skills.csv`, along with its learning resources. English, French, Spanish and German stay.
- **Why:** Rasen, 2026-11-26: Arabic is for the interface only, not a professional language SkillGraph assesses or recommends learning (extends D-030). Keeping the skill would have forced Arabic-learning resources into the recommendation list.
- **Where:** `backend/app/skills/data/skills.csv`, `resources.csv`.

### M4.2 · Skill list loader and CV skill finder

#### T-139 · One lookup key for every spelling: no accents, lowercase, punctuation as spaces
- **What:** `normalize` does Unicode NFKD, drops the combining marks, casefolds, and keeps only runs of letters, digits, `+` and `#` as words, joined by one space. `Node.js` → `node js`, `Développement-Web` → `developpement web`, `C++` stays `c++`, `.NET` → `net`.
- **Why:** one rule for both the index and the CV text, so they always agree. Dropping marks also removes Arabic diacritics and the hamza on alef for free. No Arabic-specific rules were added (ة/ه, ى/ي), because Arabic text isn't read (D-030).
- **Where:** `backend/app/skills/normalize.py`.
- **Watch out:** Python's word class in regular expressions doesn't match combining marks, so the word pattern lists their ranges. They're built from numbers, because some editing tools turn written-out Unicode escapes into invisible characters.

#### T-140 · The index holds the id, all three names and the aliases; two skills on one key are refused
- **What:** `SkillIndex` maps each key to one skill id. A key that would point at two skills raises `SkillIndexCollisionError` when the index is built. The app builds it from the database (`load_index`). Tests and the check script build it straight from the CSVs (`SkillIndex.from_csv`).
- **Why:** a collision means a guess, and guesses are what the evidence model forbids. Building from the CSV means most finder tests need no database.
- **Where:** `backend/app/skills/index.py`.

#### T-141 · Words that are also ordinary words only count in a skills list or with a capital letter
- **What:** `AMBIGUOUS` lists about 70 keys like `go`, `c`, `r`, `rest`, `vue`, `tableau`, `excel`, `spring`, `react`, `networking` and `supervision`. Outside a skills list they're only taken when written with a capital letter ("REST", "Go", "C"). A test checks each one is a real key.
- **Why:** "rest on weekends", « tableau de bord », « sous la supervision de » and "j'ai" (→ `ai`) would otherwise become skills.
- **Where:** `backend/app/skills/index.py`, `backend/app/skills/cv_finder.py`.
- **Watch out:** a sentence starting with « C'est » still gives `c`. The list will need tuning once real labeled CVs exist (M4.7).

#### T-142 · CV sections come from a fixed list of English and French headings
- **What:** a line is a heading when, without its bullet, it matches one of about 70 headings (alone, or followed by `:` and text). Headings map to skills / summary / experience / project / education / certificate, or are skipped (hobbies, references). Text before any heading counts as summary. Location is `{"section": <heading as written>, "line": <n>}`. There's no page, because the extracted text has no page breaks.
- **Why:** the section decides the evidence type, which the status rules depend on. A fixed list is easy to test and to extend by hand.
- **Where:** `HEADINGS` in `backend/app/skills/cv_finder.py`.

#### T-143 · One evidence record per sentence, quoted exactly, cut around the first skill when too long
- **What:** each line is split after `.` `!` `?` `;`. A sentence naming several skills is one record listing them all (no repeats). A sentence over 300 characters is cut at word boundaries around its first skill and marked `…`. The quote's language is detected. A bare list of tools ("Python, SQL") gets the CV's language instead of `other`.
- **Why:** the evidence model says one record can support several skills and caps quotes at about 300 characters. Labeling "Python, SQL" as `other` would hide that it came from a French CV.
- **Where:** `backend/app/skills/cv_finder.py`.

#### T-144 · The finder saves evidence records only; judging and linking come later
- **What:** `save_cv_evidence` deletes the CV's earlier evidence records and saves new ones, and returns each record with its skill ids. It doesn't mark `supports` / `weak` (M4.4) or create skill rows and links (M4.5).
- **Why:** an evidence link needs a skill row, and a skill row needs a status, which M4.4 computes. Replacing a source's records on every run keeps the result equal to what the current rules find.
- **Where:** `backend/app/services/cv_evidence.py`.

#### T-145 · The skill list is loaded with a command, and refuses to delete skills still in use
- **What:** `uv run python -m app.skills.taxonomy` makes the database match the CSVs: it updates skills in place, replaces aliases and parent links, and deletes skills that left the CSV. If a removed skill is still on a profile or a posting, it raises `SkillInUseError` before changing anything. This error and `NotACvError` have no API error code, because neither can reach a user.
- **Why:** running it again must be safe, and a typo in the CSV must not wipe profiles (T-055).
- **Where:** `backend/app/skills/taxonomy.py`. Command added to CLAUDE.md.

#### T-146 · The check script uses the made-up CVs, with expected skills written in the test
- **What:** `uv run python -m app.skills.check_cv_finder <cv file> <id,id,...>` prints `expected / found / missed / wrong`. Its tests use `cv_en.pdf` and `cv_fr.docx` with hand-written expected lists. Both are found with no misses and nothing wrong.
- **Why:** the slice wants found / wrong counts on labeled skills, but the labeled profiles (M1.5, M1.6) don't exist yet. The full evaluation over them is M4.7.
- **Where:** `backend/app/skills/check_cv_finder.py`, `backend/tests/skills/test_check_cv_finder.py`.

### M4.3 · Skills from GitHub repos

#### T-147 · "More weight to larger, recent repos the user wrote" is a stored weight, not a rule change
- **What:** each repo gets `weight = authorship × recency × size`, rounded to 2 decimals and stored in every repo evidence location:
  - authorship: the user's share of the commits; 0 for a fork or a repo with no commits.
  - recency: 1 if pushed in the last year, 0.5 in the last three, otherwise 0.25.
  - size: the code's bytes divided by 50 000, at most 1.
- **Why:** the slice asks for more weight on larger, recent, self-written repos, but status and confidence follow D-006's fixed rules, and those have no weight. Storing it lets the screens and agents order and explain repo evidence without changing the contract. Whether weight should change confidence (a new D-entry on the evidence model) was **tabled by Rasen on 2026-11-27**, to come back to later.
- **Where:** `repo_weight` in `backend/app/skills/repo_finder.py`.

#### T-148 · GitHub topics are stored as `repo_readme` evidence
- **What:** a repo's topics that are skills become one `repo_readme` record: quote `topics: fastapi, postgresql`, location `{"repo": …, "field": "topics"}`.
- **Why:** the evidence types are a decided contract (D-006) with no type for topics. Topics, like the README, are the repo describing itself, so they are context only and never raise a status. Adding a `repo_topic` type would need the owner's approval.
- **Where:** `backend/app/skills/repo_finder.py`.

#### T-149 · No `repo_code` evidence yet: the import doesn't download code
- **What:** the finder produces `repo_language`, `repo_dependency` and `repo_readme`, never `repo_code`.
- **Why:** M3.6 fetches only READMEs and dependency files, to stay within GitHub's 60 requests an hour without a token (T-095). Without code, a repo can still make a skill demonstrated through its language share (≥ 10 %, owned, not a fork).
- **Where:** `backend/app/skills/repo_finder.py`.
- **Watch out:** frameworks (FastAPI, React…) can't reach demonstrated from a repo alone, only through a CV project or experience. Reading a few code files is the natural later slice (or the Evidence Agent's job, M6).

#### T-150 · Language findings keep every share; the 10 % rule is applied later
- **What:** each GitHub language that is a skill gives a `repo_language` record, even at 1 %. The location keeps `share`, `bytes`, `owned` (owner = the profile's GitHub username) and `is_fork`. Forks still give language records, which are judged weak later.
- **Why:** the finder finds and the rules judge (T-144). Keeping the facts in the location lets the validator check guardrail 4 of the evidence model.
- **Where:** `backend/app/skills/repo_finder.py`.

#### T-151 · Package and language names that differ from the skill go in two small CSV files
- **What:** `packages.csv` (about 70 rows, for example `psycopg2,postgresql`, `react-dom,react`, `spring-boot-starter*,spring-boot`) and `github_languages.csv` (`Dockerfile,docker`, `HCL,terraform`…). They're checked first, then the skill index. A trailing `*` matches any ending, and the longest match wins. Scoped npm names (`@types/node`) only match through the file. A file gives one record per skill, so `react` and `react-dom` give one.
- **Why:** these are data, not logic, so teammates can extend them by hand like the other CSVs. Without the scope rule, `@types/node` would read as Node.js.
- **Where:** `backend/app/skills/data/`, `backend/app/skills/repo_finder.py`.

#### T-152 · README matching skips headings, code blocks and link addresses
- **What:** README lines starting with `#` and lines inside fenced code blocks are skipped. Link addresses are blanked out before matching, but the quote keeps them. Everything else is matched like CV prose (`app/skills/matching.py`, shared with the CV finder).
- **Why:** `# shop-api` would read as "API design", `pip install django` in a code block isn't a statement, and badge URLs are full of tool names.
- **Where:** `backend/app/skills/repo_finder.py`, `backend/app/skills/matching.py`.

### M4.4 · Status and confidence rules

#### T-153 · Two modules: shared status rules, and System A's link judgement
- **What:** `app/skills/status_rules.py` turns judged links into status, confidence and reason (evidence model §4–5), and holds the §7 validator. All three systems use it. `app/skills/judge.py` is System A's own judgement of one link (§3.2). The agents will replace only the judging (M6.3).
- **Why:** the evidence model says the systems differ only in how they judge links. Keeping the computation in one shared module makes that true in code too.
- **Where:** `backend/app/skills/status_rules.py`, `backend/app/skills/judge.py`.

#### T-154 · A skill's reason is the reason code of the link that set its status
- **What:** `SkillResult.reason` is `{code, evidence_id}`: the first assessment, work or claim link that decided the status. For an unverified skill it's the first link's code, and `no_evidence` for an empty list (a new reason code, for job requirements). No sentences.
- **Why:** the slice wants "a code plus data" that the frontend turns into text, and the evidence id lets the screen show the quote behind it.
- **Where:** `compute` in `backend/app/skills/status_rules.py`.

#### T-155 · Concrete work vs vague mention is decided by English and French phrase lists
- **What:** in a CV experience or project (and a manual project), a vague phrase ("familiar with", « notions de », a sentence starting "Technologies:") makes the link weak. Otherwise an action verb ("built", "wrote", « développé », « mise en place ») makes it support. Otherwise it's weak. In a skills list or summary, a wants-to-learn phrase ("interested in", "looking for", « à la recherche d' ») makes it weak. Phrases are matched as whole words after `normalize`. Bare "learning" isn't a phrase, so "Machine learning" stays a claim.
- **Why:** these are the rules of §3.2 in a form that can be tested and extended by hand. Vague phrases are checked first, so "Built a website. Tech stack: React" stays weak.
- **Where:** `WANTS_TO_LEARN`, `VAGUE`, `STARTS_VAGUE`, `ACTION_VERBS` in `backend/app/skills/judge.py`.
- **Watch out:** "looking for a backend internship" counts as wanting to learn, so a summary like that gives "backend development" as unverified, not claimed. Worth checking against the labels in M4.7.

#### T-156 · The validator covers guardrails 1 and 3–6; guardrail 2 is for the agent runtime
- **What:** `validate(links, status, confidence)` raises `RuleViolationError` with a code: `no_links`, `supports_on_context_type`, `repo_language_conditions`, `assessed_not_allowed` (unless `allow_assessed=True`, for M11), `status_mismatch`, `confidence_mismatch`. Guardrail 2 (only cite evidence given to this agent) needs the agent's context, so the runtime checks it (M5).
- **Why:** the agents' results (M6.3) must be refused when they break the evidence model, and the checks belong next to the rules they protect.
- **Where:** `backend/app/skills/status_rules.py`.

#### T-157 · Hypothesis for the property-based tests (new dev dependency)
- **What:** `hypothesis` is added to the dev dependency group. The property tests generate random lists of links and check that:
  - more supporting evidence never lowers confidence or status;
  - weak evidence never changes confidence;
  - only an assessment gives assessed;
  - unverified is always low;
  - the order of links doesn't matter.
- **Why:** the slice asks for property-based tests (GLOSSARY). Hypothesis is the standard Python library for them, and it's free. When a property fails, it shrinks the failing list to the smallest example, which a hand-rolled random generator wouldn't. It's for tests only, never in the app. Decided under autonomous mode (D-017).
- **Where:** `backend/pyproject.toml`, `backend/tests/skills/test_status_rules_properties.py`.

### M4.5 · Build profile and skills API

#### T-158 · A rebuild updates skill rows in place and replaces their evidence and links
- **What:** `build_profile` re-runs every finder (each source's evidence records are replaced, and their links go with them by cascade), then updates the user's `user_skills` rows by skill id and adds fresh links. Rows for skills no evidence names any more are deleted.
- **Why:** the same sources always give the same skills, statuses, confidences and evidence (tested), and the skill row ids, plus the user's hidden / disputed / note, survive a rebuild. Deleting skills without evidence keeps "no skill without a source".
- **Where:** `backend/app/services/skill_profile.py`.
- **Watch out:** evidence ids change on every rebuild, so nothing should store an evidence id for long. Manual projects (M4.10) and user-added skills aren't read yet. Once user-added skills exist, the rebuild must keep their links.

#### T-159 · The reason is computed when skills are read, not stored
- **What:** `GET /skills` computes each skill's `reason` from its stored links with `compute`, after sorting them in a fixed order (supporting first, then type, then quote). Status and confidence are stored, because the database checks them and matching will filter on them.
- **Why:** no new column, and the reason can't disagree with the links. The rules are cheap and deterministic.
- **Where:** `backend/app/services/skill_profile.py`.

#### T-160 · New column `user_skills.note` (migration `d8e2f4a61b37`)
- **What:** optional text, at most 500 characters (checked by the API), set with `PATCH /skills/{id}`. Sending `"note": null` or an empty note clears it. `hidden` and `disputed` can't be cleared with null, only set to true or false.
- **Why:** the slice asks for an optional note when hiding or disputing. 500 characters is enough for a reason and keeps the screen tidy.
- **Where:** `backend/app/db/models/user_skills.py`, `backend/migrations/versions/2026_11_27-d8e2f4a61b37_user_skills_note.py`, `backend/app/api/skills.py`.

#### T-161 · Three endpoints: build, list, correct
- **What:**
  - `POST /skills/build` runs the build and returns the skills.
  - `GET /skills` lists them, strongest first (status, then confidence, then English name), hidden ones included with their flag so the screen can offer "show again".
  - `PATCH /skills/{id}` changes only `hidden`, `disputed` and `note`. Any other field is a 422, and another user's id is a 404 `not_found`.
  - Each skill carries `names` in en, fr and ar, so the screen picks its language without another request.
- **Why:** building can take a moment and writes data, so it's an explicit action rather than a side effect of reading.
- **Where:** `backend/app/api/skills.py`.

#### T-162 · Building before the skill list is loaded answers 503 `skill_list_not_loaded`
- **What:** if the `skills` table is empty, the build refuses with a code. The interface text is in en, fr and ar.
- **Why:** a silent empty result would look like "this CV has no skills". The list is loaded by a command (T-145), not by the app, so a fresh setup can hit this.
- **Where:** `backend/app/services/skill_profile.py`, `backend/app/api/skills.py`, `frontend/src/locales/*.json`.

### M4.10 · Manual projects as evidence, and removing sources

#### T-163 · Saving a project rebuilds the user's skills; deleting anything only recomputes
- **What:** adding or editing a project updates its `sources` row (kind `manual_project`, text = title and description), then runs `build_profile`. Deleting a project, a CV or a repo, importing GitHub again, or withdrawing consent runs `recompute_skills`. That one runs no finder: it removes skills left without any link and recomputes status and confidence from the links that remain, in the same transaction.
- **Why:** after an edit, the new evidence has to be linked at once, or fixing a typo would make a skill disappear until the next build. The rebuild only re-reads stored text, with no network. A deletion never needs to find anything new, so the light step is enough and works even without the skill list.
- **Where:** `backend/app/services/manual_projects.py`, `backend/app/services/skill_profile.py` (`recompute_skills`), `sources.py`, `github_imports.py`.
- **Watch out:** saving a project gives a new user their first skills without pressing "build". That's intended: projects are evidence (M3.3).

#### T-164 · A project is found like CV prose, one finding per sentence, as `manual_project`
- **What:** the title and each description sentence are matched with the shared prose matcher. Location `{"project_id", "field": "title" | "description", "line"}`. The judgement is the CV project test (concrete work or vague mention).
- **Where:** `backend/app/skills/project_finder.py`, `backend/app/services/project_evidence.py`.

#### T-165 · The sources endpoints only show CVs and repos
- **What:** `GET /sources` lists only kinds `cv` and `github_repo`. `DELETE /sources/{id}` on a project's source answers 404 `not_found`.
- **Why:** a project's source is managed with the project. Deleting it from the sources screen would leave a project that no longer counts, without saying so.
- **Where:** `LISTED_KINDS` in `backend/app/services/sources.py`.

#### T-166 · Without the skill list, a project still saves
- **What:** if the `skills` table is empty, saving a project removes its old evidence and recomputes, instead of failing. Skills appear at the next build.
- **Why:** a profile edit shouldn't fail because of server setup. The build endpoint already reports the missing list (T-162).
- **Where:** `backend/app/services/manual_projects.py`.

### M2.1 · LLM spike

#### T-167 · The spike compares Groq, the Gemini free tier and Ollama
- **What:** three $0 options: Groq `llama-3.3-70b-versatile`, Gemini `gemini-2.5-flash`, Ollama `qwen2.5:7b` locally. All are called through the OpenAI-compatible chat endpoint with JSON mode, so one HTTP function serves all three.
- **Why:** one fast hosted free tier with a large open model, one big-lab free tier, one that needs no account and keeps data on the machine. `qwen2.5:7b` is the largest common model that fits the 6 GB laptop GPU. OpenRouter free models and GitHub Models were left out to keep the spike small.
- **Where:** `PROVIDERS` in `spikes/llm/run_spike.py`; limits and terms in `docs/spikes/llm.md`.
- **Watch out:** the Gemini free tier's terms allow human review and product use of prompts and say not to send personal data, so it is a poor fit for real CVs whatever it scores.

#### T-168 · Five spike-only profiles, English and French CVs, answers in all three languages
- **What:** 5 made-up profiles (3 en, 2 fr) with reference answers (must-find skills, allowed skills, acceptable statuses) in `spikes/llm/profiles.py`. Each is asked for explanations in en, fr and ar: 15 calls per model. No Arabic CV, though the slice text asks for one.
- **Why:** M1.5's profile set isn't done yet, and CVs are English/French only (D-030). 15 calls fit even the smallest reported free limit (~20/day for Gemini).
- **Where:** `spikes/llm/profiles.py`.

#### T-169 · The model judges links; the status is computed by the D-006 rules
- **What:** the model returns skills with quoted evidence, a type, `supports`/`weak` and a reason code. The scorer computes the status from those judgements (D-006 choice 4) and compares it with the reference. It also checks that each quote is in the input word for word, and guesses the explanation's language from letters and common words.
- **Why:** that's the AI's only job in the real design, so it's what the spike should measure. The quote check catches made-up evidence. The language check is rough (a sentence full of English skill names can fool it), so the hand read of the answers still matters.
- **Where:** `status_of`, `score_row`, `language_of` in `spikes/llm/score.py`.

#### T-170 · Spike code uses only the standard library and keys come from the shell
- **What:** `urllib` for HTTP, no new dependencies. Keys are read from `SPIKE_GROQ_API_KEY` / `SPIKE_GEMINI_API_KEY` in the shell, never from `.env` and never saved. Raw answers go to `spikes/llm/results/*.jsonl` and are committed. Ruff's line-length and import-order rules are turned off per file for the spike.
- **Why:** throwaway code shouldn't add dependencies to the backend; the `SPIKE_` prefix keeps spike keys apart from the app's `LLM_API_KEY` (M2.2). The profiles are made up, so the answers are safe to commit and let anyone re-score without spending quota.
- **Where:** `spikes/llm/`.

#### T-171 · The spike calls Ollama through its own API with an 8k context
- **What:** for Ollama, `run_spike.py` uses `/api/chat` with `format: "json"`, `num_ctx: 8192`, `num_predict: 4000` and temperature 0, instead of the OpenAI-compatible endpoint.
- **Why:** the OpenAI-compatible endpoint can't change the context window, and Ollama's default (~4k tokens) would cut off long answers without an error. The prompts turned out to be ~1,250 tokens, so this was a precaution; M2.2 should still set `num_ctx` explicitly.
- **Where:** `call` in `spikes/llm/run_spike.py`.

### Repo setup script (no slice)

#### T-078 · `github_setup.py` creates only missing labels
- **What:** `ensure_labels` first lists the repo's labels (`gh label list --json name --limit 200`) and creates only the ones not there yet, like milestones and issues already do. Existing labels keep their current color and description.
- **Why:** `gh label create --force` on an existing label started returning HTTP 500 from GitHub, which stopped the whole setup before it reached the new M11–M16 milestones and issues. Skipping existing labels avoids that call entirely.
- **Also:** `--dry-run` now runs the read calls for real (they change nothing) and skips only the writes. Before, it skipped the reads too, so every dry run listed all labels, milestones and issues as "would create" and couldn't show what was actually new.
- **Where:** `scripts/github_setup.py` (`ensure_labels`, `GH.run`).
- **Watch out:** changing a label's color or description in the script no longer updates GitHub. Edit it on the website (Issues → Labels) instead.

### Session tooling (no slice)

#### T-042 · A hook tells Claude Code sessions about teammates' new work
- **What:** every time a prompt is sent, a `UserPromptSubmit` hook runs `scripts/session_check.py`. At most once every 30 minutes it fetches from GitHub and compares with the previous check. It looks for new commits on `origin/main` by someone other than you, new or updated open PRs, and new branches without a PR. If anything changed, a short note appears in the session; otherwise nothing happens. Its memory is `.git/claude-session-check.json`, one per clone and never committed. The first run only records a starting point.
- **Why:** CLAUDE.md's "Every session, before any work" check only runs when a session starts. A session left open overnight would otherwise never notice teammates' pushes.
- **Where:** `.claude/settings.json` (`hooks`), `scripts/session_check.py`.
- **Watch out:** it never blocks a prompt. If you're offline or `gh` is missing, it stays silent and tries again on the next prompt. Run `python scripts/session_check.py --force` to check by hand. To turn it off, remove the hook in `/hooks` or in `.claude/settings.json`. Commits are matched to you by git `user.name`.
