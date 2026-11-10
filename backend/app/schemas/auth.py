from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    correo: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    correo: str
    cedula: str
    rol: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UserResponse

from pydantic import Field, field_validator
from app.services.operacion import cedula_valida


class RegistroRequest(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    correo: str = Field(min_length=5, max_length=100, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    cedula: str = Field(min_length=10, max_length=10)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("cedula")
    @classmethod
    def validar_cedula(cls, value):
        if not cedula_valida(value):
            raise ValueError("Cédula ecuatoriana inválida")
        return value
