# SkillGraph user guide

How to use SkillGraph, written for the people using it: students, recent graduates, and anyone trying the demo. It describes only what works today. Features still being built are listed at the end.

_Last updated: 2026-11-23, after M0.7 (three-language support)._

> **For contributors:** update this guide in the same commit as any slice that changes what a user sees or does (CLAUDE.md, "Finishing"). See "Keeping this guide up to date" at the end.

---

## 1. Opening SkillGraph

SkillGraph isn't online yet (hosting is decided in M10.1). For now it runs on your own computer. The first-time setup (tools, cloning the repo, `.env`) is in the README, under "Getting started". After that, each time:

1. Start the database: `docker compose up -d db`
2. Start the backend: `cd backend && uv run uvicorn app.main:app --reload`
3. In a second terminal, start the frontend: `cd frontend && npm run dev`
4. Open **http://localhost:5173** in your browser.

## 2. Choosing your language

SkillGraph works in **English**, **French** and **Arabic**.

- Use the **Language** menu at the top of the page. Each language is listed in its own language: English, Français, العربية.
- The whole page switches at once. In Arabic it reads right-to-left: the menu moves to the left and the text lines up on the right.
- Your choice is remembered in this browser, so the next visit opens in the same language.
- On your first visit, SkillGraph uses your browser's language if it's one of the three, otherwise English.
- Numbers and dates follow your language's conventions, always with the digits 0–9.

## 3. Checking that SkillGraph is working

The home page currently shows whether SkillGraph's parts are running:

| Message (English) | What it means | What to do |
|---|---|---|
| Checking the backend… | The page is asking the backend. | Wait a moment. |
| Backend and database are working. | Everything is ready. | Nothing. |
| The backend is running, but it can't reach the database. | The database isn't running. | Run `docker compose up -d db` (step 1 above), then reload. |
| The backend can't be reached. Is it running? | The backend isn't running. | Start it (step 2 above), then reload. |

## 4. Coming later

These are planned (see `docs/MILESTONES.md`) but **not available yet**:

- Creating an account and logging in
- Uploading your CV and linking your GitHub profile
- Seeing your skills, each linked to its evidence, with a status: claimed, demonstrated, assessed or unverified
- Matching your profile against curated internships, with an explanation of each match and each gap
- Recommendations for closing your skill gaps

---

## Keeping this guide up to date

- Write for a user, not a developer: say what they click and what they see, not how the code works.
- Each feature gets its own numbered section. When a feature from "Coming later" ships, move it into a section and remove it from the list.
- Describe only what works on `main`. Mark anything partial plainly ("for now…").
- Interface text quoted here is the English text from `frontend/src/locales/en.json`. If a quoted label changes there, change it here.
- Update the "Last updated" line with the date and the slice.
