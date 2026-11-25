"""Tests for reading the text out of a CV file (M3.5): PDF and Word, in en, fr and ar,
and clear errors for files we can't use. No database needed.

The CV files are made up, see tests/fixtures/cv/make_cv_fixtures.py.
"""

import io
import zipfile
from pathlib import Path

import pytest

from app.ingestion.cv_text import (
    CvFile,
    NoTextFoundError,
    UnreadableFileError,
    UnsupportedFileTypeError,
    clean_text,
    read_cv,
)
from tests.fixtures.cv.make_cv_fixtures import CV_LINES

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "cv"
LANGUAGES = ["en", "fr", "ar"]


def fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("extension", ["pdf", "docx"])
def test_reads_every_line_of_the_cv(language: str, extension: str) -> None:
    cv = read_cv(fixture(f"cv_{language}.{extension}"))

    assert isinstance(cv, CvFile)
    assert cv.file_type == extension
    assert cv.text.splitlines() == CV_LINES[language]


def test_arabic_pdf_keeps_letters_joined_and_in_reading_order() -> None:
    """Some PDF readers give Arabic words back to front (ةسدنهم for مهندسة) or as
    one-off letter shapes (U+FE70 to U+FEFF). Neither may happen here."""
    text = read_cv(fixture("cv_ar.pdf")).text

    assert "المهارات: بايثون وقواعد البيانات وتعلم الآلة." in text
    assert "تارا" not in text  # "المهارات" reversed
    assert not any("\ufb50" <= char <= "\ufeff" for char in text)


def test_pdf_reports_its_page_count() -> None:
    assert read_cv(fixture("cv_en.pdf")).pages == 1
    assert read_cv(fixture("cv_en.docx")).pages is None


def test_scanned_pdf_has_no_text() -> None:
    with pytest.raises(NoTextFoundError):
        read_cv(fixture("cv_scanned.pdf"))


def test_broken_pdf_is_unreadable() -> None:
    cut_in_half = fixture("cv_en.pdf")[:2000]

    with pytest.raises(UnreadableFileError):
        read_cv(cut_in_half)


def test_zip_that_is_not_a_word_file_is_unsupported() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("notes.txt", "hello")

    with pytest.raises(UnsupportedFileTypeError):
        read_cv(buffer.getvalue())


def test_broken_word_file_is_unreadable() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("word/document.xml", "<not really xml")

    with pytest.raises(UnreadableFileError):
        read_cv(buffer.getvalue())


def test_word_file_that_unzips_to_something_huge_is_refused() -> None:
    """A small zip can unpack to gigabytes (a "zip bomb"); we check before unpacking."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", "a" * (60 * 1024 * 1024))

    with pytest.raises(UnreadableFileError):
        read_cv(buffer.getvalue())


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"just some plain text",
        b"\x89PNG\r\n\x1a\n" + b"\x00" * 50,
        b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 50,  # old .doc (Word 97-2003)
    ],
    ids=["empty", "text", "png", "old-doc"],
)
def test_other_files_are_unsupported(data: bytes) -> None:
    with pytest.raises(UnsupportedFileTypeError):
        read_cv(data)


def test_word_file_with_only_blank_paragraphs_has_no_text() -> None:
    from docx import Document

    document = Document()
    document.add_paragraph("   ")
    buffer = io.BytesIO()
    document.save(buffer)

    with pytest.raises(NoTextFoundError):
        read_cv(buffer.getvalue())


def test_word_tables_are_read_too() -> None:
    """Many CV templates put the skills list in a table."""
    from docx import Document

    document = Document()
    document.add_paragraph("Sam Example")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Skills"
    table.cell(0, 1).text = "Python, SQL"
    buffer = io.BytesIO()
    document.save(buffer)

    text = read_cv(buffer.getvalue()).text

    assert "Python, SQL" in text


def test_clean_text() -> None:
    raw = "  Sam\x00 Example  \r\n\r\n\r\n\r\nSkills:\tPython \ufb01  \n   "

    # NUL removed (PostgreSQL can't store it), "fi" ligature (U+FB01) split, spaces trimmed,
    # at most one empty line in a row, Windows line ends made plain.
    assert clean_text(raw) == "Sam Example\n\nSkills:\tPython fi"


def test_clean_text_turns_arabic_letter_shapes_into_letters() -> None:
    # "سارة" written with the one-off presentation shapes some PDF makers use.
    shapes = "\ufeb3\ufe8e\ufead\ufe93"

    assert clean_text(shapes) == "سارة"
