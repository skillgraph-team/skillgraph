"""Makes the made-up CV files used by the CV upload tests (M3.5). Not a test itself.

The files are committed, so tests and CI never need this script or its fonts. Run it
again only to change the fixtures, from `backend/`:

    uv run python tests/fixtures/cv/make_cv_fixtures.py

It writes, next to itself:
- `cv_en.pdf`, `cv_fr.pdf`, `cv_ar.pdf` and the same three as `.docx`: one short CV
  per language, text from `CV_LINES` below (the tests check for these exact lines).
- `cv_scanned.pdf`: a page that is only a picture, like a scanned paper CV (no text).

The Arabic PDF needs a font with Arabic letters and real text shaping (joined letters,
right-to-left), like Word's "Save as PDF" makes. It uses Arial from Windows by default;
set `CV_FIXTURE_FONT` to another .ttf with Arabic letters (e.g. DejaVuSans.ttf on Linux).
Everyone in these files is made up.
"""

import os
from pathlib import Path

from docx import Document
from fpdf import FPDF
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
FONT = Path(os.environ.get("CV_FIXTURE_FONT", "C:/Windows/Fonts/arial.ttf"))

CV_LINES: dict[str, list[str]] = {
    "en": [
        "Sam Example",
        "Computer science student looking for a backend internship.",
        "Skills: Python, FastAPI, PostgreSQL and Docker.",
        "Experience: intern at Example Startup, where I wrote REST endpoints for the team.",
        "Project: a library management app built with Django and tested with pytest.",
    ],
    "fr": [
        "Camille Exemple",
        "Étudiante en informatique à la recherche d'un stage en développement web.",
        "Compétences : Python, Django, PostgreSQL et le développement de tests.",
        "Expérience : stagiaire chez Exemple SARL, où j'ai écrit des API pour l'équipe.",
        "Projet : une application de gestion de bibliothèque avec une base de données.",
    ],
    "ar": [
        "سارة مثال",
        "طالبة في علوم الحاسوب تبحث عن تدريب في تطوير البرمجيات.",
        "المهارات: بايثون وقواعد البيانات وتعلم الآلة.",
        "الخبرة: متدربة في شركة ناشئة حيث كتبت واجهات برمجية للفريق.",
        "المشروع: تطبيق لإدارة المكتبة مع اختبارات آلية.",
    ],
}


def make_pdf(language: str, path: Path) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("cv", fname=str(FONT))
    pdf.set_font("cv", size=12)
    align = "L"
    if language == "ar":
        pdf.set_text_shaping(use_shaping_engine=True, direction="rtl", script="arab")
        align = "R"
    for line in CV_LINES[language]:
        pdf.multi_cell(0, 8, line, align=align, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(path))


def make_docx(language: str, path: Path) -> None:
    document = Document()
    for line in CV_LINES[language]:
        document.add_paragraph(line)
    document.save(str(path))


def make_scanned_pdf(path: Path) -> None:
    """A page with only a picture on it: grey bars where a scan would show text."""
    picture = Image.new("RGB", (600, 300), "white")
    draw = ImageDraw.Draw(picture)
    for row in range(6):
        draw.rectangle((40, 30 + row * 40, 560, 50 + row * 40), fill="grey")
    pdf = FPDF()
    pdf.add_page()
    pdf.image(picture, x=10, y=10, w=190)
    pdf.output(str(path))


def main() -> None:
    for language in CV_LINES:
        make_pdf(language, HERE / f"cv_{language}.pdf")
        make_docx(language, HERE / f"cv_{language}.docx")
    make_scanned_pdf(HERE / "cv_scanned.pdf")
    print(f"wrote the CV fixtures to {HERE}")


if __name__ == "__main__":
    main()
