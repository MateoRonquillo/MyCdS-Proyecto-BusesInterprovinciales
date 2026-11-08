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
def comprobante_pago():
    import base64
    from io import BytesIO
    from PIL import Image
    imagen = BytesIO()
    Image.new("RGB", (2, 2), "white").save(imagen, format="PNG")
    return "data:image/png;base64," + base64.b64encode(imagen.getvalue()).decode()


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

def test_historial_compras_retorna_datos_completos(reserva_client: TestClient):
    fecha = (date.today() + timedelta(days=5)).isoformat()
    reserva_client.post(
        "/api/v1/reservas",
        json={"frecuencia_id": 1, "fecha_viaje": fecha, "asiento": 7, "tipo_pasajero": "GENERAL"},
    )

    resp = reserva_client.get("/api/v1/reservas/historial")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    item = next(i for i in items if i["asiento"] == 7)
    assert item["cooperativa"] == "Coop Express"
    assert item["origen"] == "Quito"
    assert item["destino"] == "Guayaquil"
    assert item["estado"] == "PENDIENTE"


def test_consistencia_transicion_estados_reserva(reserva_client: TestClient):
    fecha = (date.today() + timedelta(days=6)).isoformat()
    creada = reserva_client.post(
        "/api/v1/reservas",
        json={"frecuencia_id": 1, "fecha_viaje": fecha, "asiento": 8, "tipo_pasajero": "GENERAL"},
    )
    res_id = creada.json()["id"]

    # Simular usuario administrador para actualizar estado
    app = reserva_client.app
    original_user = app.dependency_overrides[get_current_user]

    def admin_user():
        return Usuario(id=1, nombre="Admin", correo="admin@test.com", cedula="1111111111", rol="admin", activo=True)

    try:
        app.dependency_overrides[get_current_user] = admin_user

        # 1. Una reserva no puede pagarse al margen del registro de pagos
        ok_resp = reserva_client.patch(f"/api/v1/reservas/{res_id}/estado", json={"estado": "PAGADA"})
        assert ok_resp.status_code == 409
        assert "aprobación de pagos" in ok_resp.json()["error"]["message"]

        # 2. Cancelar la reserva
        cancel_resp = reserva_client.patch(f"/api/v1/reservas/{res_id}/estado", json={"estado": "CANCELADA"})
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["estado"] == "CANCELADA"

        # 3. Transición inválida: de CANCELADA no se puede volver a PAGADA -> 409 Conflict
        fail_resp = reserva_client.patch(f"/api/v1/reservas/{res_id}/estado", json={"estado": "PAGADA"})
        assert fail_resp.status_code == 409
        assert "Transición de estado inválida" in fail_resp.json()["error"]["message"]
    finally:
        app.dependency_overrides[get_current_user] = original_user


def test_no_permite_pagar_reserva_vencida_y_la_marca_expirada(reserva_client: TestClient):
    from app.models.core_models import Reserva

    # 1. Crear una reserva con fecha vencida directamente en la base de datos
    app = reserva_client.app
    admin_user = Usuario(id=1, nombre="Admin", correo="admin@test.com", cedula="1111111111", rol="admin", activo=True)
    app.dependency_overrides[get_current_user] = lambda: admin_user

    # Obtener sesión para insertar reserva vencida
    get_db_override = app.dependency_overrides[get_db]
    db = next(get_db_override())
    reserva_vencida = Reserva(
        usuario_id=1,
        frecuencia_id=1,
        fecha_viaje=date.today() - timedelta(days=1),
        asiento=9,
        tipo_pasajero="GENERAL",
        precio=12.50,
        estado="PENDIENTE",
    )
    db.add(reserva_vencida)
    db.commit()
    db.refresh(reserva_vencida)
    res_id = reserva_vencida.id

    # 2. Intentar pasar la reserva de PENDIENTE a PAGADA directamente -> debe rechazar con 409
    resp = reserva_client.patch(f"/api/v1/reservas/{res_id}/estado", json={"estado": "PAGADA"})
    assert resp.status_code == 409
    assert "ha expirado" in resp.json()["error"]["message"]

    # 3. Comprobar que en base de datos quedó actualizada como EXPIRADA
    db.refresh(reserva_vencida)
    assert reserva_vencida.estado == "EXPIRADA"


