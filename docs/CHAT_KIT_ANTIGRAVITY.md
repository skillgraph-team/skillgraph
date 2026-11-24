# Antigravity kit: doing a slice with Google Antigravity

How to work on SkillGraph with **Google Antigravity** (Google's free agent IDE). English first, then the same guide in Algerian Darija ([الدارجة](#الدارجة)).

The rules are the same for everyone (D-011): one slice = one issue = one branch = one PR, tests first, Rasen reviews and merges. This file only explains how to apply them in Antigravity. For the Claude chatbot, see `docs/CHAT_KIT.md`.

> Antigravity changes often. If a menu or setting below has a different name in your version, look for the closest one, then fix this file in your next PR.

---

## 1. How Antigravity fits in

- Antigravity's agent automatically reads `AGENTS.md` at the root of the repo. That file sends it to **`CLAUDE.md`**, which holds the project's rules, architecture, commands and the step-by-step workflow ("Working on a slice"). It was written for Claude Code, but it applies to any agent.
- A few lines in `CLAUDE.md` **don't apply to you**:
  - Everything that says "Rasen works on `main`" or "Rasen works autonomously". You are not Rasen: you always work on a branch, open a PR, and approve the plan before the agent writes code.
  - The 30-minute hook that checks for teammates' work (T-042) only runs in Claude Code. You do the check yourself: pull `main` at the start of every session.
- Unlike the chatbot, the agent sees your files and runs commands itself. That's faster, but **you** are responsible for every command it runs and every file it changes. Read before you approve.

## 2. One-time setup

1. Install **Git**, **Docker Desktop**, **uv**, **Node.js LTS** and **Antigravity**. Sign in to Antigravity with your Google account (the free plan is enough).
2. Install the **GitHub CLI** (`gh`) and run `gh auth login`. The workflow uses it to see PRs, assign issues and open your PR. Without it, do those steps on the GitHub website.
3. Clone the repo (`git clone https://github.com/skillgraph-team/skillgraph.git`) and open the folder in Antigravity.
4. **Safe settings** (in Antigravity's settings):
   - **Terminal commands:** the agent must **ask you before running a command**. Don't use the "run automatically" option. You may put read-only commands in the allow list (`git status`, `git diff`, `git log`, `uv run pytest`, `npm test`).
   - **Review of plans and changes:** the agent must **stop and wait for your review** of its implementation plan. Don't choose "always proceed".
5. Ask the agent to set up the project with you:
   ```
   Read AGENTS.md, CLAUDE.md and README.md. Walk me through README "Getting started" step by step
   until the app runs and the backend and frontend tests pass. Ask me before each command.
   Never open, print or change .env (I'll fill it in myself from .env.example).
   ```
   If a step fails because the README is wrong, fix the README in your first PR so the next person doesn't hit the same problem.

### The free quota
The free plan has a limited agent quota that resets periodically. To make it last:
- **One slice per conversation.** Start a new conversation for every slice.
- Point the agent at the exact files (the slice's "Read first" and the files it changes) instead of letting it read the whole repo.
- If the quota runs out mid-slice: commit what you have **to your branch**, push it, and write in the issue what's done and what's left. You (or a teammate) can pick it up from there.

## 3. Claiming a slice

1. Open the **SkillGraph** board. Pick an unassigned card whose `Depends on` slices are all Done.
2. Read the whole issue: Goal, Why, Read first, Tasks, Done when. If anything is unclear, ask in the group chat.
3. Assign yourself and set **Status** to *In Progress* (or let the agent do it with `gh` in step 4).

## 4. Starting the slice: the prompt

Open a **new conversation** in the agent panel and paste this, replacing `M3.5` with your slice:

```
We're doing slice M3.5 of SkillGraph. Read AGENTS.md and CLAUDE.md first and follow them.

Important differences from what CLAUDE.md says:
- I am NOT Rasen. Always work on a branch (m<n>.<k>-short-name), never commit or push to main,
  and open a pull request at the end. Rasen reviews and merges it.
- Don't start writing code until I approve your plan.
- There's no session hook in this tool: do the "Every session, before any work" checks yourself now.

Then follow CLAUDE.md "Working on a slice" → "Starting":
1. Run the session checks (git status, switch to main and pull, open PRs, teammates' branches)
   and summarise them in 2–5 lines.
2. Read only this slice's section in docs/MILESTONES.md and the files in its "Read first".
   Check the issue isn't assigned to someone else and its "depends" slices are done.
3. Assign me, set the board status to In Progress, create the branch.
4. Write an implementation plan: the goal, the tasks, the "Done when" list, any Open decision it
   needs, and the exact files and tests you'll write. Then stop and wait for my OK.

Rules: tests first; never weaken, skip or delete a test to make it pass; no work outside this
slice; any text users see goes in frontend/src/locales/{en,fr,ar}.json, all three at once;
never open, print or change .env; never read anything outside this repo folder.
```

## 5. While it works

- **Check the implementation plan** against the slice's "Done when" before approving it. Comment on the plan if something is missing or out of scope.
- **Read every command before approving it.** Always refuse:
  - `git push` to `main`, `git push --force`, `git reset --hard`, or `rm -rf` on anything;
  - any command that opens or changes `.env`;
  - edits to existing files in `backend/migrations/versions/` (add a new migration instead), to `backend/eval/data/labels/`, to `.github/`, or to the rules in `CLAUDE.md`, unless the slice says so (see "Do not touch without asking" in `CLAUDE.md`);
  - deleting a test or adding `skip` to make the checks pass.
- **Check the changes** file by file in the diff view. Ask "why did you change this?" about anything you don't understand. That's also how you learn the code.
- **The same fix fails twice?** Tell the agent to stop, explain the root cause, and propose a different approach (a `CLAUDE.md` rule).
- **The browser agent** can test a screen for you (e.g. "open http://localhost:5173 and try the sign-up form in Arabic"). Only use it on the local app, and never sign in to your own accounts in it.
- **Long or confused conversation?** Ask it for a short handoff (what's done, what's left, which files changed), start a new conversation, and paste the handoff plus the prompt from step 4.

## 6. Finishing: the prompt

```
The slice is done. Follow CLAUDE.md "Working on a slice" → "Finishing", for a teammate (not Rasen):
1. Run every check that applies (CLAUDE.md "Commands") and show me the real output.
2. Go through "Done when" item by item and say how each is shown.
3. If the diff is over ~400 lines outside generated files, tell me and propose a split.
4. Add every technical choice to the "Technical choices log" in docs/DECISIONS.md (next free
   T-number). If users see or do anything new, update docs/USER_GUIDE.md.
5. Commit as "M3.5: <imperative summary>", push the branch, and open the PR with
   .github/pull_request_template.md filled in: "Closes #<issue>", a plain-language Review guide,
   How to test it manually, and a Handoff. Show me the PR text before you create it.
6. Report what's unsure or untested.
```

Then tell Rasen in the group chat that the PR is ready. If Rasen asks for changes, make them **on the same branch** (same conversation if it's still short, otherwise a new one with the handoff), commit and push: the PR updates by itself.

## 7. Never

- Paste or let the agent read **secrets** (`.env`, API keys, tokens) or **real people's data**. Real participants' CVs and labels stay in the private team folder (D-013). **Keep that folder outside the repo folder**, so the agent can't read it by accident.
- Commit to `main`. It's protected for teammates anyway: a direct push will fail.
- Merge your own PR.

## 8. Problems

| Problem | What to do |
|---|---|
| `gh` isn't installed or not logged in | `gh auth login`, or do that step on the GitHub website |
| The agent changes files outside the slice | Reject those changes and remind it: "only this slice" |
| Tests pass on your machine, fail in CI | Paste the CI log into the conversation (PR → *Checks*) |
| Docker / database errors | `docker compose up -d db`, then rerun; still failing → group chat |
| Quota is out | Commit to your branch, push, write the status in the issue (section 2) |

---

<div dir="rtl">

## الدارجة

كيفاش تخدم على SkillGraph بـ **Google Antigravity** (الـ IDE تاع Google بالـ agent، باطل).

القواعد هي نفسها للجميع (D-011): slice وحدة = issue وحدة = branch واحد = PR واحد، التستات قبل الكود، وRasen هو لي يشوف ويدير merge. هاد الملف يشرحلك برك كيفاش تطبّقهم في Antigravity. إذا تخدم بالـ chatbot تاع Claude، شوف `docs/CHAT_KIT.md`.

> Antigravity يتبدّل بزاف. إذا لقيت إعداد ولا menu بإسم آخر عندك، دوّر على لي يقربلو، ومن بعد صلّح هاد الملف في الـ PR الجاي تاعك.

## 1. كيفاش يدخل Antigravity في الخدمة

- الـ agent تاع Antigravity يقرا وحدو `AGENTS.md` لي راهو في الـ root تاع الـ repo. هاد الملف يبعثو لـ **`CLAUDE.md`**، وفيه القواعد تاع المشروع، الـ architecture، الـ commands، والخطوات بالتفصيل ("Working on a slice"). تكتب لـ Claude Code، بصح يتطبّق على أي agent.
- كاين شوية حوايج في `CLAUDE.md` **ماشي ليك**:
  - كلش لي يقول "Rasen يخدم على `main`" ولا "Rasen يخدم وحدو". نتا ماكش Rasen: ديما تخدم على branch، تحل PR، وتوافق على الـ plan قبل ما الـ agent يكتب الكود.
  - الـ hook لي يشوف كل 30 دقيقة واش زادو الصحاب (T-042) يخدم غير في Claude Code. نتا لي تشوف: دير pull لـ `main` في بداية كل session.
- ماشي كيما الـ chatbot، الـ agent يشوف الملفات تاعك ويخدّم الـ commands وحدو. هكا أسرع، بصح **نتا** لي مسؤول على كل command يخدّمو وكل ملف يبدّلو. اقرا قبل ما توافق.

## 2. الـ setup (مرة وحدة برك)

1. انصّب **Git**، **Docker Desktop**، **uv**، **Node.js LTS** و **Antigravity**. ادخل لـ Antigravity بالكونط Google تاعك (الـ plan الباطل يكفي).
2. انصّب **GitHub CLI** (`gh`) ودير `gh auth login`. الخدمة تستعملو باش تشوف الـ PRs، تدير assign للـ issues وتحل الـ PR تاعك. بلا بيه، دير هاد الخطوات في الموقع تاع GitHub.
3. دير clone للـ repo (`git clone https://github.com/skillgraph-team/skillgraph.git`) وحل الدوسي في Antigravity.
4. **الإعدادات لي لازم** (في الـ settings تاع Antigravity):
   - **Terminal commands:** الـ agent لازم **يسقسيك قبل ما يخدّم أي command**. ما تختارش "run automatically". تقدر تزيد في الـ allow list غير الـ commands لي يقراو برك (`git status`، `git diff`، `git log`، `uv run pytest`، `npm test`).
   - **Review تاع الـ plan والتبديلات:** الـ agent لازم **يحبس ويستنى حتى تشوف** الـ implementation plan تاعو. ما تختارش "always proceed".
5. قول للـ agent يدير معاك الـ setup. حط هاد الـ prompt (خليه بالإنجليزية، الـ agent يفهم خير):
   ```
   Read AGENTS.md, CLAUDE.md and README.md. Walk me through README "Getting started" step by step
   until the app runs and the backend and frontend tests pass. Ask me before each command.
   Never open, print or change .env (I'll fill it in myself from .env.example).
   ```
   إذا خطوة ما خدمتش على خاطر الـ README غالط، صلّحو في أول PR تاعك باش لي يجي من موراك ما يطيحش في نفس المشكل.

### الـ quota الباطل
الـ plan الباطل عندو quota محدود للـ agent، ويرجع يتعمّر كل مدة. باش يكفيك:
- **slice وحدة في كل conversation.** حل conversation جديدة لكل slice.
- ورّي للـ agent الملفات لي يحتاجهم بالضبط (الـ "Read first" تاع الـ slice والملفات لي راح يبدّلهم)، ما تخليهش يقرا الـ repo كامل.
- إذا كمل الـ quota وانت في نص الـ slice: دير commit للي درت **على الـ branch تاعك**، دير push، واكتب في الـ issue واش كمل وواش بقى. تكمّل نتا من بعد، ولا واحد من الصحاب.

## 3. كيفاش تاخذ slice

1. حل الـ board تاع **SkillGraph**. اختار كارطة ماشي مدّيها حتى واحد، والـ slices لي في `Depends on` تاعها كاملين Done.
2. اقرا الـ issue كامل: Goal، Why، Read first، Tasks، Done when. إذا كاين حاجة ماشي واضحة، سقسي في الـ group.
3. دير لروحك assign وحط **Status** على *In Progress* (ولا خلي الـ agent يديرها بـ `gh` في الخطوة 4).

## 4. تبدا الـ slice: الـ prompt

حل **conversation جديدة** في الـ panel تاع الـ agent وحط هاد الـ prompt. بدّل `M3.5` بالـ slice تاعك، وخليه بالإنجليزية:

```
We're doing slice M3.5 of SkillGraph. Read AGENTS.md and CLAUDE.md first and follow them.

Important differences from what CLAUDE.md says:
- I am NOT Rasen. Always work on a branch (m<n>.<k>-short-name), never commit or push to main,
  and open a pull request at the end. Rasen reviews and merges it.
- Don't start writing code until I approve your plan.
- There's no session hook in this tool: do the "Every session, before any work" checks yourself now.

Then follow CLAUDE.md "Working on a slice" → "Starting":
1. Run the session checks (git status, switch to main and pull, open PRs, teammates' branches)
   and summarise them in 2–5 lines.
2. Read only this slice's section in docs/MILESTONES.md and the files in its "Read first".
   Check the issue isn't assigned to someone else and its "depends" slices are done.
3. Assign me, set the board status to In Progress, create the branch.
4. Write an implementation plan: the goal, the tasks, the "Done when" list, any Open decision it
   needs, and the exact files and tests you'll write. Then stop and wait for my OK.

Rules: tests first; never weaken, skip or delete a test to make it pass; no work outside this
slice; any text users see goes in frontend/src/locales/{en,fr,ar}.json, all three at once;
never open, print or change .env; never read anything outside this repo folder.
```

## 5. وهو يخدم

- **شوف الـ implementation plan** وقارنو مع الـ "Done when" تاع الـ slice قبل ما توافق. إذا كاين حاجة ناقصة ولا خارج الـ slice، اكتب commentaire على الـ plan.
- **اقرا كل command قبل ما توافق عليه.** ديما قول لا لـ:
  - `git push` لـ `main`، `git push --force`، `git reset --hard`، ولا `rm -rf` على أي حاجة؛
  - أي command يحل ولا يبدّل `.env`؛
  - تبديل الملفات لي كاينين في `backend/migrations/versions/` (زيد migration جديدة بلاصتها)، ولا `backend/eval/data/labels/`، ولا `.github/`، ولا القواعد تاع `CLAUDE.md`، إلا إذا الـ slice طلبها (شوف "Do not touch without asking" في `CLAUDE.md`)؛
  - تنحية تست ولا زيادة `skip` باش تفوت الـ checks.
- **شوف التبديلات** ملف بملف في الـ diff. سقسي "علاش بدّلت هادي؟" على كل حاجة ما فهمتهاش. هكا تتعلم الكود تاني.
- **نفس الـ fix ما خدمش زوج مرات؟** قول للـ agent يحبس، يشرح السبب الحقيقي، ويقترح طريقة أخرى (قاعدة من `CLAUDE.md`).
- **الـ browser agent** يقدر يتستيلك شاشة (مثلاً: "open http://localhost:5173 and try the sign-up form in Arabic"). استعملو غير على الـ app لي عندك في الـ PC، وما تدخلش فيه للكونطات تاعك.
- **الـ conversation طوّلت ولا تخلطت؟** طلب منو handoff قصير (واش كمل، واش بقى، واش من ملفات تبدّلو)، حل conversation جديدة، وحط الـ handoff مع الـ prompt تاع الخطوة 4.

## 6. تكمّل: الـ prompt

```
The slice is done. Follow CLAUDE.md "Working on a slice" → "Finishing", for a teammate (not Rasen):
1. Run every check that applies (CLAUDE.md "Commands") and show me the real output.
2. Go through "Done when" item by item and say how each is shown.
3. If the diff is over ~400 lines outside generated files, tell me and propose a split.
4. Add every technical choice to the "Technical choices log" in docs/DECISIONS.md (next free
   T-number). If users see or do anything new, update docs/USER_GUIDE.md.
5. Commit as "M3.5: <imperative summary>", push the branch, and open the PR with
   .github/pull_request_template.md filled in: "Closes #<issue>", a plain-language Review guide,
   How to test it manually, and a Handoff. Show me the PR text before you create it.
6. Report what's unsure or untested.
```

من بعد قول لـ Rasen في الـ group بلي الـ PR واجد. إذا Rasen طلب تبديلات، ديرهم **على نفس الـ branch** (في نفس الـ conversation إذا مازالت قصيرة، ولا في وحدة جديدة مع الـ handoff)، دير commit وpush: الـ PR يتبدّل وحدو.

## 7. عمرك

- ما تحط ولا تخلي الـ agent يقرا **الأسرار** (`.env`، API keys، tokens) ولا **les données تاع ناس حقيقيين**. الـ CVs والـ labels تاع المشاركين الحقيقيين يقعدو في الدوسي الخاص تاع الفريق (D-013). **خلي هاد الدوسي برّا الدوسي تاع الـ repo**، باش الـ agent ما يقراهش بالغلط.
- ما تدير commit على `main`. راهو محمي للصحاب كامل: push مباشر ما يفوتش.
- ما تدير merge للـ PR تاعك وحدك.

## 8. المشاكل

| المشكل | واش تدير |
|---|---|
| `gh` ماشي منصّب ولا ماكش داخل | `gh auth login`، ولا دير الخطوة في الموقع تاع GitHub |
| الـ agent بدّل ملفات خارج الـ slice | ارفض هاد التبديلات وفكّرو: "غير هاد الـ slice" |
| التستات يفوتو عندك ويطيحو في الـ CI | حط الـ log تاع الـ CI في الـ conversation (PR ← *Checks*) |
| أخطاء تاع Docker ولا الـ database | `docker compose up -d db`، وعاود؛ مازال ما خدمش ← الـ group |
| كمل الـ quota | commit على الـ branch تاعك، push، واكتب وين وصلت في الـ issue (القسم 2) |

</div>
