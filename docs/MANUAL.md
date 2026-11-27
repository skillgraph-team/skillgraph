# Manual checks

Things that need a person: opening a page in a browser, clicking through the app,
judging wording, or checking a GitHub setting. Claude Code can't confirm these
itself. Each item names the slice it comes from; the full steps are in that slice's
issue comment ("How to test it manually").

Tick items as you go. When something fails, note it next to the item and open an
issue (or tell Claude Code which item failed).

*Last updated: 2026-11-26, after M4.8.*

---

## 0. Start everything (once per session)

- [ ] Docker Desktop is running.
- [ ] `.env` exists (`cp .env.example .env`). If it was copied before M0.4, check it has
      `VITE_API_BASE_URL=/api` and `BACKEND_URL=http://localhost:8000`.
- [ ] `docker compose up -d db`
- [ ] `cd backend && uv sync && uv run alembic upgrade head && uv run uvicorn app.main:app --reload`
- [ ] Second terminal: `cd frontend && npm install && npm run dev`
- [ ] Old database volume from before M0.3? Run `docker compose down -v` once (this **wipes
      local data**), then start again.

The automated checks (`uv run pytest`, `npm test`, …) run in CI and Claude Code runs them
on every slice, so they're not listed here.

---

## 1. Data to read and judge (M4.1, M4.8, M4.9)

These are files to look at, not code to run. Open the CSVs in a spreadsheet app.

- [ ] **Skill list coverage** (`backend/app/skills/data/skills.csv`, 245 skills). Skim for
      software-engineering skills students commonly list that are missing, or entries
      that don't belong. (T-126)
- [ ] **Short, ambiguous aliases** (`aliases.csv`): `go`, `r`, `c`, `ui`, `ai`, `ts`, `os`.
      Keep or drop? M4.2's CV finder has to avoid matching them as ordinary words.
- [ ] **French names** (`name_fr` column). A fluent French speaker reads them once. (T-134)
- [ ] **Arabic names** (`name_ar` column). A fluent Arabic speaker reads them once:
      Modern Standard Arabic, no diacritics, technical names in Latin letters. (T-134)
- [ ] **Term list** in `docs/design/localization.md` §5: one read by a fluent French
      speaker and a fluent Arabic speaker (asked for since M2.8).
- [ ] **Learning resources** (`resources.csv`). Open about 10 random rows: does each page
      match its title, and is it really free?

## 2. Links to open in a browser (M4.8)

A script confirmed 507 of 526 links. These 19 blocked the script (bot protection, rate
limit or timeout). Open each one. If one is broken, delete its row from `resources.csv`;
every skill still has 2 confirmed links.

- [ ] https://dev.mysql.com/doc/refman/8.4/en/
- [ ] https://dev.mysql.com/doc/refman/8.4/en/tutorial.html
- [ ] https://www.mathworks.com/help/matlab/
- [ ] https://helpx.adobe.com/photoshop/tutorials.html
- [ ] https://helpx.adobe.com/photoshop/user-guide.html
- [ ] https://helpx.adobe.com/xd/tutorials.html
- [ ] https://helpx.adobe.com/xd/user-guide.html
- [ ] https://www.tableau.com/learn/training
- [ ] https://developer.salesforce.com/docs
- [ ] https://devgym.oracle.com/pls/apex/f?p=10001:26
- [ ] https://livesql.oracle.com/
- [ ] https://www.splunk.com/en_us/training/free-courses/overview.html
- [ ] https://apprendre.tv5monde.com/
- [ ] https://francaisfacile.rfi.fr/
- [ ] https://learnenglish.britishcouncil.org/
- [ ] https://tryhackme.com/path/outline/presecurity
- [ ] https://docs.opencv.org/4.x/
- [ ] https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
- [ ] https://www.gnu.org/software/bash/manual/bash.html

---

## 3. Backend API, by hand (http://localhost:8000/docs)

Use "Try it out" on each endpoint. The browser keeps the login cookie between calls.

**Health (M0.3)**
- [ ] http://localhost:8000/health shows `{"status":"ok","database":"ok"}`.
- [ ] `docker compose stop db`, reload: `"database":"unreachable"`. Then `docker compose start db`.

