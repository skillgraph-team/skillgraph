"""Password hashing with argon2 (via pwdlib). Passwords are never stored or logged as text.

`verify_dummy()` does the same work as a real check, so a login for an unknown email
takes as long as one with a wrong password (nobody can time which emails exist).
"""

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

_hasher = PasswordHash((Argon2Hasher(),))
_DUMMY_HASH = _hasher.hash("dummy password used to equalise login timing")


def hash_password(password: str) -> str:
    """An argon2id hash (`$argon2id$...`) with a random salt."""
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _hasher.verify(password, password_hash)


def verify_dummy(password: str) -> None:
    """Spend the time of a password check, for logins with an unknown email."""
    _hasher.verify(password, _DUMMY_HASH)
