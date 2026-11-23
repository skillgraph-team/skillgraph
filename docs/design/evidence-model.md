# Evidence model

**Contract** (D-006). **Owner: Rasen.** Changing anything here needs a new D-entry approved by the owner.
Used by: database schema (M2.4), hand labels (M1.6), skill finders (M4.2, M4.3), status rules (M4.4), Evidence Evaluation Agent (M6.3), matching, and the UI.

This page defines what counts as evidence, how a skill's **status** and **confidence** follow from its evidence, and gives worked examples. If code, labels or prompts disagree with this page, this page wins and the other thing is a bug.

---

## 1. The pieces

| Term | What it is |
|---|---|
| **Source** | One thing we read: an uploaded CV, one GitHub repo, a certificate, a project the user typed in. Has a `source_id`. |
| **Evidence record** | One exact piece of a source that mentions or shows a skill: the quote, where it is, its type and its language (section 6). |
| **Evidence link** | Connects one skill to one evidence record, with a **judgement**: `supports` or `weak` (section 3). One evidence record can be linked to several skills ("built a REST API with FastAPI and PostgreSQL" → three skills). |
| **Skill record** | A skill on a person's profile, with its links, its status and its confidence. **No skill record without at least one link** ("no skill without a source"). |

The flow is always the same, in all three systems (rules, single agent, multi-agent):

1. Finders (or an agent) create evidence records and link them to skills.
2. Rules (System A) or an agent (Systems B and C) mark each link `supports` or `weak`.
3. **Fixed rules** (section 4 and 5) turn the links into status and confidence. No system picks the status freely; the systems only differ in how well they do step 2.

---

## 2. Evidence types

A fixed list. Every evidence record has exactly one type. The **level** column says the most a supporting link of that type can do for a status.

| Type | What it is | Level when `supports` | Points to |
|---|---|---|---|
| `cv_skills_list` | The skill is named in the CV's skills / technologies list | claim | CV section, page |
| `cv_summary` | The skill is named in the CV's profile / summary / objective | claim | CV section, page |
| `cv_experience` | A job, internship or volunteering entry describes using the skill | work | CV section, page |
| `cv_project` | A project entry on the CV describes using the skill | work | CV section, page |
| `cv_education` | A degree, course or module name mentions the skill | context only (never raises status) | CV section, page |
| `certificate` | A course certificate or certification naming the skill | claim | certificate source, or CV section |
| `repo_language` | GitHub's language share for a repo | work, only if the conditions in 3.2 hold | repo, language, share |
| `repo_dependency` | A package in a dependency file (`requirements.txt`, `pyproject.toml`, `package.json`, …) | context only (never raises status) | repo, file path, line |
| `repo_code` | Code in the repo that actually uses the skill (routes, queries, tests, config) | work | repo, file path, lines |
| `repo_readme` | The repo's README mentions the skill | context only (never raises status) | repo, file path, lines |
| `manual_project` | A project the user described in the app (not on the CV) | work | manual project id |
| `user_added` | The user added the skill by hand (section 8) | claim | — (the user's action) |
| `assessment` | Result of a practical assessment. **Nothing produces this in the MVP (D-014).** | assessment | assessment id |

Groups used by the rules:
- **Work types:** `cv_experience`, `cv_project`, `repo_language`, `repo_code`, `manual_project`
- **Claim types:** `cv_skills_list`, `cv_summary`, `certificate`, `user_added`
- **Context types:** `cv_education`, `repo_dependency`, `repo_readme`. They are stored because they help explain a skill and point to where to look, but they never raise a status or confidence. Their links are always `weak`. A validator rejects `supports` on them.
- **Assessment type:** `assessment`

Why a certificate is only a claim: finishing a course isn't doing the work. It still raises confidence (section 5).

---

## 3. Judging one link: `supports` or `weak`

This is the only judgement a rule or an agent makes. Judge **this one piece of evidence** for **this one skill**. Don't look at the person's other evidence.

### 3.1 General test
- **`supports`**: the evidence states the skill directly (claim types) or shows the person doing concrete work with it (work types).
- **`weak`**: it only hints at the skill, mentions it in passing, or the skill has to be guessed from something else.

### 3.2 Per type

| Type | `supports` when… | `weak` when… |
|---|---|---|
| `cv_skills_list`, `cv_summary` | The skill is named as something the person has, at any level ("Python", "notions de Docker"). | The person only says they want to learn it ("interested in Kubernetes"), or the skill is only guessed from another one. |
| `cv_experience`, `cv_project` | The text names the skill **used in concrete work**: what was built or done with it. "Built a REST API with FastAPI", "Développement d'un tableau de bord en React". | Vague or passive: "familiar with Docker", "exposure to Agile", a bare "Technologies: …" line without saying what was done. **A weak link here still makes the skill claimed** (section 4), because the person says it. |
| `certificate` | The certificate names the skill or is clearly about it. | Only loosely related ("Digital skills fundamentals" for SQL). |
| `repo_language` | **All three hold:** the language is **≥ 10 %** of the repo's code (GitHub's byte share); the repo is **owned by the person's GitHub account**; the repo **is not a fork**. | Any of the three fails. |
| `repo_code` | The code in a repo owned by the person (not a fork) really uses the skill: defines routes, runs queries, configures the tool, has tests for it. | Generated or template code only, a one-line import, or the repo is a fork / not owned by the person. |
| `manual_project` | Same test as `cv_project`. | Same as `cv_project`. |
| `user_added` | Always `supports` (it's the person's own claim). | — |
| `cv_education`, `repo_dependency`, `repo_readme` | Never. | Always. |
| `assessment` | The person passed the assessment for this skill. | Failed or incomplete. |

