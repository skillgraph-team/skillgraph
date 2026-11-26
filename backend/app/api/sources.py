"""Sources: things we read skills from (M3.5: CV upload). GitHub import: app/api/github.py.

GET    /sources       → 200 the user's sources, newest first (M3.7). A summary only: no
                        text or details, which can be large; `url` is a repo's GitHub page
POST   /sources/cv    form field `file` (PDF or .docx) → 201 the new source, with its text
DELETE /sources/{id}  → 204; a CV's file is deleted too (M3.7). 404 `not_found` for an id
                        that isn't the user's

Errors (body `{"detail": {"code": ...}}`):
- 413 `file_too_large`: bigger than the CV_MAX_BYTES setting (default 5 MB)
- 415 `unsupported_file_type`: not a PDF or .docx (the bytes are checked, not the name)
- 422 `file_unreadable`: broken or password-protected file
- 422 `too_many_pages`: a PDF with more pages than a CV has
- 422 `no_text_found`: no text in it, e.g. a scanned paper CV
- 422 (FastAPI's own validation error): no `file` field sent

How the file is read and stored: app/services/cv_uploads.py.
"""

import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict

from app.api.current_user import CurrentUser
from app.config import Settings, get_settings
from app.db.models import Source
from app.db.session import DbSession
from app.ingestion.cv_text import CvFileError, UnsupportedFileTypeError
from app.services import cv_uploads
from app.services import sources as source_service

router = APIRouter(prefix="/sources", tags=["sources"])


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    kind: str
    title: str
    language: str | None
    text: str | None
    details: dict[str, Any]
    created_at: datetime


class SourceSummary(BaseModel):
    id: uuid.UUID
    kind: str
    title: str
    language: str | None
    url: str | None
    created_at: datetime


def _summary(source: Source) -> SourceSummary:
    url = source.details.get("html_url")
    return SourceSummary(
        id=source.id,
        kind=source.kind,
        title=source.title,
        language=source.language,
        url=url if isinstance(url, str) else None,
        created_at=source.created_at,
    )


def _error(status_code: int, code: str) -> HTTPException:
    return HTTPException(status_code, detail={"code": code})


@router.post("/cv", status_code=status.HTTP_201_CREATED)
def upload_cv(
    file: UploadFile,
    user: CurrentUser,
    session: DbSession,
    settings: Annotated[Settings, Depends(get_settings)],
) -> SourceOut:
    # Read one byte more than allowed: if we get it, the file is too big.
    data = file.file.read(settings.cv_max_bytes + 1)
    if len(data) > settings.cv_max_bytes:
        raise _error(status.HTTP_413_CONTENT_TOO_LARGE, "file_too_large")
    try:
        source = cv_uploads.upload_cv(
            session, user, filename=file.filename, data=data, upload_dir=settings.upload_dir
        )
    except UnsupportedFileTypeError as error:
        raise _error(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, error.code) from None
    except CvFileError as error:
        raise _error(status.HTTP_422_UNPROCESSABLE_CONTENT, error.code) from None
    session.commit()
    return SourceOut.model_validate(source)


@router.get("")
def list_sources(user: CurrentUser, session: DbSession) -> list[SourceSummary]:
    return [_summary(source) for source in source_service.list_sources(session, user)]


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    try:
        source_service.delete_source(session, user, source_id, upload_dir=settings.upload_dir)
    except source_service.SourceNotFoundError:
        raise _error(status.HTTP_404_NOT_FOUND, "not_found") from None
    session.commit()
