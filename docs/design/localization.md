# Languages: rules and term list

**Contract** (D-012, written in M2.8). **Owner: Rasen.** Changing a rule or a term here needs the owner's approval in the PR.
Used by: every screen (`frontend/src/locales/`), the backend's error and result codes, the agents' prompts (M6), the skill names (M4.9), and the assessments (M11).

SkillGraph works in **English, French and Arabic** (Arabic is right-to-left). This page says which text is translated where, and gives the words for SkillGraph's key ideas, so that "demonstrated" is the same word on every screen and in every explanation. If a screen or a prompt uses a different word for a term on this list, that's a bug.

---

## 1. Who writes which text

| Text | Written by | Language | Where it lives |
|---|---|---|---|
| Interface text (buttons, labels, messages, status names, errors) | People, through translation keys | The interface language | `frontend/src/locales/{en,fr,ar}.json` |
| Errors and results from the backend | The backend sends a **code plus data**, never a sentence: `{"code": "not_found"}`, `{"status": "demonstrated", "confidence": "high"}` | — | The frontend turns each code into text with a key (section 4) |
| Explanations and recommendations written by the AI | The agents, directly in the user's language | The `language` field of the message envelope (`app/agents/runtime/messages.py`) | Stored as written; never translated afterwards |
| Quotes from CVs, repos and postings | Nobody: copied exactly | Their **original** language, whatever the interface language | Evidence records (evidence model §6) |
| Skill names | The taxonomy | Each skill has a name per language (M4.9); technical names stay in Latin letters (section 3) | `backend/app/skills/data/skills.csv` |
| Assessment content (questions, tasks, their explanations) | People (M11) | **English and French only** (D-020); the screens around it are in all three | M11's question bank |

The rules behind the table:

1. **No text users see is written in the code.** Frontend code uses a key (`t("skills.status.demonstrated")`), and the words go in all three locale files in the same change. A key that exists in one file must exist in the other two.
2. **The backend never builds sentences.** It returns codes (`snake_case`, English, stable) and the data the sentence needs (numbers, names, ids). Adding a new code means adding its key in all three files.
3. **Agents write in the language they're given.** The orchestrator passes the user's `preferred_language`; each agent writes its explanation or recommendation in that language and uses the terms in section 5 for SkillGraph's ideas. If an agent can't write well enough in Arabic (risk noted in D-012, measured in M2.1), that's handled by the fallback D-012 describes, never by translating the output with another tool.
4. **Quotes are never translated,** not even "for convenience". A French CV shown in the Arabic interface shows its French quote, marked `lang="fr"` and `dir="auto"` (section 6). The explanation around it is in Arabic.
5. **English is the source language.** New text is written in English first, then in French and Arabic in the same change. If a translation is missing at runtime, the English text is shown (the fallback), but a missing translation is still a bug.
6. **Assessments are the one exception** (D-020). With the interface in Arabic, the student picks English or French for the assessment content. Everything around it (the list of assessments, buttons, timer, results page) is in the interface language like any other screen.

## 2. Picking the language

- On a first visit, the browser's language if it's one of the three, otherwise English. The user can switch at any time; once logged in, the choice is saved to their account (`users.preferred_language`, `PATCH /profile`).
- The page's `lang` and `dir` follow the interface language (`dir="rtl"` for Arabic). This is set in one place, `frontend/src/i18n`.
- The language of a **source** (CV, repo, posting) is detected separately and stored on its evidence (`en`, `fr`, `ar` or `other`). It doesn't depend on the interface language.

## 3. Style

### All three languages
- **Western digits** (0–9) everywhere, including Arabic. Numbers and dates are formatted with `frontend/src/i18n/format.ts`, which uses each language's separators and month names.
- **Technical names stay in Latin letters** and aren't translated: Python, Docker, PostgreSQL, React, GitHub, REST API, SQL. SkillGraph itself is always "SkillGraph".
- **Short and plain.** Interface text says what to do or what happened, in everyday words. No exclamation marks in errors.
- **Keep the same meaning, not the same words.** A translation can reorder a sentence; it can't add or drop information.

