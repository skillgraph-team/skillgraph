# Chat kit: doing a slice with the Claude chatbot

Anyone can take any slice. This is how to do one with the Claude chatbot. (With Claude Code, just tell it which slice; CLAUDE.md gives it the steps. With Google Antigravity, see `docs/CHAT_KIT_ANTIGRAVITY.md`. With another tool, follow the same steps in spirit.)

- **Part A**: slices that only produce documents or data (research, labels, prompts, sketches, docs). Chatbot + GitHub website.
- **Part B**: slices that change code. Chatbot + your computer + GitHub Desktop.
- **Part C**: reviewing someone else's pull request.

## Claiming a slice
1. Open the **SkillGraph** board. Pick an unassigned card whose `Depends on` slices are all Done.
2. Read the whole issue: Goal, Why, Read first, Tasks, Done when. If anything is unclear, ask in the group chat before starting, and improve the slice text in `docs/MILESTONES.md` afterwards so the next person doesn't have to ask.
3. **Assignees** → assign yourself. Set **Status** to *In Progress*.
4. One slice per chat. Start a new conversation for every slice.

**Never paste** real names, emails, phone numbers or addresses (anonymize CVs and interview notes first), `.env` files or API keys.

---

## Part A: docs and data slices

### A1. Start the chat
Paste this, filled in:

```
You're helping me with one task ("slice") in SkillGraph, a 4-person student startup project:
an evidence-based skills platform that extracts skills from a CV and GitHub, links each skill
to its evidence with a status (claimed / demonstrated / assessed / unverified) and a confidence,
and matches students to internships with explanations and gap analysis.

Rules:
- Work only on this slice. If something outside it seems needed, tell me instead of doing it.
- Ask me up to 3 questions if anything is unclear, then state your assumptions.
- For every file you produce, give its exact path in the repo and its complete contents
  in one code block, ready to paste. CSV and JSON must be valid.
- Don't invent facts, links or numbers. Mark anything you're unsure about.
- Explain any term I might not know (our glossary is below if I paste it).
- At the end, check the "Done when" list item by item and tell me what's still missing.

The slice (copied from the GitHub issue):
<paste the whole issue>

Project files it needs:
<paste docs/SPEC.md, plus any file the slice names>
```

Which files to paste: always `docs/SPEC.md`; every file in the slice's **Read first**; and `docs/GLOSSARY.md` if the slice uses terms you don't know. To copy a file from GitHub, open it and click **Copy raw file**.

If your Claude plan has Projects, put SPEC.md, DECISIONS.md and the evidence model in a "SkillGraph" project once instead of pasting them every time.

### A2. Save it to the repo from the website
1. On the repo page, go to the folder. Click **Add file → Create new file** (or **Upload files** for several).
2. Type the path in the name box; `/` creates folders (e.g. `docs/research/competitors.md`). Paste the contents.
3. **Commit changes…** → **Create a new branch for this commit and start a pull request** → name it after the slice (`m1.3-competitors`) → **Propose changes**.
4. Fill in the PR template, include `Closes #<issue number>`, click **Create pull request**.
5. To add more files to the same PR, switch to your branch in the branch dropdown first, then **Add file** and commit to that branch.
6. Ask Rasen to review and merge it (D-016).

---

## Part B: code slices with the chatbot

### B1. One-time setup (slice M0.6)
1. Install: **Git**, **GitHub Desktop**, **VS Code**, **Docker Desktop**, **uv**, **Node.js LTS**.
2. GitHub Desktop → *File → Clone repository* → `skillgraph`.
3. In GitHub Desktop: *Repository → Open in Terminal* (or Command Prompt), then follow README "Getting started" to the point where the app runs and the tests pass. If a step fails, paste the exact error into the chatbot and fix it; then fix README too so the next person doesn't hit it.

