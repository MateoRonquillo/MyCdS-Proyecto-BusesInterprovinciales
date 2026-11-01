from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import create_app
from app.models.core_models import Bus, Cooperativa, Frecuencia, Ruta, Usuario
from app.api.dependencies import get_current_user


@pytest.fixture
def reserva_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(autoflush=False, bind=engine)

    with test_session() as db:
        user = Usuario(
            nombre="Pasajero Test",
            correo="pasajero@test.com",
            cedula="1720000001",
            rol="cliente",
            activo=True,
        )
        coop = Cooperativa(nombre="Coop Express")
        db.add_all([user, coop])
        db.commit()
        db.refresh(coop)

        bus = Bus(
            placa="PBA-1234",
            numero_disco="05",
            capacidad_asientos=10,
            cooperativa_id=coop.id,
            activo=True,
        )
        ruta = Ruta(origen="Quito", destino="Guayaquil", duracion_estimada_horas=8.0)
        db.add_all([bus, ruta])
        db.commit()
        db.refresh(bus)
        db.refresh(ruta)

        from datetime import time
        frecuencia = Frecuencia(
            ruta_id=ruta.id,
            bus_id=bus.id,
            hora_salida=time(10, 0),
            precio=12.50,
            activo=True,
        )
        db.add(frecuencia)
        db.commit()

    application = create_app()

    def override_get_db():
        with test_session() as db:
            yield db

    def override_current_user():
        with test_session() as db:
            return db.get(Usuario, 1)

    application.dependency_overrides[get_db] = override_get_db
    application.dependency_overrides[get_current_user] = override_current_user

    return TestClient(application)


def test_disponibilidad_y_prevencion_doble_asignacion_asiento(reserva_client: TestClient):
    fecha_futura = (date.today() + timedelta(days=2)).isoformat()

    # 1. Comprobar disponibilidad inicial: 10 asientos libres
    disp_resp = reserva_client.get(f"/api/v1/reservas/disponibilidad/1?fecha={fecha_futura}")
    assert disp_resp.status_code == 200
    data = disp_resp.json()
    assert data["capacidad_total"] == 10
    assert len(data["asientos_disponibles"]) == 10
    assert data["asientos_ocupados"] == []

    # 2. Reservar el asiento 4 exitosamente
    res_payload = {
        "frecuencia_id": 1,
        "fecha_viaje": fecha_futura,
        "asiento": 4,
        "tipo_pasajero": "GENERAL",
    }
    create_resp = reserva_client.post("/api/v1/reservas", json=res_payload)
    assert create_resp.status_code == 201
    assert create_resp.json()["asiento"] == 4

    # 3. Intentar reservar el MISMO asiento 4 para el mismo viaje -> debe fallar con 409
    dup_resp = reserva_client.post("/api/v1/reservas", json=res_payload)
    assert dup_resp.status_code == 409
    assert "El asiento ya está reservado" in dup_resp.json()["error"]["message"]

    # 4. Verificar que disponibilidad ahora muestra el asiento 4 como ocupado
    disp_after = reserva_client.get(f"/api/v1/reservas/disponibilidad/1?fecha={fecha_futura}")
    assert disp_after.status_code == 200
    data_after = disp_after.json()
    assert 4 in data_after["asientos_ocupados"]
    assert 4 not in data_after["asientos_disponibles"]

def test_asiento_cancelado_puede_reservarse_nuevamente(
    reserva_client: TestClient,
):
    fecha = (date.today() + timedelta(days=3)).isoformat()

    payload = {
        "frecuencia_id": 1,
        "fecha_viaje": fecha,
        "asiento": 5,
        "tipo_pasajero": "GENERAL",
    }

    primera = reserva_client.post(
        "/api/v1/reservas", json=payload
    )
    assert primera.status_code == 201

    reserva_id = primera.json()["id"]

    cancelacion = reserva_client.delete(
        f"/api/v1/reservas/{reserva_id}"
    )
    assert cancelacion.status_code == 204

    disponibilidad = reserva_client.get(
        f"/api/v1/reservas/disponibilidad/1?fecha={fecha}"
    )
    assert disponibilidad.status_code == 200
    assert 5 in disponibilidad.json()["asientos_disponibles"]

    segunda = reserva_client.post(
        "/api/v1/reservas", json=payload
    )
    assert segunda.status_code == 201


def test_calculo_tarifas_general_y_preferencial(
    reserva_client: TestClient,
):
    general = reserva_client.post(
        "/api/v1/tarifas/calcular",
        json={
            "frecuencia_id": 1,
            "cantidad_pasajeros": 2,
        },
    )

    assert general.status_code == 200
    assert general.json()["subtotal"] == 25.00
    assert general.json()["total"] == 25.00
    assert general.json()["descuento_total"] == 0

    preferencial = reserva_client.post(
        "/api/v1/tarifas/calcular",
        json={
            "frecuencia_id": 1,
            "tipos_pasajero": [
                "GENERAL",
                "ADULTO_MAYOR",
            ],
        },
    )

    assert preferencial.status_code == 200
    assert preferencial.json()["subtotal"] == 25.00
    assert preferencial.json()["descuento_total"] == 6.25
    assert preferencial.json()["total"] == 18.75


def test_cliente_no_puede_consultar_reserva_ajena(
    reserva_client: TestClient,
):
    from app.models.core_models import Reserva

    fecha = (date.today() + timedelta(days=4)).isoformat()

    respuesta = reserva_client.post(
        "/api/v1/reservas",
        json={
            "frecuencia_id": 1,
            "fecha_viaje": fecha,
            "asiento": 6,
            "tipo_pasajero": "GENERAL",
        },
    )

    assert respuesta.status_code == 201
    reserva_id = respuesta.json()["id"]

    def otro_usuario():
        return Usuario(
            id=999,
            nombre="Otro cliente",
            correo="otro@test.com",
            cedula="9999999999",
            rol="cliente",
            activo=True,
        )

    app = reserva_client.app
    anterior = app.dependency_overrides[get_current_user]

    try:
        app.dependency_overrides[get_current_user] = otro_usuario

        consulta = reserva_client.get(
            f"/api/v1/reservas/{reserva_id}"
        )

        assert consulta.status_code == 403
    finally:
        app.dependency_overrides[get_current_user] = anterior