### French
- **"Vous"**, not "tu". SkillGraph is a career tool, and its users show it to employers and teachers; "vous" is the usual choice for that kind of tool and reads as polite, not distant.
- French typography: a **narrow no-break space (U+202F)** before `?`, `!`, `;` and `:`, and inside « guillemets ». (The existing `fr.json` already does this.)
- Inclusive spelling ("étudiant·e") isn't used. Prefer words that don't need it ("vos compétences", "la personne").

### Arabic
- **Modern Standard Arabic** (فصحى), not a regional dialect, so it reads correctly for users from every Arabic-speaking country.
- **Don't assume the user's gender.** Arabic second-person forms are gendered, so:
  - buttons and menu items use a **verbal noun** instead of an order: «رفع السيرة الذاتية», not «ارفع سيرتك الذاتية»;
  - messages are **impersonal** where possible: «تم حفظ التغييرات», not «لقد حفظتَ التغييرات»;
  - when a sentence really has to address the user, use the masculine singular (the usual grammatical default in Arabic software), and keep such sentences rare.
- Arabic punctuation: «،» for commas, «؛» for semicolons, «؟» for question marks.
- No diacritics (تشكيل), except where a word would be misread without them.

## 4. Translation keys

- Keys are English, lowercase, grouped by screen or topic, dot-separated: `profile.education.add`, `errors.not_found`.
- **Codes from the backend map to keys by name.** The key is the group plus the code exactly as the backend sends it, so no mapping table is needed:

| Backend code | Key |
|---|---|
| status `claimed`, `demonstrated`, `assessed`, `unverified` | `skills.status.<code>` |
| confidence `low`, `medium`, `high` | `skills.confidence.<code>` |
| judgement `supports`, `weak` | `evidence.judgement.<code>` |
| match category `strong`, `partial`, `weak` | `matches.category.<code>` |
| importance `required`, `nice_to_have` | `opportunities.importance.<code>` |
| error `{"code": "<code>"}` | `errors.<code>` |

The words for these keys are in section 5. A slice that first shows one of them on screen copies them into the locale files from there.

## 5. Term list

**Status of this list:** proposed by Claude Code in M2.8, approved by Rasen. Each term should still be read once by a fluent French speaker and a fluent Arabic speaker on the team; any change goes through a PR that updates this table and the locale files together.

Statuses and confidence are written as adjectives that agree with "compétence" (feminine) in French and «مهارة» (feminine) in Arabic, because they're almost always shown next to a skill.

### Evidence and skills

| Term (code) | English | French | Arabic | Notes |
|---|---|---|---|---|
| skill | skill | compétence | مهارة | |
| evidence | evidence | preuve | دليل (pl. أدلة) | "Preuves" in lists: « 3 preuves » |
| source | source | source | مصدر | A CV, a repo, a certificate, a project the user added |
| profile | profile | profil | الملف الشخصي | |
| status | status | statut | الحالة | |
| `claimed` | claimed | déclarée | مُصرَّح بها | The person says they have it |
| `demonstrated` | demonstrated | démontrée | مُثبَتة | Shown by work they did |
| `assessed` | assessed | évaluée | مُقيَّمة | Proven by a SkillGraph assessment (M11) |
| `unverified` | unverified | non vérifiée | غير مُتحقَّق منها | Only a hint; not enough evidence |
| confidence | confidence | confiance | درجة الثقة | |
| `low` | low | faible | منخفضة | |
| `medium` | medium | moyenne | متوسطة | |
| `high` | high | élevée | عالية | |
| `supports` | supports | appuie | يدعم | Judgement on one piece of evidence |
| `weak` (judgement) | weak | faible | ضعيف | |
| quote | quote | extrait | مقتطف | The exact text copied from a source |
| hide (a skill) | hide | masquer | إخفاء | |
| dispute (a skill) | dispute | contester | الاعتراض | |
| add a skill | add a skill | ajouter une compétence | إضافة مهارة | Added by the user: at most `claimed` |

### Sources

