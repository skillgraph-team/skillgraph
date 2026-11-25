# Glossary

Plain-language meanings of the terms used in this repo. Add a term whenever someone has to ask what it means.

## Working on the project
- **Milestone**: a stage of the project with a demo at the end (M0–M10).
- **Slice**: one small piece of work: one issue, one branch, one pull request. Named like `M3.5`.
- **Board**: the GitHub Project showing every slice and its status (Todo, In Progress, Done).
- **Branch**: a separate line of changes, so your work doesn't affect `main` until it's reviewed.
- **Pull request (PR)**: a request to merge a branch into `main`. It's where review happens.
- **Contract**: something everyone else builds on (evidence model, database schema, message format, API). Changing it after it's agreed needs the owner's approval.
- **CI (continuous integration)**: GitHub automatically running the checks (tests, lint, types) on every pull request.
- **Ruleset**: a GitHub setting that protects `main`, e.g. "only via a reviewed pull request with green CI".
- **Spike**: a quick, throwaway experiment to answer a risky question before building on it.
- **Fixture**: fixed example data used by tests (a made-up CV, a saved GitHub response).
- **Lint / type check**: automatic checks for style mistakes and type errors, before the code even runs.

## SkillGraph ideas
- **Evidence**: something that supports a skill: a CV mention, a project description, a repo's languages or code, a certificate, an assessment. Every skill must point to its evidence.
- **Source**: where evidence came from (an uploaded CV, a GitHub account).
- **Status**: how well a skill is supported. *Claimed*: the person says so. *Demonstrated*: supported by work they did. *Assessed*: proven by an assessment. *Unverified*: not enough evidence. Exact rules: `docs/design/evidence-model.md`.
- **Confidence**: how sure we are about a skill's status, on the scale defined in the evidence model.
- **Taxonomy**: our list of skills, with their other names and which skill belongs under which.
- **Alias**: another name for the same skill ("Postgres" for PostgreSQL).
- **Ground truth / labels**: the correct answers written by people for the test profiles. Systems are scored against them.
- **System A / B / C**: the three versions we compare. A: fixed rules, no AI. B: one AI agent. C: several specialized agents with an orchestrator.

## AI and agents
- **LLM**: large language model, the AI that reads and writes text.
- **Prompt**: the instructions given to an LLM.
- **Golden example**: an input with the exact answer we want; used to write prompts and as a test.
- **Structured output**: making the LLM answer in a fixed JSON shape that code can check.
- **Agent**: an LLM with instructions, a set of allowed tools, and an expected answer shape, doing one job.
- **Tool call**: when an agent asks the system to run a function for it (e.g. "get this user's evidence").
- **Agent loop**: ask the LLM → run any tool it asks for → give it the result → repeat until it gives a final answer or hits the step limit.
- **Orchestrator**: the component that splits a request into tasks, gives them to agents in order, passes results along, handles failures and combines the results.
- **State machine**: a fixed set of states and allowed moves between them (a task can go from running to succeeded, never from succeeded back to running).
- **Record / replay, cassette**: saving real LLM answers to files (cassettes) and replaying them in tests, so tests are free, fast and give the same result every time.
- **Rate limit**: a cap on how many requests a service accepts per minute or day. Free LLM tiers and GitHub have them.
- **Retry with backoff**: trying again after a failure, waiting longer each time, a limited number of times.
- **Fault injection**: deliberately making things fail in tests to check the system handles it.
- **Token**: the unit LLMs count text in; it drives cost and limits. (Also, in auth, a login token: see below.)

## Backend and data
- **Endpoint**: one URL the backend responds to, like `GET /skills`.
- **API**: the set of all endpoints the frontend can call.
- **OpenAPI**: a file (`openapi.json`) describing every endpoint, from which frontend types can be generated.
- **Schema**: the database's tables, columns and links between them.
- **ORM**: a library (SQLAlchemy) that lets code work with tables as Python classes.
- **Migration**: a versioned script that changes the database structure, so everyone's database matches.
- **Cascade delete**: deleting a row also deletes the rows that belong to it (deleting a user deletes their evidence).
- **Authentication**: checking who a user is (login).
- **Password hashing**: storing a scrambled form of a password that can be checked but not reversed.
- **Login token / session cookie**: what the browser sends with each request to prove the user is logged in.

## Languages
- **Localization (i18n)**: making the app work in several languages. "i18n" is short for "internationalization" (18 letters between the i and the n).
- **Locale**: a language code the app uses: `en`, `fr` or `ar`.
- **RTL (right-to-left)**: text and layout that run from right to left, as in Arabic. The whole page mirrors: the menu moves to the right, arrows flip.
- **Translation key**: a name for a piece of interface text (`skills.status.demonstrated`) whose words live in `en.json`, `fr.json` and `ar.json`. The code uses the key, never the words.
- **Fallback language**: the language shown when a translation is missing (English).
- **CSS logical properties**: layout rules that follow the reading direction (`margin-inline-start` means "left" in English and "right" in Arabic), so one stylesheet works both ways.
- **Text normalization**: making different spellings of the same word comparable before matching: lowercase, French accents removed (`données` → `donnees`), Arabic letter variants and diacritics unified.
- **Term list**: the agreed translation of each SkillGraph concept in all three languages (`docs/design/localization.md`).

## Beyond the MVP
- **Assessment**: a test a student takes to prove a skill: a timed quiz or a practical task. Passing is the only way to reach the `assessed` status.
- **Practical task**: a small programming exercise with automated tests; the student's solution passes when all tests pass.
- **Sandbox**: an isolated place to run code someone else wrote, so it can't reach our secrets, our database or other users.
- **Template repository**: a GitHub repo students copy to start a practical task; GitHub Actions can run its tests on GitHub's machines.
- **GitHub Actions**: GitHub's service that runs commands (like tests) automatically when code is pushed.
- **SSRF (server-side request forgery)**: tricking our server into fetching an address it shouldn't, like `localhost` or a private network. Any feature that fetches a URL a user gave us must block this.
- **robots.txt**: a file where a website says which pages automated tools may read. We respect it.
- **Role**: what an account is allowed to do (student, organization member, organization admin, platform admin).
- **Moderation**: a person checking content (here, employer postings) before it goes public.
- **Audit log**: a permanent record of sensitive actions, such as who viewed which profile and when.
- **Minimum group size**: the smallest group for which an aggregate figure is shown; smaller groups are hidden so no one can be singled out.
- **Transactional email**: an email sent because of something a user did (password reset, notification), not marketing.
- **Accessibility**: making the app usable by everyone, including with a keyboard only, a screen reader, or low vision.

## Evaluation
- **Precision**: of the skills the system found, the share that were correct.
- **Recall**: of the correct skills, the share the system found.
- **F1**: one number combining precision and recall.
- **Precision@k**: of the top k recommended postings, the share that were labeled relevant.
- **Coordination overhead**: the extra time and cost of having several agents talk to each other instead of one.
- **Property-based test**: a test that checks a rule on many generated inputs ("more evidence never lowers confidence"), not just a few hand-picked ones.