**Sign-up and login (M3.1, M3.10)**
- [ ] `POST /auth/signup` with an email and an 8+ character password → 201; `GET /auth/me` → 200.
- [ ] `POST /auth/logout` → 204; `GET /auth/me` → 401 `not_authenticated`.
- [ ] `POST /auth/login` with a wrong password → 401 `invalid_credentials`.
- [ ] `POST /auth/password` with a wrong current password → 401, then with the right one → 204.
      Log out: the old password fails, the new one works.

**Profile (M3.3)**
- [ ] `GET /profile` is empty for a new user.
- [ ] `PATCH /profile` `{"display_name": "Test", "preferred_language": "ar"}`, then `GET /auth/me` shows `"ar"`.
- [ ] Create, edit and delete a project with `/profile/projects`.
- [ ] As a **second** user, `DELETE` the first user's project → 404 `not_found`; it's still there for the first user.
- [ ] A project link `javascript:alert(1)`, or an education end date before its start date → 422.

**CV upload (M3.5)** (files in `backend/tests/fixtures/cv/`)
- [ ] `cv_en.pdf` → 201, `"language": "en"`, text visible.
- [ ] `cv_fr.docx` → `"language": "fr"`, accents intact (Étudiante, Compétences).
- [ ] `cv_scanned.pdf` → 422 `no_text_found`; a `.txt` or `.png` → 415 `unsupported_file_type`.
- [ ] `backend/storage/uploads/` has one folder per user, one file per upload.

**GitHub import (M3.6, M3.9)** (uses the real GitHub)
- [ ] `POST /sources/github {"username": "octocat"}` without consent → 403 `github_consent_required`.
- [ ] `PUT /profile/github-consent`, then again → 200 with repos. `octocat/Spoon-Knife` has
      language shares and README text; a fork like `octocat/linguist` has `"is_fork": true` and no README.
- [ ] The same request again is instant (cached in `backend/storage/github_cache/`).
- [ ] `{"username": "-bad-"}` → 422; a name that doesn't exist → 404 `github_user_not_found`.
- [ ] `DELETE /profile/github-consent` → 204; the repos are gone, the CV stays.

**Account deletion (M3.9)**
- [ ] `POST /account/delete {"password": "wrong"}` → 403 `wrong_password`.
- [ ] With the real password → 204; `GET /auth/me` → 401; `backend/storage/uploads/<user id>/` is gone.

**Database schema (M2.4)**
- [ ] `uv run alembic downgrade base`, then `uv run alembic upgrade head`: no errors.
- [ ] Optional, in `psql`: `INSERT INTO users (email, password_hash) VALUES ('A@B.com', 'x');` is refused (emails must be lowercase).

---

## 4. The app in a browser (http://localhost:5173)

Do this pass once in English, then repeat the starred (★) steps in **Français** and **العربية**.

**Frontend status (M0.4)**
- [ ] http://localhost:5173/health shows "Backend and database are working", without logging in.
- [ ] Stop the database and reload: "can't reach the database". Stop the backend: "The backend can't be reached".

**Languages and right-to-left (M0.7)**
- [ ] ★ Switch the language: the text changes. In Arabic the whole page mirrors (switcher on the left, text on the right).
- [ ] Reload: the page stays in the last language.
- [ ] DevTools → Application → Local storage: delete `skillgraph.language`, set the browser language to French, reload. The page is in French.

**Sign-up and login screens (M3.2)**
- [ ] A fresh visit lands on **Log in**. **Sign up** shows the "Your data" notice.
- [ ] ★ Email `abc` → "doesn't look like an email address"; 5-character password → "needs at least 8 characters".
- [ ] Sign up properly → home page "Logged in as …".
- [ ] ★ Wrong password → the error message; correct login → the page keeps the account's language.
- [ ] Sign up again with the same email → "An account with this email already exists".
- [ ] Stop the backend and try to log in → "SkillGraph can't be reached right now…".

