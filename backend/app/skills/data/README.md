# Skill list (taxonomy)

The skills SkillGraph knows about, their other names, and which skill belongs under which.
Three CSV files (UTF-8, comma-separated, with a header row). They are loaded into the
`skills`, `skill_aliases` and `skill_relations` tables (loader: M4.2). The structure
checks are in `backend/tests/skills/test_skill_data.py`.

## The files

**`skills.csv`**: `id,name_en,category`
- `id`: lowercase, readable and permanent: `postgresql`, `node.js`, `c++`, `c#`.
  Letters, digits and `. + # _ -` only, and it starts with a letter or digit (the
  database refuses anything else). Use `-` between words: `spring-boot`.
  **Never rename an id** once it's used. Profiles and postings point at it.
- `name_en`: the English name shown to users (`PostgreSQL`). French and Arabic names
  come in M4.9 (`name_fr`, `name_ar`).
- `category`: one of the values below.

**`aliases.csv`**: `alias,skill_id`
- Other ways people write the skill: `postgres,postgresql`, `js,javascript`,
  `bases de données,databases`.
- Lowercase, keeping accents (`développement web`). Matching later removes case,
  punctuation and accent differences, so you don't need `Postgres` *and* `postgres`.
- Don't repeat the skill's own id or English name; those are matched anyway.
- Each alias belongs to **one** skill. If a word could mean two skills, leave it out.

**`relations.csv`**: `child_id,parent_id`
- "child belongs under parent": `postgresql,sql`, then `sql,databases`. A skill can have
  several parents (`r` is under both `programming` and `data-analysis`). Only link to
  the nearest parent: `postgresql → databases` is already implied by the chain.
- No loops (a skill can't end up under itself).

## Categories

| category | for | examples |
|---|---|---|
| `area` | a broad field that groups other skills | `databases`, `web-development` |
| `language` | a programming or markup language | `python`, `sql`, `html` |
| `framework` | a framework or platform you build on | `react`, `django`, `android` |
| `library` | a library used inside code | `pandas`, `pytorch` |
| `database` | a database engine | `postgresql`, `mongodb` |
| `cloud` | a cloud provider or hosted service | `aws`, `firebase` |
| `devops` | build, deploy and run tools | `docker`, `kubernetes` |
| `tool` | other software people use | `git`, `figma`, `excel` |
| `data` | data and analytics skills and tools | `statistics`, `apache-spark` |
| `ai` | AI and machine learning topics | `deep-learning`, `nlp` |
| `practice` | a method or way of working | `rest-api`, `agile`, `unit-testing` |
| `soft` | soft skills | `teamwork`, `communication` |
| `spoken_language` | human languages | `english`, `french` |

A new category also needs to be added to `CATEGORIES` in the test file.

## How to add a skill

1. Check it isn't already there under another name: search `skills.csv` *and*
   `aliases.csv`.
2. Add a row to `skills.csv`: id, English name, category.
3. Add its other names to `aliases.csv` (English and French spellings, short forms).
4. Add one row per parent to `relations.csv`.
5. Run `cd backend && uv run pytest tests/skills`. It reports duplicates, bad ids, aliases
   pointing nowhere and loops.

Keep the list between 150 and 300 skills (the test checks this). It's meant to cover
what student internships ask for, not every technology there is.