| Term | English | French | Arabic | Notes |
|---|---|---|---|---|
| CV | CV | CV | السيرة الذاتية | |
| GitHub repository | repository (repo) | dépôt | مستودع | "GitHub" stays in Latin letters |
| certificate | certificate | certificat | شهادة | |
| project (added by hand) | project | projet | مشروع | |
| education | education | formation | التعليم | Profile section |
| experience | experience | expérience | الخبرة | Profile section |

### Opportunities and matching

| Term (code) | English | French | Arabic | Notes |
|---|---|---|---|---|
| opportunity | opportunity | opportunité | فرصة | Any posting: internship or job |
| `internship` | internship | stage | تدريب | In Algeria «تربص» is common; MSA «تدريب» is understood everywhere |
| `job` | job | emploi | وظيفة | |
| posting | posting | offre | عرض | |
| `required` | required | requise | مطلوبة | A skill the posting needs |
| `nice_to_have` | nice to have | souhaitée | مرغوب فيها | |
| match | match | correspondance | التوافق | |
| `strong` match | strong match | forte correspondance | توافق قوي | |
| `partial` match | partial match | correspondance partielle | توافق جزئي | |
| `weak` match | weak match | faible correspondance | توافق ضعيف | |
| matched skill | matched | présente | متوفرة | The profile has the required skill |
| missing skill | missing | manquante | مفقودة | |
| weakly supported skill | to strengthen | à renforcer | تحتاج إلى تعزيز | Required skill the profile has, but only weakly |
| gap | gap | écart | فجوة | |
| gap analysis | gap analysis | analyse des écarts | تحليل الفجوات | |
| recommendation | recommendation | recommandation | توصية | |
| explanation | explanation | explication | شرح | Why a match or status is what it is |

### Assessments (M11)

| Term | English | French | Arabic | Notes |
|---|---|---|---|---|
| assessment | assessment | évaluation | تقييم | Matches `assessed` / évaluée / مُقيَّمة |
| quiz | quiz | quiz | اختبار قصير | |
| practical task | practical task | exercice pratique | مهمة تطبيقية | |
| passed | passed | réussie | ناجح | |
| failed | not passed | non réussie | غير ناجح | "Not passed", never "failed": softer, and accurate for a retry |

### Account

| Term | English | French | Arabic |
|---|---|---|---|
| account | account | compte | الحساب |
| sign up | sign up | s'inscrire / inscription | إنشاء حساب |
| log in | log in | se connecter / connexion | تسجيل الدخول |
| log out | log out | se déconnecter / déconnexion | تسجيل الخروج |
| password | password | mot de passe | كلمة المرور |
| delete my account | delete account | supprimer le compte | حذف الحساب |
| language | language | langue | اللغة |

## 6. Mixed directions

Arabic text often contains Latin words (Python, a French quote, a URL). To keep them readable:

- **Quotes and anything a user typed** are shown with `dir="auto"` and, for quotes, `lang` set to the evidence's detected language. The browser then lays each one out in its own direction.
- **A Latin name inside an Arabic sentence** (a skill name, a repo name) goes in `<bdi>` (or an interpolated element with `dir="auto"`), so punctuation next to it doesn't jump to the wrong side.
- **Layout uses CSS logical properties only** (`margin-inline-start`, `padding-inline-end`, `inset-inline-start`), never `left` / `right`, so one stylesheet works both ways. Icons that point a direction (arrows, "next") flip in Arabic; icons that don't (a check mark, a GitHub logo) don't.
- **Check every new screen in Arabic** before calling it done (MILESTONES rule).

## 7. Using this page

- **Adding a screen:** write the English text, take SkillGraph terms from section 5, add the same keys to `fr.json` and `ar.json`, follow section 3, check it in Arabic.
- **Adding a backend code:** add the key in all three files (section 4) in the same PR, or in the PR of the screen that first shows it.
- **Writing a prompt (M6):** tell the agent the output language, give it the section 5 terms for that language, and remind it that quotes stay in their original language.
- **A term is missing:** add a row here in the same PR, with all three languages, and say so in the review guide.
