# Decisions

One entry per decision. Status is `Open`, `Proposed` (has a recommendation, waiting for a yes) or `Decided`. Work through one in its own session ("let's decide D-005"). Once `Decided`, change it only with a new entry that supersedes it.

| ID | Question | Status | Needed by |
|---|---|---|---|
| D-001 | How work is split into sessions and PRs | Decided | — |
| D-002 | Who owns the repo, and public or private | Decided | M0.1 |
| D-003 | Frontend framework | Open | M0.4 |
| D-004 | Backend stack and tooling | Decided | M0.2 |
| D-005 | Which free LLM (hosted free tier vs local) | Open | M2.1 |
| D-006 | Evidence model: types, statuses, confidence | Open (contract) | M2.3 |
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
- **Status:** Open
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
- **Status:** Open — owner: _TBD_. Defined in M2.3, written up in `docs/design/evidence-model.md`.

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