def test_pago_pendiente_no_genera_qr(reserva_client, comprobante_pago):
    fecha = (date.today() + timedelta(days=7)).isoformat()

    # Crear una reserva
    reserva = reserva_client.post("/api/v1/reservas", json={
        "frecuencia_id": 1,
        "fecha_viaje": fecha,
        "asiento": 1,
        "tipo_pasajero": "GENERAL"
    })
    assert reserva.status_code == 201

    # Registrar un pago
    pago = reserva_client.post("/api/v1/pagos", json={
        "reserva_id": reserva.json()["id"],
        "metodo_pago": "TRANSFERENCIA",
        "referencia": "PRUEBA-INTEGRACION",
        "comprobante": comprobante_pago,
        "monto": 12.50
    })
    assert pago.status_code == 201
    assert pago.json()["estado"] == "PENDIENTE"

    # El cliente no puede aprobar el pago
    aprobar = reserva_client.post(
        f"/api/v1/pagos/{pago.json()['id']}/aprobar"
    )
    assert aprobar.status_code == 403

    # No se puede descargar el QR sin aprobar el pago
    qr = reserva_client.get(
        f"/api/v1/boletos/{reserva.json()['id']}/qr"
    )
    assert qr.status_code == 409


def test_pago_aprobado_genera_qr(reserva_client, comprobante_pago):
    fecha = (date.today() + timedelta(days=7)).isoformat()

    # Crear reserva y pago
    reserva = reserva_client.post("/api/v1/reservas", json={
        "frecuencia_id": 1,
        "fecha_viaje": fecha,
        "asiento": 2,
        "tipo_pasajero": "GENERAL"
    })
    assert reserva.status_code == 201

    pago = reserva_client.post("/api/v1/pagos", json={
        "reserva_id": reserva.json()["id"],
        "metodo_pago": "TRANSFERENCIA",
        "referencia": "PRUEBA-INTEGRACION",
        "comprobante": comprobante_pago,
        "monto": 12.50
    })
    assert pago.status_code == 201

    # Simular un oficinista
    app = reserva_client.app
    anterior = app.dependency_overrides[get_current_user]

    def oficinista():
        return Usuario(
            id=1, nombre="Oficinista",
            correo="oficina@test.com",
            cedula="1234567890",
            rol="oficinista",
            activo=True
        )

    try:
        app.dependency_overrides[get_current_user] = oficinista

        # Aprobar el pago
        aprobado = reserva_client.post(
            f"/api/v1/pagos/{pago.json()['id']}/aprobar"
        )
        assert aprobado.status_code == 200
        assert aprobado.json()["estado"] == "APROBADO"
    finally:
        app.dependency_overrides[get_current_user] = anterior

    # Descargar el QR como cliente
    qr = reserva_client.get(
        f"/api/v1/boletos/{reserva.json()['id']}/qr"
    )
    assert qr.status_code == 200
    assert qr.headers["content-type"] == "image/png"



def test_pago_con_monto_incorrecto(reserva_client, comprobante_pago):
    fecha = (date.today() + timedelta(days=7)).isoformat()

    # Crear una reserva de $12.50
    reserva = reserva_client.post("/api/v1/reservas", json={
        "frecuencia_id": 1,
        "fecha_viaje": fecha,
        "asiento": 3,
        "tipo_pasajero": "GENERAL"
    })
    assert reserva.status_code == 201

    # Intentar pagar solo $10
    pago = reserva_client.post("/api/v1/pagos", json={
        "reserva_id": reserva.json()["id"],
        "metodo_pago": "TRANSFERENCIA",
        "referencia": "PRUEBA-INTEGRACION",
        "comprobante": comprobante_pago,
        "monto": 10.00
    })

    # El sistema debe rechazar el monto
    assert pago.status_code == 422