"Owned by the person's GitHub account" means the repo's owner is the GitHub username the person gave us. In the MVP this doesn't prove the account is theirs (see D-009).

### 3.3 Inferred skills
A skill that doesn't appear anywhere, but follows from others ("Python + REST API + PostgreSQL" → "backend development"), is linked to the **same evidence records** as the skills it comes from, every link `weak`, with reason code `inferred_from_related` and the ids of those skills. Result: always **unverified · low** unless direct evidence for it shows up. (An inferred link to a CV project never counts as a vague mention: the text doesn't name the skill.)

### 3.4 Reason codes
Each link carries a short reason code so the UI can explain it in the user's language (the backend never returns sentences). The starting list; M4.4 and M6.3 may add codes but must not reuse one for a different meaning:

`concrete_work`, `named_in_list`, `named_in_summary`, `vague_mention`, `wants_to_learn`, `certificate_match`, `certificate_loose`, `language_share_ok`, `language_share_low`, `not_owned_repo`, `forked_repo`, `code_uses_skill`, `template_or_trivial_code`, `dependency_only`, `readme_only`, `education_only`, `added_by_user`, `inferred_from_related`, `assessment_passed`, `assessment_failed`.

---

## 4. Status rules

Statuses form a ladder: **unverified < claimed < demonstrated < assessed**. A skill gets the highest step its links reach:

```
assessed      if any link is type assessment            and supports
demonstrated  elif any link is a work type               and supports
claimed       elif any link is a claim type              and supports
              or   any link is cv_experience/cv_project  and weak      (a vague mention is still the person's claim)
                                                         and not inferred_from_related
unverified    otherwise   (only weak links, only inferred links, or no links at all)
```

- An **empty** list of links gives `unverified`. Skill records never have an empty list, but the same rules are used for job requirements, where "no evidence" is the normal case.
- **`assessed` is never produced in the MVP** (D-014): no assessment evidence exists, and rules and agents must not output it.
- The rules are deterministic: the same links always give the same status. An agent that reports a status must report the one these rules give for its own judgements. If not, the validator rejects it.

---

## 5. Confidence rules

Three levels: **low < medium < high**. Shown as words (translation keys), stored as the codes `low` / `medium` / `high`, mapped to 1 / 2 / 3 for charts.

Count the person's **independent supporting links**: links marked `supports`, of a work, claim or assessment type, counted once per distinct **(source, type)** pair. Two links are independent if they come from different sources (the CV and a repo, two different repos) **or** have different types (the CV's skills list and a CV project).

