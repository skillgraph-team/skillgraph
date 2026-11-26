# SkillGraph — Spec v0.6

Changes go through a PR approved by Rasen (D-018). Bump the version and add a line to the changelog at the bottom.

## Goal
SkillGraph builds evidence-backed skills profiles for students and recent graduates. It extracts skills from a CV and GitHub, records the evidence behind each skill with a status (claimed / demonstrated / assessed / unverified) and a confidence, matches the profile against a curated set of internships, and explains each match and gap with concrete next steps. A small set of specialized agents, coordinated by an orchestrator, does the analysis, and the project measures whether that multi-agent design beats a rule-based baseline and a single-agent version. The interface and the AI's explanations are in English, French and Arabic; the CVs and postings it reads are in English or French (D-030).

## Non-goals of the MVP (M0–M10)
These are limits of the MVP. Some are lifted by the milestones in "Beyond the MVP" below.
- No recruiter portal, job marketplace, payments or automated hiring decisions.
- No graph database (skill relations live in relational tables).
- No university integrations.
- No scraping of job sites; opportunities are curated by hand from legitimate sources.
- Never calls a skill "verified" because an LLM inferred it. Only an assessment can make a skill `assessed`.
- No assessments in the MVP (D-014): `assessed` exists in the evidence model, but nothing in the MVP produces it.
- No languages beyond English, French and Arabic, and no Arabic CVs or postings (Arabic is for the interface only, D-030). Users' CVs and evidence are never machine-translated: quotes stay in their original language.

## Never, at any stage
- No automated hiring decisions: SkillGraph explains matches; people decide.
- No scraping of sites against their terms.
- A skill is `assessed` only through an assessment; an LLM never decides it.
- No personal data shared with recruiters or institutions without the student's explicit, revocable consent.

## Beyond the MVP (M11–M16, D-029)
Full milestones, scheduled alongside M7–M10. M9 and M10 never depend on them.
- **M11 · Practical assessments:** timed quizzes and practical tasks checked by tests, in English and French only; passing produces `assessment` evidence and the `assessed` status (D-020, supersedes D-014).
- **M12 · More evidence sources:** certificates (with link checks), portfolio websites, LinkedIn PDF exports; weekly re-sync and profile history ("continuously updated profile").
- **M13 · Opportunities at scale:** legitimate sources and employer submissions with moderation, duplicates and expiry, search, notifications and email.
- **M14 · Recruiter side:** opt-in visibility, candidate search and comparison with evidence, contact requests, audit log of views.
- **M15 · Institutions:** consented student linking, aggregate cohort analytics with a minimum group size, training recommendations.
- **M16 · Product:** free and premium plans, payments decision, skill graph view, graph-database check, phone and accessibility pass, landing page, privacy-respecting usage numbers.

## Constraints
- 4 people, one semester (14 weeks). Working prototype before week 9. The graded work (M9, M10) comes first if time runs short.
- **$0 budget.** Free tools, free hosting or a local demo, free or local LLM.
- Custom agent loop and orchestration in Python; no large agent framework.
- The backend owns validation, permissions and every database write. Agents read through tools and return results; they never write.
- All LLM calls go through one provider interface, with recorded responses for repeatable tests and evaluation.
- Every skill keeps references to its source evidence.
- Three languages (D-012, narrowed by D-030): English, French and Arabic (right-to-left) for the interface and AI-written text; CVs, repos and postings in English or French are read correctly. The backend sends codes plus data, not sentences.
- Personal data: consent before GitHub ingestion, account deletion removes everything, no real people's CVs in tests. Real participants' CVs and labels are never committed; they stay in a private team folder (D-013).

## Interfaces
| Module | Input | Output |
|---|---|---|
| Ingestion (CV, GitHub) | uploaded file / GitHub username | `Source` + raw `Evidence` records |
| Skills baseline (rules) | evidence | skill candidates, status, confidence (System A) |
| Profile Agent | CV text, project descriptions | skill candidates normalized to the taxonomy, each with a source span |
| Evidence Evaluation Agent | skill + evidence bundle | status, confidence, rationale citing evidence ids |
| Opportunity Agent | posting text | required / desirable skills, experience, qualifications |
| Matching Agent | profile + opportunity | category/score, matched, missing, weak skills, explanation with evidence |
| Development Agent | gaps | prioritized, concrete recommendations tied to each gap |
| Orchestrator | user request | plan → delegated tasks → consolidated report; bounded retries; run log |
| Agent message envelope | — | task_id, parent_task_id, sender, recipient, task, context, expected_schema, status, result \| error, attempt, language |

## Definition of done (MVP)
For the full product, each of M11–M16 has its own demo in `docs/MILESTONES.md`.

1. A student signs up, uploads a CV, connects a GitHub username, and gets a profile where every skill has a status, a confidence and linked evidence they can inspect.
2. For a curated internship, they get a match report: matched, missing and weakly supported skills, and an explanation that cites evidence.
3. They get a gap analysis with at least one concrete recommendation per missing required skill.
4. Steps 1–3 run through the orchestrated multi-agent workflow with bounded retries, budgets and a viewable run log.
5. The same labeled inputs run through System A (rules), System B (single agent) and System C (multi-agent), and the evaluation table (extraction accuracy, evidence assessment quality, matching precision, completion rate, latency, cost, failure rate, coordination overhead) is filled in with ≥3 runs per system.
6. The app is deployed (free host) or runs as a reproducible local demo, and 5+ students have used it and given feedback.
7. Steps 1–3 work with the interface in English, French and Arabic (right-to-left), and for an English CV and a French CV. The evaluation table is also broken down by language.

## Changelog
- v0.6: the plan now covers the full product (D-029): M11–M16; "Never, at any stage" rules; MVP non-goals marked as MVP-only.
- v0.5: spec changes are approved by Rasen, not the whole team (D-018).
- v0.4: no assessments in the MVP (D-014); real participants' data stays out of the repo (D-013).
- v0.3: English, French and Arabic support (D-012).
- v0.2: $0 budget; provider interface + record/replay; open task claiming with one owner per contract; repo/board setup as the first slice.
- v0.1: first draft from the project report.