def test_no_permite_pago_duplicado(reserva_client, comprobante_pago):
    fecha = (date.today() + timedelta(days=8)).isoformat()

    # Crear reserva
    reserva = reserva_client.post("/api/v1/reservas", json={
        "frecuencia_id": 1,
        "fecha_viaje": fecha,
        "asiento": 4,
        "tipo_pasajero": "GENERAL"
    })
    assert reserva.status_code == 201

    # Datos del pago
    datos = {
        "reserva_id": reserva.json()["id"],
        "metodo_pago": "TRANSFERENCIA",
        "referencia": "PRUEBA-INTEGRACION",
        "comprobante": comprobante_pago,
        "monto": 12.50
    }

    # Primer pago: correcto
    primero = reserva_client.post("/api/v1/pagos", json=datos)
    assert primero.status_code == 201

    # Segundo pago: debe rechazarse
    segundo = reserva_client.post("/api/v1/pagos", json=datos)
    assert segundo.status_code == 409


def test_rechazo_de_pago(reserva_client, comprobante_pago):
    fecha = (date.today() + timedelta(days=9)).isoformat()

    # Crear reserva
    reserva = reserva_client.post("/api/v1/reservas", json={
        "frecuencia_id": 1,
        "fecha_viaje": fecha,
        "asiento": 5,
        "tipo_pasajero": "GENERAL"
    })
    assert reserva.status_code == 201
    reserva_id = reserva.json()["id"]

    # Registrar pago
    pago = reserva_client.post("/api/v1/pagos", json={
        "reserva_id": reserva_id,
        "metodo_pago": "TRANSFERENCIA",
        "referencia": "PRUEBA-INTEGRACION",
        "comprobante": comprobante_pago,
        "monto": 12.50
    })
    assert pago.status_code == 201

    # Simular un oficinista
    app = reserva_client.app
    anterior = app.dependency_overrides[get_current_user]

    def oficinista():
        return Usuario(
            id=1, nombre="Oficinista",
            correo="oficina@test.com",
            cedula="1234567890",
            rol="oficinista",
            activo=True
        )

    try:
        app.dependency_overrides[get_current_user] = oficinista

        # Rechazar pago
        rechazo = reserva_client.post(
            f"/api/v1/pagos/{pago.json()['id']}/rechazar",
            json={"motivo": "Comprobante incorrecto"}
        )
        assert rechazo.status_code == 200
        assert rechazo.json()["estado"] == "RECHAZADO"
    finally:
        app.dependency_overrides[get_current_user] = anterior

    # La reserva vuelve a pendiente
    consulta = reserva_client.get(f"/api/v1/reservas/{reserva_id}")
    assert consulta.status_code == 200
    assert consulta.json()["estado"] == "PENDIENTE"

    # El QR sigue bloqueado
    qr = reserva_client.get(f"/api/v1/boletos/{reserva_id}/qr")
    assert qr.status_code == 409


def test_asiento_expirado_queda_disponible_para_nueva_reserva(reserva_client: TestClient):
    from app.models.core_models import Reserva

    app = reserva_client.app
    get_db_override = app.dependency_overrides[get_db]
    db = next(get_db_override())

    fecha = (date.today() + timedelta(days=7)).isoformat()

    # 1. Crear reserva expirada directamente en el asiento 10
    reserva_exp = Reserva(
        usuario_id=1,
        frecuencia_id=1,
        fecha_viaje=date.today() + timedelta(days=7),
        asiento=10,
        tipo_pasajero="GENERAL",
        precio=12.50,
        estado="EXPIRADA",
    )
    db.add(reserva_exp)
    db.commit()

    # 2. El mapa de disponibilidad debe mostrar el asiento 10 disponible
    disp = reserva_client.get(f"/api/v1/reservas/disponibilidad/1?fecha={fecha}")
    assert disp.status_code == 200
    assert 10 in disp.json()["asientos_disponibles"]
    assert 10 not in disp.json()["asientos_ocupados"]

    # 3. Debe permitir reservar nuevamente ese asiento 10 sin colisión
    nueva = reserva_client.post(
        "/api/v1/reservas",
        json={"frecuencia_id": 1, "fecha_viaje": fecha, "asiento": 10, "tipo_pasajero": "GENERAL"},
    )
    assert nueva.status_code == 201
    assert nueva.json()["asiento"] == 10


