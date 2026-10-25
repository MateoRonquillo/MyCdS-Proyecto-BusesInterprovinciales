import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import create_app
from app.models.core_models import Usuario
from app.core.roles import Role
from app.api.dependencies import require_roles


@pytest.fixture
def auth_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-with-at-least-32-characters")
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(autoflush=False, bind=engine)
    password_hash = PasswordHash.recommended().hash("correct-password")
    with test_session() as db:
        db.add_all(
            [
                Usuario(
                    nombre="Cliente de prueba",
                    correo="cliente@example.com",
                    cedula="1234567890",
                    rol="cliente",
                    password_hash=password_hash,
                ),
                Usuario(
                    nombre="Cuenta inactiva",
                    correo="inactivo@example.com",
                    cedula="0987654321",
                    rol="cliente",
                    activo=False,
                    password_hash=password_hash,
                ),
                Usuario(
                    nombre="Administrador de prueba",
                    correo="admin@example.com",
                    cedula="1111111111",
                    rol="admin",
                    password_hash=password_hash,
                ),
            ]
        )
        db.commit()

    application = create_app()

    def override_get_db():
        with test_session() as db:
            yield db

    application.dependency_overrides[get_db] = override_get_db
    return TestClient(application)


def test_login_returns_jwt_and_profile(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/v1/auth/login",
        json={"correo": "cliente@example.com", "password": "correct-password"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["usuario"] == {
        "id": 1,
        "nombre": "Cliente de prueba",
        "correo": "cliente@example.com",
        "rol": "cliente",
    }
    token = response.json()["access_token"]
    profile = auth_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert profile.status_code == 200
    assert profile.json()["correo"] == "cliente@example.com"


def test_current_user_requires_valid_bearer_token(auth_client: TestClient) -> None:
    missing_token = auth_client.get("/api/v1/auth/me")
    invalid_token = auth_client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid"}
    )

    assert missing_token.status_code == 401
    assert invalid_token.status_code == 401


def test_role_dependency_grants_and_denies_access(auth_client: TestClient) -> None:
    @auth_client.app.get("/test/admin")
    def admin_endpoint(
        user: Usuario = Depends(require_roles(Role.ADMINISTRADOR)),
    ) -> dict[str, str]:
        return {"role": user.rol}

    client_login = auth_client.post(
        "/api/v1/auth/login",
        json={"correo": "cliente@example.com", "password": "correct-password"},
    )
    admin_login = auth_client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@example.com", "password": "correct-password"},
    )

    denied = auth_client.get(
        "/test/admin",
        headers={"Authorization": f"Bearer {client_login.json()['access_token']}"},
    )
    allowed = auth_client.get(
        "/test/admin",
        headers={"Authorization": f"Bearer {admin_login.json()['access_token']}"},
    )

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json() == {"role": "admin"}


@pytest.mark.parametrize(
    "input_role,expected_role",
    [
        ("administrador", Role.ADMINISTRADOR.value),
        ("usuario_cooperativa", Role.USUARIO_COOPERATIVA.value),
        ("usuario", Role.CLIENTE.value),
        ("admin", Role.ADMINISTRADOR.value),
    ],
)
def test_role_aliases_are_normalized(input_role: str, expected_role: str) -> None:
    from app.core.roles import normalize_role

    assert normalize_role(input_role) == expected_role


@pytest.mark.parametrize(
    "correo,password",
    [
        ("cliente@example.com", "wrong-password"),
        ("missing@example.com", "correct-password"),
        ("inactivo@example.com", "correct-password"),
    ],
)
def test_login_rejects_invalid_credentials(
    auth_client: TestClient,
    correo: str,
    password: str,
) -> None:
    response = auth_client.post(
        "/api/v1/auth/login",
        json={"correo": correo, "password": password},
    )

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Correo o contraseña incorrectos"