# SkillGraph user guide

How to use SkillGraph, written for the people using it: students, recent graduates, and anyone trying the demo. It describes only what works today. Features still being built are listed at the end.

_Last updated: 2026-11-26, after M3.4 (profile screens)._

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
- Once you're logged in, your choice is also saved to your account. When you log in on another computer, SkillGraph switches to your account's language.
- On your first visit, SkillGraph uses your browser's language if it's one of the three, otherwise English.
- Numbers and dates follow your language's conventions, always with the digits 0–9.

## 3. Creating an account and logging in

Everything except the status page (section 5) needs an account. If you aren't logged in, SkillGraph shows the **Log in** page.

**Creating an account**
1. On the Log in page, next to "No account yet?", click **Sign up**.
2. Enter your email and a password of at least 8 characters.
3. Read the short **Your data** notice: what SkillGraph stores, what it's used for, and that deleting your account removes all of it.
4. Click **Sign up**. You're logged in right away. Your account gets the language the page is in.

**Logging in:** enter your email and password and click **Log in**. If you tried to open a page before logging in, you're taken back to it.

**Logging out:** click **Log out** at the top of the page.

There's no "forgot my password" email yet. If you lose your password, ask whoever runs your SkillGraph.

| Message (English) | What it means |
|---|---|
| Enter your email and password. | One of the two fields is empty. |
| This doesn't look like an email address. | Check the email for typos. |
| The password needs at least 8 characters. | Choose a longer password. |
| An account with this email already exists. | Log in instead, or use another email. |
| Wrong email or password. | One of the two is wrong. For your safety, SkillGraph doesn't say which. |
| SkillGraph can't be reached right now. Try again in a moment. | The backend isn't running (see section 5). |

## 4. Your profile

Click **Profile** at the top of the page.

- **Name and headline:** fill them in and click **Save**. A headline is one line about you, such as "Computer science student looking for a data internship".
- **Education, Experience, Projects:** click **Add education** (or **Add experience**, **Add a project**), fill in the form and click **Save**. Fields marked * are required. A project needs a title and a description; its link must start with `http://` or `https://`.
- **Editing:** click **Edit** next to an entry, change it, and click **Save** (or **Cancel**).
- **Deleting:** click **Delete** next to an entry, then **Yes, delete**. This can't be undone.
- If something isn't right, a message shows under the field, for example "The end date is before the start date."
- Dates are shown as month and year. An entry with no end date shows "present".
- You can write entries in any language; each text is shown in its own direction, also in the Arabic interface.

**Changing your password:** at the bottom of the Profile page, enter your current password and a new one (at least 8 characters), then click **Change password**. You stay logged in. If the current password is wrong, the message says "That password isn't right." and nothing changes.

## 5. Checking that SkillGraph is working

Open **http://localhost:5173/health** to see whether SkillGraph's parts are running:

| Message (English) | What it means | What to do |
|---|---|---|
| Checking the backend… | The page is asking the backend. | Wait a moment. |
| Backend and database are working. | Everything is ready. | Nothing. |
| The backend is running, but it can't reach the database. | The database isn't running. | Run `docker compose up -d db` (step 1 above), then reload. |
| The backend can't be reached. Is it running? | The backend isn't running. | Start it (step 2 above), then reload. |

## 6. Coming later

These are planned (see `docs/MILESTONES.md`) but **not available yet**:

- Deleting your account from the screen (it works in the backend already)
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
