"""CV uploads (M3.5): read the file, then keep its text, language and the file itself.

`upload_cv` does it in this order, so a bad file leaves nothing behind:
1. read the text (`app.ingestion.cv_text`); a bad file raises a `CvFileError` here,
   before anything is saved;
2. guess the language (`app.ingestion.language`);
3. add the `sources` row (kind `cv`), then write the file to
   `<upload_dir>/<user id>/<source id>.<pdf|docx>`.

The file is named after the source id, never after the name the browser sent, so a
name like `../../x.pdf` can't choose where it goes. The sent name is only the title.

Each upload is a new source; earlier CVs are kept (T-087). Like the other services this
flushes but never commits; the endpoint commits.
"""

import re
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import Source, User
from app.ingestion.cv_text import read_cv
from app.ingestion.language import detect_language

TITLE_MAX_CHARS = 200
DEFAULT_TITLE = "cv"


def upload_cv(
    session: Session, user: User, *, filename: str | None, data: bytes, upload_dir: Path
) -> Source:
    cv = read_cv(data)
    source = Source(
        user_id=user.id,
        kind="cv",
        title=file_title(filename),
        language=detect_language(cv.text),
        text=cv.text,
        details={"file_type": cv.file_type, "size_bytes": len(data), "pages": cv.pages},
    )
    session.add(source)
    session.flush()  # gives the source its id, used as the file name

    relative = f"{user.id}/{source.id}.{cv.file_type}"
    path = upload_dir / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    source.storage_path = relative
    session.flush()
    return source


def file_title(filename: str | None) -> str:
    """The last part of the name the browser sent (without any folders), shortened."""
    name = re.split(r"[\\/]", filename or "")[-1].strip()
    return name[:TITLE_MAX_CHARS] or DEFAULT_TITLE
