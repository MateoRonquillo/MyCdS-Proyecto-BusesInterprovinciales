from collections import Counter

import pytest
from pwdlib import PasswordHash
from sqlalchemy import create_engine, select, func, event
from sqlalchemy.orm import Session

from app.db.database import Base
from app.db.seed import run_seed, cedula_demo, DEMO_PASSWORD
from app.models.core_models import Usuario, Cooperativa, Frecuencia, Reserva, Pago, Boleto, Abordaje, OcupacionAsiento, Ruta
from app.services.operacion import cedula_valida


@pytest.fixture
def db():
    engine = create_engine('sqlite://')
    @event.listens_for(engine, 'connect')
    def foreign_keys(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')
    Base.metadata.create_all(engine)
    with Session(engine, autoflush=False) as session:
        yield session
    engine.dispose()


def test_datos_demo_roles_compras_y_repeticion_sin_sobrescribir(db):
    assert run_seed(db)['compras_nuevas'] == 9
    cliente = db.scalar(select(Usuario).where(Usuario.correo == 'cliente.demo@example.test'))
    assert PasswordHash.recommended().verify(DEMO_PASSWORD, cliente.password_hash)
    assert all(cedula_valida(cedula_demo(n)) for n in range(1, 8))
    assert {u.rol for u in db.scalars(select(Usuario))} == {'admin','cooperativa','oficinista','cliente','chofer','ayudante'}
    assert db.scalar(select(func.count()).select_from(Cooperativa)) == 3
    assert db.scalar(select(func.count()).select_from(Frecuencia)) == 6
    assert db.scalar(select(func.count()).select_from(Ruta)) == 4
    assert db.scalar(select(func.count()).select_from(Boleto)) == 4
    assert db.scalar(select(func.count()).select_from(Abordaje)) == 1
    assert Counter(db.scalars(select(Pago.estado))) == {'APROBADO':4,'PENDIENTE':1,'RECHAZADO':1}
    reserva = db.scalar(select(Reserva).where(Reserva.pasajero_nombre == 'DEMO: Pendiente de pago'))
    reserva.estado = 'CANCELADA'
    original_hash = cliente.password_hash
    cliente.nombre = 'Nombre editado durante la demo'
    db.commit()
    assert run_seed(db, 'Otra-clave-demo-2026!')['compras_nuevas'] == 0
    assert db.scalar(select(func.count()).select_from(Reserva)) == 9
    assert db.scalar(select(func.count()).select_from(Ruta)) == 4
    assert cliente.password_hash == original_hash
    assert cliente.nombre == 'Nombre editado durante la demo'
    assert reserva.estado == 'CANCELADA'


def test_seed_rechaza_cuentas_ajenas_y_claves_cortas(db):
    with pytest.raises(ValueError, match='12 caracteres'):
        run_seed(db, 'corta')
    db.add(Usuario(nombre='Cuenta existente', correo='admin.demo@example.test', cedula='9999999999', rol='cliente'))
    db.commit()
    with pytest.raises(ValueError, match='otro perfil'):
        run_seed(db)
    db.rollback()
    usuario = db.scalar(select(Usuario).where(Usuario.correo == 'admin.demo@example.test'))
    assert usuario.nombre == 'Cuenta existente' and usuario.rol == 'cliente'
