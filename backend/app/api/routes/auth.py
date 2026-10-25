from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security import create_access_token
from app.db.database import get_db
from app.models.core_models import Usuario
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.services.auth import authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, summary="Iniciar sesión")
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    user = authenticate_user(db, credentials.correo, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )
    return LoginResponse(
        access_token=create_access_token(str(user.id)),
        usuario=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse, summary="Obtener usuario actual")
def read_current_user(user: Usuario = Depends(get_current_user)) -> Usuario:
    return user