| Count | Confidence |
|---|---|
| 0 | **low**: only weak or inferred evidence |
| 1 | **medium** |
| 2 or more | **high** |

- `unverified` is always **low** (it has 0 supporting links by definition).
- Weak links never add to confidence. So a skill claimed only through a vague CV project mention is **claimed · low**.
- Two `repo_code` links in the same repo count once. One CV project description alone is at most **medium**.
- Adding a supporting link can only keep or raise the count, so **more supporting evidence never lowers confidence**. This is a property test in M4.4.

Confidence is about how well-backed the skill is overall, so links below the status's level still count: a skill demonstrated by a repo and also listed on the CV is high.

---

## 6. What an evidence record stores

| Field | Rule |
|---|---|
| `type` | One value from section 2. |
| `source_id` | The CV, repo, certificate or manual project it came from. |
| `quote` | The exact text, copied character for character, **at most ~300 characters** (cut at a word boundary and mark the cut with `…`). For `repo_language` there is no text: store e.g. `Python 90%`. **Never translated.** |
| `location` | Where to find it: CV section name and page; repo full name + file path + line range; dependency file + line; language + share for `repo_language`. |
| `language` | Detected language of the quote: `en`, `fr`, `ar` or `other`. Code and package names count as `other`. |

- The UI shows quotes exactly as stored, inside an element with `lang="<language>"` and `dir="auto"`, so Arabic quotes display right-to-left inside an English page and the other way round.
- Agents and explanations cite evidence by its id, never by retyping the quote.
- Deleting a user deletes their sources, evidence records and links.
- Exact column names and tables are M2.4's job; the fields above are what it must hold.

---

## 7. Guardrails (checked by a validator, M4.4 / M6.3)

1. No skill record without at least one link.
2. A link can only cite evidence records that were given to the agent for this person.
3. `supports` is rejected on a context type (`cv_education`, `repo_dependency`, `repo_readme`).
4. `supports` is rejected on a `repo_language` link that fails the conditions in 3.2 (the data to check is in `location`).
5. `demonstrated` is rejected unless at least one work-type link is `supports`. `assessed` is rejected in the MVP.
6. The reported status and confidence must equal what sections 4 and 5 compute from the links.

---

## 8. User corrections

Users can **hide**, **dispute** or **add** a skill. They can never raise a status directly.

- **Hide:** the skill stays stored but isn't shown and isn't used in matching.
- **Dispute:** the skill is flagged `disputed`. Status and confidence stay as computed; the UI shows the flag.
- **Add:** creates a `user_added` evidence record and link (claim type, `supports`). So an added skill is at most **claimed** on its own; if other evidence already demonstrates it, nothing changes.

Building these features is a later slice; the model only needs the `user_added` type and the hidden / disputed flags.

---

## 9. Worked examples

Each table lists every link for the skill, its judgement, then the result. "CV" is one source; each repo is its own source.

### 9.1 Report §4.3: Python REST API with PostgreSQL

Repo `shop-api`, owned by the person, not a fork: 90 % Python; FastAPI route handlers in `app/routes.py`; `psycopg` in `requirements.txt`; SQL queries against a PostgreSQL database in `app/db.py`. The CV skills list says "Python, SQL".

| Skill | Links | Status · confidence | Why |
|---|---|---|---|
| Python | `repo_language` "Python 90%" supports · `repo_code` `app/routes.py` supports · `cv_skills_list` "Python" supports | **demonstrated · high** | Work-type support; 3 independent links. |
| SQL | `repo_code` `app/db.py` supports · `cv_skills_list` "SQL" supports | **demonstrated · high** | Work-type support; 2 independent links (repo + CV). |
| REST API development | `repo_code` `app/routes.py` supports · `repo_dependency` `fastapi` weak | **demonstrated · medium** | One supporting link; the dependency doesn't count. |
| PostgreSQL | `repo_code` `app/db.py` (connects with psycopg, PostgreSQL-specific SQL) supports · `repo_dependency` `psycopg` weak | **demonstrated · medium** | One supporting link. With only the dependency it would be unverified · low. |
| Backend development | all links weak, `inferred_from_related` (Python, REST API, PostgreSQL) | **unverified · low** | Inferred only. |

