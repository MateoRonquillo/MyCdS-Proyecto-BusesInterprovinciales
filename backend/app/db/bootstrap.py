"""Crear cuentas por CLI; nunca provisionar contraseñas conocidas en producción."""
import argparse
import getpass
from sqlalchemy import select
from pwdlib import PasswordHash
from app.db.database import SessionLocal
from app.models.core_models import Usuario, Cooperativa
from app.core.roles import Role
from app.services.operacion import cedula_valida


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--nombre", required=True)
    p.add_argument("--correo", required=True)
    p.add_argument("--cedula", required=True)
    p.add_argument("--rol", choices=[r.value for r in Role], default="admin")
    p.add_argument("--cooperativa-id", type=int)
    a = p.parse_args()
    if not cedula_valida(a.cedula):
        p.error("Cédula inválida")
    password = getpass.getpass("Contraseña (mínimo 12 caracteres): ")
    if len(password) < 12 or password != getpass.getpass("Repetir contraseña: "):
        p.error("Las contraseñas no coinciden o son muy cortas")
    with SessionLocal() as db:
        if db.scalar(select(Usuario.id).where(Usuario.correo == a.correo.lower())):
            p.error("El correo ya existe")
        if a.rol in {"cooperativa", "chofer", "ayudante"} and not a.cooperativa_id:
            p.error("Este rol requiere --cooperativa-id")
        if a.cooperativa_id and not db.get(Cooperativa, a.cooperativa_id):
            p.error("Cooperativa inexistente")
        db.add(Usuario(nombre=a.nombre, correo=a.correo.lower(), cedula=a.cedula, rol=a.rol,
            cooperativa_id=a.cooperativa_id, password_hash=PasswordHash.recommended().hash(password)))
        db.commit()
    print("Cuenta creada")


if __name__ == "__main__":
    main()