**Profile screens (M3.4)**
- [ ] Fill in name and headline, **Save** → "Changes saved."
- [ ] In each section (education, experience, projects): Add, Edit, Delete (with "Yes, delete"). Reload between steps; the list matches.
- [ ] ★ A project without a description, a link `javascript:x`, or an end date before the start date: the message shows under the field and nothing is saved.
- [ ] Change the password with a wrong current one → "That password isn't right"; with the right one → "Password changed".
- [ ] ★ In Arabic, a French institution name still reads left to right.

**Sources: CV and GitHub (M3.7)**
- [ ] Upload `cv_fr.pdf`: a progress bar, then "CV added.", listed as French.
- [ ] ★ Upload `cv_scanned.pdf` → "No text was found in this file…"
- [ ] Read the consent text, **Allow GitHub import**, import `octocat`: repos listed and linked.
- [ ] Delete one repo, import again: it comes back.
- [ ] **Withdraw consent** → **Yes, withdraw**: the consent text is back, the repos are gone, the CV stays.
- [ ] ★ In Arabic, repo names and file names keep their own direction.

**Dashboard (M3.8)**
- [ ] With no sources, Recent activity offers "Add a CV or GitHub". After uploading a CV, it's listed on **Home**.
- [ ] ★ Narrow the window: the cards stack. In Arabic the layout mirrors.

---

## 4b. Skills, rule-based (M4)

**Skill list and CV finder (M4.2)**
- [ ] `cd backend && uv run python -m app.skills.taxonomy` prints `skills: 245, aliases: 348, parent links: 258, removed: 0`. Running it again prints the same.
- [ ] `uv run python -m app.skills.check_cv_finder tests/fixtures/cv/cv_en.pdf python,docker,kubernetes` prints `expected 3, found 2, missed 1, wrong 6` and `missed: kubernetes`.
- [ ] Try it on a made-up CV of your own (never a real person's). List the skills you'd expect, and note what's missed or wrong. Misses usually mean a missing alias or heading, which is worth adding.

**Status rules (M4.4)**
- [ ] `uv run pytest tests/skills/test_status_rules.py -v`: one test per worked example in the evidence model, section 9. Read the names; if an example's expected result looks wrong, the evidence model is what needs a new decision.

**Build and skills API (M4.5)** (http://localhost:8000/docs; load the skill list first)
- [ ] Sign up, upload `tests/fixtures/cv/cv_en.pdf`, then `POST /skills/build` → 200. Python is `claimed · medium`, with reason `named_in_list` and the quote "Skills: Python, FastAPI, PostgreSQL and Docker."
- [ ] Give GitHub consent, import `octocat`, build again: the repo languages appear as evidence.
- [ ] `PATCH /skills/{id}` with `{"hidden": true, "note": "test"}` → 200, status unchanged. Build again: still hidden, same note.
- [ ] `PATCH` with `{"status": "assessed"}` → 422. As a second user, `PATCH` the first user's skill → 404 `not_found`.
- [ ] On a fresh database without `python -m app.skills.taxonomy`: `POST /skills/build` → 503 `skill_list_not_loaded`.

---

## 5. GitHub settings and tooling

- [ ] **CI (M0.5):** the Actions tab shows `backend` and `frontend` green on the latest `main` run.
- [ ] **Branch protection (M0.5):** Settings → Rules → Rulesets → `protect-main` still lists its rules. Optional: a branch with a broken test opens a PR whose merge button is blocked (close it afterwards).
- [ ] **Board script on Windows (M0.4):** in a normal terminal, `python scripts/github_setup.py parse` shows `·` correctly in slice titles.

---

## 6. Waiting on people, not checks

These block slices and can only be done by the team:

- [ ] **M1.5 test profiles, M1.6 labeling guide and answers, M1.7 curated postings.** Until
      they exist, #32 (M4.1), #40 (M4.9) and #39 (M4.8) stay open, and M4.7 (first
      evaluation) can't start.
- [ ] **D-005, which free LLM** (via M2.1, the LLM spike). Blocks M2.2 and the agent runtime (M5).
- [ ] **M2.7 screen sketches.** Blocks M4.6 (skills and evidence screen).