### B2. Start the slice
1. GitHub Desktop: switch to `main`, click **Fetch origin**, then **Pull origin**.
2. *Branch → New branch*, named after the slice: `m3.3-profile-api`.
3. Collect what the chatbot needs:
   - the issue text, and every file in its **Read first**;
   - `CLAUDE.md` (the project's rules, architecture and conventions; they apply to you too);
   - the list of existing files in the area: in the terminal, `git ls-files backend/app` (or `frontend/src`);
   - the full current contents of every file you expect to change, plus one or two similar existing files to copy the style from (e.g. an existing endpoint and its test).

### B3. The prompt
```
You're my pair programmer on one slice of SkillGraph, a student project. I'll paste the code
you write into my editor, run it, and paste back any errors. You can't see my files, so rely
only on what I paste.

Rules:
- Follow the project rules in CLAUDE.md below (architecture, conventions, "do not touch").
- First, give me a short plan: files to create or change and the tests to write. Wait for my OK.
- Write the tests first, then the code.
- Always give me COMPLETE files with their path, never partial snippets or "..." placeholders.
- Don't add libraries unless the slice needs them; if you do, tell me the exact install command.
- Any text users see goes in the translation files for English, French and Arabic
  (frontend/src/locales/), never directly in the code, using the terms in docs/design/localization.md.
  Layouts must work right-to-left for Arabic (CSS logical properties).
- When a test fails, find the cause in the code. Never change a test just to make it pass;
  if you think a test is wrong, explain why and let me decide.
- If the same fix fails twice, stop and rethink the approach instead of patching again.

CLAUDE.md:
<paste>

The slice:
<paste the issue>

Existing files in this area:
<paste git ls-files output>

Files I'll change, and examples to follow:
<paste each file with its path>
```

### B4. The loop
1. Paste each file into VS Code at the path given (create folders if needed).
2. Run the checks for what you changed, from CLAUDE.md "Commands" (backend: pytest, ruff, mypy; frontend: lint, check, test).
3. Paste any error, **complete and unedited**, back into the chat. Repeat until everything passes.
4. Check the slice's "Done when" list yourself, item by item.
5. If the chat gets long or confused, start a new chat with the same prompt and the files as they are now.
6. Stuck after two real attempts? Post in the group chat. Don't let a slice sit.

### B5. Open the PR
1. GitHub Desktop: review the changed files on the left (nothing unexpected, no `.env`), write the summary `M3.3: add profile CRUD endpoints`, **Commit**, then **Publish branch**.
2. Click **Create Pull Request**. Fill in the template, including `Closes #<issue>` and the test results.
3. Rasen reviews it. If Rasen asks for changes, make them on the same branch, commit and **Push origin**; the PR updates by itself.

---

## Part C: review someone else's pull request
Rasen reviews and merges every teammate's pull request (D-016); you can still review any PR to learn the code, or when Rasen asks you to. (With Claude Code: "review PR 12".)

1. Open the PR. Read its **Review guide** and **How to test it manually**.
2. Get the changes: add `.diff` to the end of the PR's URL (works when the repo is public) and copy everything. Otherwise use **Files changed** and copy file by file.
3. In a new chat, paste:

```
I want to review a pull request in our project SkillGraph. I'm not the author.
1. Explain in plain language what it changes and why, file by file.
2. Explain from scratch any concept or term I might not know.
3. List anything that looks wrong, risky, untested, or not matching the slice's "Done when" list.
4. Give me 3 questions to ask the author.
5. Point out anything that breaks the project rules in CLAUDE.md (pasted below).

CLAUDE.md: <paste>
The slice: <paste the issue>
The PR description: <paste>
The diff: <paste>
```

4. If the diff is too long for one message, send it in parts and say "more coming" until the last one.
5. If it has manual test steps: in GitHub Desktop, open the **Current branch** dropdown → **Pull requests** tab → pick the PR, then run them.
6. On GitHub: **Files changed → Review changes →** *Approve*, *Comment* (questions), or *Request changes*.
