# Kickoff: from this folder to a working team repo

For Rasen, once. About 30–45 minutes.

## 1. Decide two things first (5 minutes)
Read D-002 and D-010 in `docs/DECISIONS.md`.
- If you choose a **GitHub organization** (recommended): on github.com, click your avatar → *Your organizations* → *New organization* → *Free*. Name it something like `skillgraph-team`.
- Note your teammates' GitHub usernames.

## 2. Install and log in
Git, GitHub CLI, Docker, uv, Node.js LTS, Python 3.12, Claude Code. Then:
```bash
gh auth login
gh auth refresh -s project      # lets scripts and Claude Code manage the board
```

## 3. Start Claude Code in this folder
Open a terminal in the `skillgraph` folder (the one containing `CLAUDE.md`) and run `claude`. Starting it one folder up means it won't load the project rules.
(On Windows, use `python` where the docs say `python3`, or vice versa.)

## 4. Tell it what you want
Talk normally. Something like:

> Let's do M0.1, setting up the repo and board. The repo doesn't exist yet. Walk me through it: explain D-002 and D-010 and record my choices, check my tools are installed, create the repo and push these files, then do a dry run of the setup script and show me what it will create before running it for real. My teammates are <user1>, <user2>, <user3>.

You don't need to list every step. `docs/KICKOFF.md` and CLAUDE.md give it the details, and it will ask when it needs a decision from you.

## 5. Manual steps Claude Code can't do
- On the board: *⋯ → Workflows*: check "Item closed" and "Pull request merged" set Status to Done.
- If the board belongs to your personal account (not an org): board *Settings → Manage access* → add each teammate as Writer.
- Optional board views: a **Board** view grouped by Status, a **Table** view grouped by Milestone, and a view filtered to `assignee:@me`.

## 6. Tell the team
Send them the repo link and this message: "Accept the invite, read README.md and docs/CHAT_KIT.md, then claim any open slice on the board whose dependencies are done. Right now that's M0.2, M0.4, M1.1, M1.3 and M2.8."

The first week has five independent starting points (M0.2, M0.4, M1.1, M1.3, M2.8), so everyone can begin at once. Do M0.7 (three languages in the frontend) right after M0.4, before any real screen is built.

## Every session after this
Just talk to it:
- **"Let's do M2.3"**: it pulls the latest code, reads that slice, claims the issue, makes a branch, restates the plan and waits for your go-ahead.
- **"This is done"** or **"open the PR"**: it runs the checks, checks "Done when", commits, pushes and opens the PR with a review guide.
- **"Review PR 12"**: it runs and reviews a teammate's work and gives you a verdict.
- **"Let's decide D-005"**: it explains the options and records your choice.
- **"What should I work on?"**: it lists open slices whose dependencies are done.

One slice per session: type `/clear` (or open a new session) before starting the next one. It keeps each session small, which saves your usage. If a session gets long, finish what's done, open the PR, and turn the rest into a new slice. For L-sized slices, ask for the plan first and agree on it before any code.
