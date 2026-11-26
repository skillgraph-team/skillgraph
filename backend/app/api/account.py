"""Deleting your account (M3.9).

POST /account/delete  {password} → 204, removes every row and file about the user and
                      logs them out

The password is asked again so that a login left open on a shared computer, or a
mistaken click, can't delete an account. Errors: 403 `wrong_password`; 401 without a
login. What is removed and in which order: app/services/accounts.py.

POST rather than DELETE: a request body (the password) on DELETE is ignored by some
browsers' tools and proxies.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.current_user import CurrentUser
from app.auth.cookies import clear_login_cookie
from app.config import Settings, get_settings
from app.db.session import DbSession
from app.services.accounts import WrongPasswordError, delete_account

router = APIRouter(prefix="/account", tags=["account"])


class DeleteAccountRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    password: Annotated[str, Field(max_length=128)]


@router.post("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    body: DeleteAccountRequest,
    user: CurrentUser,
    session: DbSession,
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    try:
        delete_account(
            session,
            user,
            password=body.password,
            upload_dir=settings.upload_dir,
            github_cache_dir=settings.github_cache_dir,
        )
    except WrongPasswordError:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail={"code": "wrong_password"}) from None
    session.commit()
    clear_login_cookie(response)
