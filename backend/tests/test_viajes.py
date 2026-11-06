from datetime import date, time, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import create_app
from app.models.core_models import Bus, Cooperativa, Frecuencia, Reserva, Ruta, Usuario

DIA = (date.today() + timedelta(days=3)).isoformat()


@pytest.fixture
def viajes_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(autoflush=False, bind=engine)

    with test_session() as db:
        coop = Cooperativa(nombre="Flota Pelileo", color_principal="#FF5733")
        user = Usuario(nombre="Cliente", correo="c@test.com", cedula="1720000001", rol="cliente", activo=True)
        db.add_all([coop, user])
        db.commit()

        chico = Bus(placa="AAA-001", numero_disco="01", capacidad_asientos=3, cooperativa_id=coop.id, activo=True)
        grande = Bus(placa="AAA-002", numero_disco="02", capacidad_asientos=40, cooperativa_id=coop.id, activo=True)
        inactivo = Bus(placa="AAA-003", numero_disco="03", capacidad_asientos=40, cooperativa_id=coop.id, activo=False)
        ruta = Ruta(origen="Ambato", destino="Quito", duracion_estimada_horas=2.5, activo=True)
        db.add_all([chico, grande, inactivo, ruta])
        db.commit()

        temprano = Frecuencia(ruta_id=ruta.id, bus_id=chico.id, hora_salida=time(6, 30), precio=4.0, activo=True)
        tarde = Frecuencia(ruta_id=ruta.id, bus_id=grande.id, hora_salida=time(8, 0), precio=4.5, activo=True)
        fuera = Frecuencia(ruta_id=ruta.id, bus_id=inactivo.id, hora_salida=time(9, 0), precio=4.0, activo=True)
        db.add_all([temprano, tarde, fuera])
        db.commit()

        fecha = date.today() + timedelta(days=3)
        for asiento, estado in ((1, "PENDIENTE"), (2, "CONFIRMADA"), (3, "CANCELADA")):
            db.add(Reserva(usuario_id=user.id, frecuencia_id=temprano.id, fecha_viaje=fecha,
                           asiento=asiento, tipo_pasajero="GENERAL", precio=4.0, estado=estado))
        db.commit()

    def override_get_db():
        with test_session() as db:
            yield db

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client


def buscar(client, origen="Ambato", destino="Quito", fecha=DIA):
    return client.get("/api/v1/viajes", params={"origen": origen, "destino": destino, "fecha": fecha})


def test_busca_viajes_ordenados_por_hora(viajes_client: TestClient) -> None:
    response = buscar(viajes_client)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # el bus inactivo no aparece
    assert [v["hora_salida"] for v in data["items"]] == ["06:30", "08:00"]
    primero = data["items"][0]
    assert primero["hora_llegada"] == "09:00"
    assert primero["duracion_min"] == 150
    assert primero["precio"] == 4.0
    assert primero["cooperativa"]["nombre"] == "Flota Pelileo"


def test_busqueda_ignora_tildes_y_mayusculas(viajes_client: TestClient) -> None:
    response = buscar(viajes_client, origen="  ÁMBATO ", destino="quito")

    assert response.status_code == 200
    assert response.json()["total"] == 2


def test_asientos_disponibles_descuentan_reservas_activas(viajes_client: TestClient) -> None:
    items = buscar(viajes_client).json()["items"]

    # Bus de 3 asientos: 1 pendiente + 1 confirmada ocupan; la cancelada no cuenta
    assert items[0]["asientos_disponibles"] == 1
    assert items[1]["asientos_disponibles"] == 40


def test_otro_dia_no_tiene_reservas(viajes_client: TestClient) -> None:
    otro_dia = (date.today() + timedelta(days=4)).isoformat()

    items = buscar(viajes_client, fecha=otro_dia).json()["items"]

    assert items[0]["asientos_disponibles"] == 3


def test_ruta_sin_viajes_devuelve_lista_vacia(viajes_client: TestClient) -> None:
    response = buscar(viajes_client, origen="Quito", destino="Ambato")

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}


def test_rechaza_fecha_pasada(viajes_client: TestClient) -> None:
    ayer = (date.today() - timedelta(days=1)).isoformat()

    assert buscar(viajes_client, fecha=ayer).status_code == 422


def test_exige_origen_destino_y_fecha(viajes_client: TestClient) -> None:
    assert viajes_client.get("/api/v1/viajes").status_code == 422