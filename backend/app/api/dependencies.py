from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.roles import Role, normalize_role
from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.core_models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        user_id = int(subject) if isinstance(subject, str) else None
    except (InvalidTokenError, TypeError, ValueError):
        raise unauthorized from None

    if user_id is None:
        raise unauthorized

    user = db.get(Usuario, user_id)
    if user is None or not user.activo:
        raise unauthorized
    return user


def require_roles(*roles: str | Role) -> Callable[..., Usuario]:
    allowed_roles = {normalize_role(role) for role in roles}

    def role_dependency(user: Usuario = Depends(get_current_user)) -> Usuario:
        if normalize_role(user.rol) not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return role_dependency