def test_transicion_pago_en_revision_consistente(reserva_client: TestClient, comprobante_pago):
    fecha = (date.today() + timedelta(days=8)).isoformat()
    creada = reserva_client.post(
        "/api/v1/reservas",
        json={"frecuencia_id": 1, "fecha_viaje": fecha, "asiento": 1, "tipo_pasajero": "GENERAL"},
    )
    res_id = creada.json()["id"]
    pago = reserva_client.post("/api/v1/pagos", json={"reserva_id": res_id, "metodo_pago": "TRANSFERENCIA", "referencia": "TRANSICION", "comprobante": comprobante_pago, "monto": 12.50})
    assert pago.status_code == 201

    app = reserva_client.app
    original_user = app.dependency_overrides[get_current_user]
    admin_user = Usuario(id=1, nombre="Admin", correo="admin@test.com", cedula="1111111111", rol="admin", activo=True)

    try:
        app.dependency_overrides[get_current_user] = lambda: admin_user

        # Pasar a PAGO_EN_REVISION
        rev = reserva_client.patch(f"/api/v1/reservas/{res_id}/estado", json={"estado": "PAGO_EN_REVISION"})
        assert rev.status_code == 200
        assert rev.json()["estado"] == "PAGO_EN_REVISION"

        # El cambio directo no puede saltarse la aprobación del pago.
        conf = reserva_client.patch(f"/api/v1/reservas/{res_id}/estado", json={"estado": "CONFIRMADA"})
        assert conf.status_code == 409
        aprobado = reserva_client.post(f"/api/v1/pagos/{pago.json()['id']}/aprobar")
        assert aprobado.status_code == 200
        consulta = reserva_client.get(f"/api/v1/reservas/{res_id}")
        assert consulta.json()["estado"] == "CONFIRMADA"
    finally:
        app.dependency_overrides[get_current_user] = original_user

def test_cancelar_reserva_en_revision_sincroniza_pago_a_rechazado(reserva_client: TestClient, comprobante_pago):
    fecha = (date.today() + timedelta(days=9)).isoformat()

    # 1. Crear reserva
    creada = reserva_client.post(
        "/api/v1/reservas",
        json={"frecuencia_id": 1, "fecha_viaje": fecha, "asiento": 2, "tipo_pasajero": "GENERAL"},
    )
    assert creada.status_code == 201
    res_id = creada.json()["id"]

    # 2. Registrar pago -> la reserva pasa a PAGO_EN_REVISION y el pago a PENDIENTE
    pago_resp = reserva_client.post(
        "/api/v1/pagos",
        json={"reserva_id": res_id, "metodo_pago": "TRANSFERENCIA",
        "referencia": "PRUEBA-INTEGRACION",
        "comprobante": comprobante_pago, "monto": 12.50},
    )
    assert pago_resp.status_code == 201
    pago_id = pago_resp.json()["id"]

    # 3. Cancelar la reserva
    del_resp = reserva_client.delete(f"/api/v1/reservas/{res_id}")
    assert del_resp.status_code == 204

    # 4. Verificar que el pago asociado quedo sincronizado a RECHAZADO
    pago_check = reserva_client.get(f"/api/v1/pagos/{pago_id}")
    assert pago_check.status_code == 200
    assert pago_check.json()["estado"] == "RECHAZADO"
    assert "Cancelado por anulación" in pago_check.json()["motivo_rechazo"]
