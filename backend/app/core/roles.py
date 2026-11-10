from enum import StrEnum


class Role(StrEnum):
    ADMINISTRADOR = "admin"
    USUARIO_COOPERATIVA = "cooperativa"
    OFICINISTA = "oficinista"
    CLIENTE = "cliente"
    CHOFER = "chofer"
    AYUDANTE = "ayudante"


ROLE_ALIASES = {
    "administrador": Role.ADMINISTRADOR.value,
    "administrator": Role.ADMINISTRADOR.value,
    "usuario_cooperativa": Role.USUARIO_COOPERATIVA.value,
    "usuario": Role.CLIENTE.value,
}


def normalize_role(role: str | Role) -> str:
    normalized = str(role).strip().lower()
    return ROLE_ALIASES.get(normalized, normalized)