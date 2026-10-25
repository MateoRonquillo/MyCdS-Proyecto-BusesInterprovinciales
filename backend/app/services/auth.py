from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.core_models import Usuario

password_hash = PasswordHash.recommended()


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(password, hashed_password)
    except (TypeError, ValueError):
        return False


def authenticate_user(db: Session, correo: str, password: str) -> Usuario | None:
    user = db.scalar(select(Usuario).where(Usuario.correo == correo))
    if (
        user is None
        or not user.activo
        or user.password_hash is None
        or not verify_password(password, user.password_hash)
    ):
        return None
    return user