"""Regresiones de los flujos de la release; MySQL opcional con TEST_DATABASE_URL."""
import base64
import os
from datetime import time, timedelta
from io import BytesIO

import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user
from app.db.database import Base, get_db
from app.main import create_app
from app.models.core_models import Abordaje, Boleto, Bus, Cooperativa, Frecuencia, Parada, Reserva, Ruta, Usuario
from app.services.operacion import hoy


@pytest.fixture
def entorno():
    url = os.getenv("TEST_DATABASE_URL", "sqlite://")
    if not url.startswith('sqlite'):
        from sqlalchemy.engine import make_url
        nombre = make_url(url).database or ''
        if not nombre.endswith(('_integration_test', '_release_test')):
            pytest.fail('TEST_DATABASE_URL debe señalar una base desechable con sufijo _integration_test o _release_test')
    engine = create_engine(url, **({"connect_args": {"check_same_thread": False}, "poolclass": StaticPool} if url.startswith("sqlite") else {}))
    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def fk_on(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(engine, autoflush=False)
    with sessions() as db:
        db.add_all([Cooperativa(id=1, nombre="Cooperativa A"), Cooperativa(id=2, nombre="Cooperativa B")])
        db.commit()
        db.add_all([Usuario(id=1, nombre="Cliente", correo="cliente@test.ec", cedula="1710034065", rol="cliente"),
            Usuario(id=2, nombre="Oficinista", correo="oficina@test.ec", cedula="1710034066", rol="oficinista"),
            Usuario(id=3, nombre="Chofer", correo="chofer@test.ec", cedula="1710034067", rol="chofer", cooperativa_id=1),
            Usuario(id=4, nombre="Gestor", correo="gestor@test.ec", cedula="1710034068", rol="cooperativa", cooperativa_id=1),
            Usuario(id=5, nombre="Administrador", correo="admin@test.ec", cedula="1710034069", rol="admin")])
        db.add_all([Bus(id=1, placa="AAA-0001", numero_disco="1", cooperativa_id=1, capacidad_asientos=10, chasis="Volvo", carroceria="Prueba", asientos_vip="1,2"),
            Bus(id=2, placa="BBB-0002", numero_disco="2", cooperativa_id=2, capacidad_asientos=10)])
        db.add(Ruta(id=1, origen="Quito", destino="Cuenca", duracion_estimada_horas=8))
        db.commit()
        db.add(Parada(ruta_id=1, orden=1, ciudad="Latacunga", minutos=90, proporcion_tarifa=0.25))
        db.add(Frecuencia(id=1, ruta_id=1, bus_id=1, hora_salida=time(10), precio=20, resolucion_ant="TEST"))
        db.commit()
    app = create_app()
    estado = {"usuario": 1}
    def get_session():
        with sessions() as db:
            yield db
    def get_user():
        with sessions() as db:
            return db.get(Usuario, estado["usuario"])
    app.dependency_overrides[get_db] = get_session
    app.dependency_overrides[get_current_user] = get_user
    with TestClient(app) as client:
        yield client, sessions, estado
    Base.metadata.drop_all(engine)
    engine.dispose()


def reservar(c, **datos):
    return c.post('/api/v1/reservas', json={"frecuencia_id": 1, "fecha_viaje": str(hoy()), "asiento": 1,
        "pasajero_nombre": "Pasajero", "pasajero_cedula": "1710034065", **datos})


def imagen():
    out = BytesIO()
    Image.new("RGB", (10, 10), "white").save(out, "PNG")
    return "data:image/png;base64," + base64.b64encode(out.getvalue()).decode()


def test_tramos_no_superpuestos_y_cancelacion(entorno):
    c, sessions, estado = entorno
    uno = reservar(c, origen_orden=0, destino_orden=1)
    dos = reservar(c, origen_orden=1, destino_orden=2)
    assert uno.status_code == dos.status_code == 201
    assert uno.json()['precio'] == 5
    assert dos.json()['precio'] == 15
    assert reservar(c).status_code == 409
    consulta = c.get('/api/v1/reservas/disponibilidad/1', params={"fecha": str(hoy()), "origen_orden": 0, "destino_orden": 1}).json()
    assert consulta['asientos_ocupados'] == [1]
    assert consulta['mapa_asientos'][0]['tipo'] == 'VIP'
    assert c.delete(f"/api/v1/reservas/{uno.json()['id']}").status_code == 204
    assert reservar(c, origen_orden=0, destino_orden=1).status_code == 201
    history = c.get('/api/v1/reservas/historial').json()
    assert any(r['origen'] == 'Latacunga' and r['destino'] == 'Cuenca' for r in history)


def test_busqueda_tarifa_y_filtros_reales(entorno):
    c, _, _ = entorno
    params = dict(origen="Latacunga", destino="Cuenca", fecha=str(hoy()), tipo_asiento="VIP", chasis="volvo", tipo_viaje="CON_PARADAS")
    r = c.get('/api/v1/viajes', params=params)
    assert r.status_code == 200
    v = r.json()['items'][0]
    assert v['precio'] == 15 and v['asientos_disponibles'] == 2
    assert v['hora_salida'] == '11:30'
    assert c.get('/api/v1/viajes', params={**params, 'chasis':'inexistente'}).json()['total'] == 0
    tarifa = c.post('/api/v1/tarifas/calcular', json={"frecuencia_id":1,"origen_orden":1,"destino_orden":2,"cantidad_pasajeros":2}).json()
    assert tarifa['total'] == 30
    assert reservar(c, origen_orden=2, destino_orden=1).status_code == 422


def test_pago_revision_boleto_y_abordaje_unico(entorno):
    c, sessions, estado = entorno
    r = reservar(c).json()
    body = dict(reserva_id=r['id'], metodo_pago='TRANSFERENCIA', monto=20, referencia='REF-1', comprobante=imagen())
    pago = c.post('/api/v1/pagos', json=body)
    assert pago.status_code == 201, pago.text
    assert c.post('/api/v1/pagos', json=body).status_code == 409
    assert c.get(f"/api/v1/boletos/{r['id']}/qr").status_code == 409
    assert c.post(f"/api/v1/pagos/{pago.json()['id']}/aprobar").status_code == 403
    estado['usuario'] = 2
    assert c.get(f"/api/v1/pagos/{pago.json()['id']}/comprobante").json()['comprobante'] == imagen()
    assert c.post(f"/api/v1/pagos/{pago.json()['id']}/aprobar").status_code == 200
    assert c.post(f"/api/v1/pagos/{pago.json()['id']}/aprobar").status_code == 409
    estado['usuario'] = 1
    assert c.get(f"/api/v1/boletos/{r['id']}/qr").headers['content-type'] == 'image/png'
    html = c.get(f"/api/v1/boletos/{r['id']}/descarga")
    assert html.status_code == 200 and 'Quito' in html.text and 'Cuenca' in html.text
    with sessions() as db:
        codigo = db.scalar(select(Boleto.codigo).where(Boleto.reserva_id == r['id']))
    assert c.post('/api/v1/boletos/abordar', json={'codigo':codigo}).status_code == 403
    estado['usuario'] = 3
    assert c.post('/api/v1/boletos/abordar', json={'codigo':codigo}).status_code == 201
    assert c.post('/api/v1/boletos/abordar', json={'codigo':codigo}).status_code == 409
    with sessions() as db:
        assert len(list(db.scalars(select(Abordaje)))) == 1
    estado['usuario'] = 1
    assert any('Abordaje' in n['mensaje'] for n in c.get('/api/v1/notificaciones').json())


def test_comprobantes_invalidos_y_efectivo_restringido(entorno):
    c, _, _ = entorno
    r = reservar(c).json()
    body = dict(reserva_id=r['id'], metodo_pago='TRANSFERENCIA', monto=20, referencia='REF')
    assert c.post('/api/v1/pagos', json=body).status_code == 422
    assert c.post('/api/v1/pagos', json={**body, 'comprobante':'data:image/png;base64,AAAA'}).status_code == 422
    assert c.post('/api/v1/pagos', json={**body, 'metodo_pago':'EFECTIVO'}).status_code == 403
    assert c.post('/api/v1/pagos', json={**body, 'monto':1, 'comprobante':imagen()}).status_code == 422


def test_rechazo_reintento_y_descuento_con_revision(entorno):
    c, _, estado = entorno
    assert reservar(c, tipo_pasajero='ADULTO_MAYOR', pasajero_cedula='0000000000').status_code == 422
    r = reservar(c, tipo_pasajero='ADULTO_MAYOR').json()
    assert r['precio'] == 10
    body = dict(reserva_id=r['id'], metodo_pago='DEPOSITO', monto=10, referencia='DEP', comprobante=imagen())
    pago = c.post('/api/v1/pagos', json=body).json()
    estado['usuario'] = 2
    assert c.post(f"/api/v1/pagos/{pago['id']}/aprobar").status_code == 422
    assert c.post(f"/api/v1/pagos/{pago['id']}/rechazar", json={'motivo':'Comprobante ilegible'}).status_code == 200
    estado['usuario'] = 1
    nuevo = c.post('/api/v1/pagos', json=body).json()
    estado['usuario'] = 2
    assert c.post(f"/api/v1/pagos/{nuevo['id']}/aprobar", json={'descuento_verificado':True}).status_code == 200


def test_aislamiento_cooperativa_y_baja_logica(entorno):
    c, _, estado = entorno
    assert c.get('/api/v1/buses').status_code == 403
    estado['usuario'] = 4
    assert [b['id'] for b in c.get('/api/v1/buses').json()] == [1]
    assert c.delete('/api/v1/buses/2').status_code == 403
    assert c.post('/api/v1/frecuencias', json={'ruta_id':1,'bus_id':2,'hora_salida':'12:00','precio':20,'resolucion_ant':'TEST'}).status_code == 403
    assert c.put('/api/v1/configuracion', json={'nombre':'Ajeno','color_principal':'#000000'}).status_code == 403
    assert c.delete('/api/v1/buses/1').status_code == 204
    assert reservar(c).status_code in {403,409}


def test_hoja_trabajo_y_dia_parada(entorno):
    c, _, estado = entorno
    estado['usuario'] = 4
    jornada = c.post('/api/v1/jornadas', json={'fecha':str(hoy()),'bus_id':1,'frecuencia_id':None})
    assert jornada.status_code == 201
    assert c.post('/api/v1/jornadas', json={'fecha':str(hoy()),'bus_id':1,'frecuencia_id':1}).status_code == 409
    assert c.get('/api/v1/viajes', params={'origen':'Quito','destino':'Cuenca','fecha':str(hoy())}).json()['total'] == 0
    estado['usuario'] = 1
    assert reservar(c).status_code == 409
    estado['usuario'] = 4
    assert c.delete(f"/api/v1/jornadas/{jornada.json()['id']}").status_code == 204
    estado['usuario'] = 1
    assert reservar(c).status_code == 201
    estado['usuario'] = 4
    assert c.post('/api/v1/jornadas', json={'fecha':str(hoy()),'bus_id':1,'frecuencia_id':None}).status_code == 409


def test_boleto_ajeno_cooperativa_y_fecha(entorno):
    c, sessions, estado = entorno
    r = reservar(c).json()
    estado['usuario'] = 2
    p = c.post('/api/v1/pagos', json={'reserva_id':r['id'],'metodo_pago':'EFECTIVO','monto':20}).json()
    c.post(f"/api/v1/pagos/{p['id']}/aprobar")
    with sessions() as db:
        codigo = db.scalar(select(Boleto.codigo))
        chofer = db.get(Usuario, 3)
        chofer.cooperativa_id = 2
        db.commit()
    estado['usuario'] = 3
    assert c.post('/api/v1/boletos/abordar', json={'codigo':codigo}).status_code == 403
    assert c.get(f"/api/v1/boletos/{r['id']}/qr").status_code == 403
    with sessions() as db:
        db.get(Usuario, 3).cooperativa_id = 1
        db.get(Reserva, r['id']).fecha_viaje = hoy() + timedelta(days=1)
        db.commit()
    assert c.post('/api/v1/boletos/abordar', json={'codigo':codigo}).status_code == 409


def test_configuracion_catalogos_y_proteccion_itinerario(entorno):
    c, _, estado = entorno
    estado['usuario'] = 5
    nueva = {'nombre':'Nueva cooperativa','color_principal':'#123456'}
    assert c.post('/api/v1/cooperativas', json=nueva).status_code == 201
    assert c.post('/api/v1/cooperativas', json=nueva).status_code == 409
    assert c.put('/api/v1/configuracion', json={'nombre':'Mi sistema','color_principal':'#123456','soporte':'soporte@test.ec'}).status_code == 200
    assert c.get('/api/v1/configuracion').json()['nombre'] == 'Mi sistema'
    assert c.put('/api/v1/rutas/1', json={'origen':'Quito','destino':'Loja','duracion_estimada_horas':8}).status_code == 409
    assert c.post('/api/v1/rutas', json={'origen':'Quito','destino':'Quito','duracion_estimada_horas':8}).status_code == 422
    assert c.post('/api/v1/frecuencias', json={'ruta_id':1,'bus_id':1,'hora_salida':'12:00','precio':20}).status_code == 422
    estado['usuario'] = 1
    n = reservar(c).json()
    avisos = c.get('/api/v1/notificaciones').json()
    assert avisos
    assert c.patch(f"/api/v1/notificaciones/{avisos[0]['id']}/leer").status_code == 204
    assert c.get('/api/v1/notificaciones').json()[0]['leida'] is True


@pytest.mark.skipif(not os.getenv('TEST_DATABASE_URL', '').startswith('mysql'), reason='Requiere MySQL para verificar bloqueos entre conexiones')
def test_concurrencia_no_duplica_asiento_ni_boleto(entorno):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    c, sessions, estado = entorno
    barrera = Barrier(2)
    def intentar(_):
        barrera.wait(timeout=10)
        return reservar(c).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = sorted(pool.map(intentar, range(2)))
    assert resultados == [201, 409]
    with sessions() as db:
        reserva_id = db.scalar(select(Reserva.id))
    estado['usuario'] = 2
    pago = c.post('/api/v1/pagos', json={'reserva_id':reserva_id,'metodo_pago':'EFECTIVO','monto':20}).json()
    barrera = Barrier(2)
    def aprobar(_):
        barrera.wait(timeout=10)
        return c.post(f"/api/v1/pagos/{pago['id']}/aprobar").status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(aprobar, range(2))) == [200, 409]
    with sessions() as db:
        assert len(list(db.scalars(select(Boleto)))) == 1