This is the point of report §4.3: the five skills come from the same repo but don't all get the same confidence.

### 9.2 French CV, no GitHub

Skills list: « Python, Django, Git ». Projects: « Développement d'une application de gestion de bibliothèque avec Django et PostgreSQL (authentification, recherche, API REST). » Education: « Licence Informatique – module Bases de données ».

| Skill | Links | Status · confidence |
|---|---|---|
| Django | `cv_project` supports (`concrete_work`) · `cv_skills_list` supports | **demonstrated · high** (same CV, but two different types) |
| PostgreSQL | `cv_project` supports | **demonstrated · medium** |
| REST API development | `cv_project` supports | **demonstrated · medium** |
| Python | `cv_skills_list` supports | **claimed · medium** (the project names Django, not Python; we don't infer it into a support) |
| Git | `cv_skills_list` supports | **claimed · medium** |
| Databases | `cv_education` weak (`education_only`) | **unverified · low** |

Quotes are stored in French with `language: fr`, even when the user reads the app in English or Arabic.

### 9.3 Arabic CV with a vague mention

Skills list: «المهارات: Python، تعلّم الآلة». Experience: «متدرّب في شركة ناشئة: اطّلعت على Docker». (Roughly: "Intern at a startup: got acquainted with Docker.")

| Skill | Links | Status · confidence |
|---|---|---|
| Python | `cv_skills_list` supports | **claimed · medium** |
| Machine learning | `cv_skills_list` supports | **claimed · medium** |
| Docker | `cv_experience` weak (`vague_mention`) | **claimed · low**: the person says it, but no concrete work |

Quotes are stored in Arabic with `language: ar` and shown with `dir="auto"`. (The Arabic sample text should be checked by a fluent member, as in M2.8.)

### 9.4 A forked repo

Repo `awesome-dashboard` is a **fork** of someone else's project: 80 % JavaScript, React components. Nothing on the CV mentions JavaScript or React.

| Skill | Links | Status · confidence |
|---|---|---|
| JavaScript | `repo_language` weak (`forked_repo`) | **unverified · low** |
| React | `repo_code` weak (`forked_repo`) | **unverified · low** |

If the CV listed "JavaScript", JavaScript would become **claimed · medium**: the fork still adds nothing.

### 9.5 Certificate plus skills list

Certificate "AWS Certified Cloud Practitioner"; the CV skills list says "AWS".

| Skill | Links | Status · confidence |
|---|---|---|
| AWS | `certificate` supports · `cv_skills_list` supports | **claimed · high**: claimed because neither is work; high because two independent links |

### 9.6 A small language share

Repo `thesis-tools`, owned, not a fork: 94 % Python, 6 % Shell.

| Skill | Links | Status · confidence |
|---|---|---|
| Shell scripting | `repo_language` weak (`language_share_low`) | **unverified · low** |

If `scripts/build.sh` does real work, a `repo_code` link to it supports, giving **demonstrated · medium**.

### 9.7 User corrections

- The user adds "Figma" (no other evidence): `user_added` supports → **claimed · medium**.
- The user disputes "Machine learning" from 9.3: stays **claimed · medium**, flagged `disputed`.
- The user hides "Git": still stored as **claimed · medium**, not shown and not used in matching.

### 9.8 A job requirement with no evidence

A posting requires "Kubernetes"; the person has nothing linked to it. The rules on an empty list give **unverified · low**, which matching reports as a gap.

---

## 10. Using this page

- **Labelers (M1.6):** for each skill, list its evidence, judge each link with section 3, then read status and confidence off sections 4 and 5. Don't judge the status "by feel".
- **Rules (M4.4):** sections 3–5 are the specification. Every example in section 9 should become a test.
- **Agents (M6.3):** the agent's job is section 3 (and the reason codes). Status and confidence are then computed or validated by section 7.
- **Schema (M2.4):** the allowed values for type, judgement, status, confidence and language are exactly the codes on this page.
