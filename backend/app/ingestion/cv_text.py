"""Reads the plain text out of an uploaded CV: a PDF or a Word (.docx) file (M3.5).

`read_cv(data)` takes the file's bytes and returns a `CvFile` (type, text, pages), or
raises one of the errors below. It never looks at the file name or the type the
browser sent: those are easy to fake, so the type is decided from the bytes.

- PDF: read with pypdf, page by page. pypdf keeps Arabic letters joined and in reading
  order; pdfminer.six, tried in M3.5, gave every Arabic word back to front (T-083).
- Word: read with python-docx, paragraphs and tables in document order. Old `.doc`
  files (Word 97-2003) are not supported.

The text is then tidied by `clean_text` (see there). Nothing is translated.
"""

import io
import logging
import re
import unicodedata
import zipfile
from dataclasses import dataclass
from typing import Literal

from docx import Document
from docx.table import Table
from pypdf import PdfReader

logger = logging.getLogger(__name__)

FileType = Literal["pdf", "docx"]

MAX_PDF_PAGES = 20
"""A CV is a few pages. More is refused, so one upload can't keep the server busy."""

MAX_UNZIPPED_BYTES = 50 * 1024 * 1024
"""A .docx is a zip file; refuse one that would unpack to more than this ("zip bomb")."""


class CvFileError(Exception):
    """Base class: this file can't be used as a CV. `code` is what the API sends back."""

    code = "cv_file_error"


class UnsupportedFileTypeError(CvFileError):
    """Not a PDF or a .docx file."""

    code = "unsupported_file_type"


class UnreadableFileError(CvFileError):
    """Looks like a PDF or .docx but is broken, password-protected or too big unpacked."""

    code = "file_unreadable"


class TooManyPagesError(CvFileError):
    """A PDF with more than MAX_PDF_PAGES pages."""

    code = "too_many_pages"


class NoTextFoundError(CvFileError):
    """The file opens but holds no text, e.g. a scanned paper CV (only pictures)."""

    code = "no_text_found"


@dataclass(frozen=True)
class CvFile:
    file_type: FileType
    text: str
    pages: int | None
    """Number of pages for a PDF; None for Word (a .docx has no fixed pages)."""


def read_cv(data: bytes) -> CvFile:
    file_type = detect_file_type(data)
    if file_type == "pdf":
        raw, pages = _read_pdf(data)
    else:
        raw, pages = _read_docx(data), None
    text = clean_text(raw)
    if not text:
        raise NoTextFoundError
    return CvFile(file_type=file_type, text=text, pages=pages)


def detect_file_type(data: bytes) -> FileType:
    """Decide the type from the first bytes ("magic numbers"), not from the name."""
    # The PDF standard allows a little junk before the header, hence "in", not startswith.
    if b"%PDF-" in data[:1024]:
        return "pdf"
    if data.startswith(b"PK\x03\x04"):  # a zip file: .docx, but also .xlsx, .odt, .zip...
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                names = archive.namelist()
                unzipped = sum(item.file_size for item in archive.infolist())
        except zipfile.BadZipFile:
            raise UnreadableFileError from None
        if "word/document.xml" not in names:
            raise UnsupportedFileTypeError
        if unzipped > MAX_UNZIPPED_BYTES:
            raise UnreadableFileError
        return "docx"
    raise UnsupportedFileTypeError


def _read_pdf(data: bytes) -> tuple[str, int]:
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted and not reader.decrypt(""):
            raise UnreadableFileError  # needs a password we don't have
        page_count = len(reader.pages)
        if page_count > MAX_PDF_PAGES:
            raise TooManyPagesError
        texts = [page.extract_text() or "" for page in reader.pages]
    except CvFileError:
        raise
    except Exception as error:
        # pypdf raises many kinds of errors on broken files; all mean "can't read it".
        # Log the kind only, never the content (it's someone's CV).
        logger.warning("could not read a PDF CV: %s", type(error).__name__)
        raise UnreadableFileError from error
    return "\n\n".join(texts), page_count


def _read_docx(data: bytes) -> str:
    try:
        document = Document(io.BytesIO(data))
        lines: list[str] = []
        for block in document.iter_inner_content():
            if isinstance(block, Table):
                lines.extend(_table_lines(block))
            else:
                lines.append(block.text)
    except Exception as error:
        logger.warning("could not read a Word CV: %s", type(error).__name__)
        raise UnreadableFileError from error
    return "\n".join(lines)


def _table_lines(table: Table) -> list[str]:
    """One line per row, cells separated by a tab. A merged cell appears once."""
    lines = []
    for row in table.rows:
        cells: list[str] = []
        for cell in row.cells:
            if cell.text not in cells:
                cells.append(cell.text)
        lines.append("\t".join(cells))
    return lines


_CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_SPACES = re.compile(r" {2,}")
_BLANK_LINES = re.compile(r"\n{3,}")


def clean_text(raw: str) -> str:
    """Tidy extracted text without changing its words:

    - NFKC: turns letter shapes some PDF makers store (Arabic presentation forms,
      the one-character "fi" ligature, non-breaking spaces) into the plain letters they stand for.
    - Removes control characters such as NUL (PostgreSQL can't store NUL in text).
    - Trims each line, squeezes runs of spaces, keeps at most one empty line in a row.
    """
    text = unicodedata.normalize("NFKC", raw).replace("\r\n", "\n").replace("\r", "\n")
    text = _CONTROL.sub("", text)
    lines = [_SPACES.sub(" ", line).strip() for line in text.split("\n")]
    return _BLANK_LINES.sub("\n\n", "\n".join(lines)).strip()
