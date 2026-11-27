"""Five made-up test profiles for the M2.1 LLM spike, with the answer a person would give.

Throwaway spike code (not part of the app). Nobody here is a real person.
Three profiles are in English and two in French; there is no Arabic CV because CVs are
English/French only (D-030). Each model is still asked to answer in en, fr and ar.

`reference` lists, per skill id (from backend/app/skills/data/skills.csv), the statuses a
person following docs/design/evidence-model.md would accept, and whether the skill must be
found (`must=True`) or is merely allowed (inferred or borderline skills: not penalised if
listed, not required).
"""

from typing import TypedDict


class Ref(TypedDict):
    ok: set[str]  # acceptable statuses
    must: bool


class Profile(TypedDict):
    id: str
    cv_language: str
    cv: str
    repos: str
    reference: dict[str, Ref]


def must(*ok: str) -> Ref:
    return {"ok": set(ok), "must": True}


def allowed(*ok: str) -> Ref:
    return {"ok": set(ok), "must": False}


PROFILES: list[Profile] = [
    {
        # The report's worked example (evidence-model.md 9.1).
        "id": "p1-en-backend",
        "cv_language": "en",
        "cv": (
            "SUMMARY\nThird-year computer science student looking for a backend internship.\n"
            "SKILLS\nPython, SQL\n"
            "PROJECTS\nshop-api: Built a REST API with FastAPI for a small online shop, "
            "storing orders in PostgreSQL.\n"
            "EDUCATION\nBSc Computer Science (in progress)"
        ),
        "repos": (
            "Repo shop-api (owner: the person, not a fork). Languages: Python 90%, HTML 10%. "
            "Dependencies (requirements.txt): fastapi, psycopg. "
            "Code: app/routes.py defines FastAPI routes; app/db.py runs SQL queries against PostgreSQL."
        ),
        "reference": {
            "python": must("demonstrated"),
            "sql": must("demonstrated"),
            "fastapi": must("demonstrated"),
            "rest-api": must("demonstrated"),
            "postgresql": must("demonstrated"),
            "backend-development": allowed("unverified", "claimed"),
            "html": allowed("demonstrated", "unverified"),
        },
    },
    {
        # No GitHub; a certificate; a "wants to learn" mention.
        "id": "p2-en-data-analyst",
        "cv_language": "en",
        "cv": (
            "SUMMARY\nData analyst intern who works with Excel and Power BI every day. "
            "Interested in machine learning.\n"
            "EXPERIENCE\nData analyst intern, retail company (6 months): built monthly sales "
            "dashboards in Power BI for three regional teams.\n"
            "SKILLS\nPython, pandas, SQL, Tableau\n"
            "CERTIFICATES\nGoogle Data Analytics Professional Certificate"
        ),
        "repos": "No GitHub account given.",
        "reference": {
            "power-bi": must("demonstrated"),
            "excel": must("claimed"),
            "python": must("claimed"),
            "pandas": must("claimed"),
            "sql": must("claimed"),
            "tableau": must("claimed"),
            "data-analysis": must("claimed", "demonstrated"),
            "data-visualization": allowed("demonstrated", "unverified", "claimed"),
            "business-intelligence": allowed("demonstrated", "unverified", "claimed"),
            "machine-learning": allowed("unverified"),
        },
    },
    {
        # A forked repo, a small language share, a vague mention.
        "id": "p3-en-frontend",
        "cv_language": "en",
        "cv": (
            "SKILLS\nReact, JavaScript, CSS, familiar with Docker\n"
            "PROJECTS\nPortfolio: developed a personal portfolio website in React with a "
            "responsive layout.\n"
            "EDUCATION\nBachelor in web development (2nd year)"
        ),
        "repos": (
            "Repo portfolio (owner: the person, not a fork). Languages: JavaScript 70%, CSS 25%, "
            "HTML 3%, Dockerfile 2%. Dependencies (package.json): react, react-dom. "
            "Code: src/components/ defines React components; styles in src/App.css.\n"
            "Repo awesome-vue (a fork of someone else's repo). Languages: Vue 95%, JavaScript 5%."
        ),
        "reference": {
            "react": must("demonstrated"),
            "javascript": must("demonstrated"),
            "css": must("demonstrated"),
            "docker": must("claimed"),
            "html": allowed("unverified"),
            "vue": allowed("unverified"),
            "responsive-design": allowed("demonstrated", "claimed"),
            "frontend-development": allowed("unverified", "claimed"),
            "web-development": allowed("unverified", "claimed"),
        },
    },
    {
        # French CV, no GitHub (evidence-model.md 9.2 style).
        "id": "p4-fr-java",
        "cv_language": "fr",
        "cv": (
            "COMPÉTENCES\nJava, Spring Boot, MySQL, Git, notions de Docker\n"
            "EXPÉRIENCE\nStage de 3 mois dans une PME : développement d'une API REST avec "
            "Spring Boot pour la gestion des stocks.\n"
            "PROJETS\nApplication mobile Android en Kotlin pour réserver des salles de cours.\n"
            "LANGUES\nAnglais (B2)\n"
            "FORMATION\nLicence 3 informatique"
        ),
        "repos": "Pas de compte GitHub.",
        "reference": {
            "java": must("claimed"),
            "spring-boot": must("demonstrated"),
            "rest-api": must("demonstrated"),
            "mysql": must("claimed"),
            "git": must("claimed"),
            "docker": must("claimed"),
            "android": must("demonstrated"),
            "kotlin": must("demonstrated"),
            "english": must("claimed"),
            "spring": allowed("demonstrated", "claimed", "unverified"),
            "mobile-development": allowed("demonstrated", "unverified"),
            "backend-development": allowed("unverified", "demonstrated"),
        },
    },
    {
        # French CV with an English repo; dependency-only and README-only hints.
        "id": "p5-fr-data-science",
        "cv_language": "fr",
        "cv": (
            "PROFIL\nÉtudiante en master data science, passionnée par le NLP.\n"
            "COMPÉTENCES\nPython, scikit-learn, TensorFlow, SQL\n"
            "PROJETS\nClassification de tweets avec un modèle BERT (Hugging Face) entraîné "
            "avec PyTorch.\n"
            "FORMATION\nMaster 1 Data Science"
        ),
        "repos": (
            "Repo tweet-classifier (owner: the person, not a fork). Languages: Jupyter Notebook 85%, "
            "Python 15%. Dependencies (requirements.txt): torch, transformers, pandas. "
            "Code: train.py fine-tunes a BERT model with the transformers Trainer. "
            "README: 'The demo can be deployed with Docker.'"
        ),
        "reference": {
            "python": must("demonstrated"),
            "pytorch": must("demonstrated"),
            "hugging-face": must("demonstrated"),
            "nlp": must("claimed", "demonstrated"),
            "scikit-learn": must("claimed"),
            "tensorflow": must("claimed"),
            "sql": must("claimed"),
            "pandas": allowed("unverified"),
            "docker": allowed("unverified"),
            "jupyter": allowed("demonstrated", "unverified"),
            "data-science": allowed("claimed", "unverified"),
            "deep-learning": allowed("unverified", "demonstrated", "claimed"),
            "machine-learning": allowed("unverified", "claimed", "demonstrated"),
            "llms": allowed("unverified"),
        },
    },
]

# ruff: noqa: E402, E501  (throwaway spike: long prompt strings, imports after sys.path)
