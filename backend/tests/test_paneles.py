from datetime import timedelta

from sqlalchemy import select, func
from app.models.core_models import Usuario, Reserva, Pago, Boleto, CorreoBoleto, VentaPresencial
from app.services import correo_boletos
from app.services.operacion import hoy
from test_release import entorno


def venta(**extra):
    return {'frecuencia_id':1,'fecha_viaje':str(hoy()),'asiento':5,'pasajero_nombre':'Pasajero de ventanilla',
        'pasajero_cedula':'1710034065','clave_operacion':'operacion-prueba-0001',**extra}


def test_venta_atomica_precio_servidor_y_reintento(entorno):
    c,sessions,estado=entorno
    assert c.post('/api/v1/ventas/presencial',json=venta()).status_code==403
    estado['usuario']=2
    creada=c.post('/api/v1/ventas/presencial',json=venta())
    assert creada.status_code==201, creada.text
    assert creada.json()['precio']==20 and creada.json()['estado']=='CONFIRMADA'
    repetida=c.post('/api/v1/ventas/presencial',json=venta())
    assert repetida.status_code==200 and repetida.json()==creada.json()
    assert c.post('/api/v1/ventas/presencial',json=venta(asiento=6)).status_code==409
    assert c.post('/api/v1/ventas/presencial',json=venta(clave_operacion='operacion-prueba-0002')).status_code==409
    assert c.post('/api/v1/ventas/presencial',json=venta(asiento=6,precio=0)).status_code==422
    with sessions() as db:
        for modelo in [Reserva,Pago,Boleto,VentaPresencial]:
            assert db.scalar(select(func.count()).select_from(modelo))==1
    assert c.get(f"/api/v1/boletos/{creada.json()['reserva_id']}/descarga").status_code==200
    estado['usuario']=5
    assert c.post('/api/v1/ventas/presencial',json=venta()).status_code==403


def test_venta_fallida_revierte_reserva_pago_y_ocupacion(entorno,monkeypatch):
    c,sessions,estado=entorno
    estado['usuario']=2
    monkeypatch.setattr('app.api.routes.paneles.secrets.token_urlsafe',lambda _: 'codigo-fijo-para-forzar-conflicto')
    assert c.post('/api/v1/ventas/presencial',json=venta(pasajero_correo='cliente@test.ec')).status_code==201
    assert c.post('/api/v1/ventas/presencial',json=venta(asiento=6, clave_operacion='operacion-prueba-0002', pasajero_correo='cliente@test.ec')).status_code==409
    with sessions() as db:
        assert db.scalar(select(func.count()).select_from(Reserva))==1
        assert db.scalar(select(func.count()).select_from(Pago))==1
        assert db.scalar(select(func.count()).select_from(CorreoBoleto))==1
    disponibles=c.get('/api/v1/reservas/disponibilidad/1',params={'fecha':str(hoy())}).json()
    assert 6 in disponibles['asientos_disponibles']


def test_venta_descuentos_validacion_y_tramos(entorno):
    c,sessions,estado=entorno
    estado['usuario']=2
    assert c.post('/api/v1/ventas/presencial',json=venta(pasajero_cedula='0000000000')).status_code==422
    assert c.post('/api/v1/ventas/presencial',json=venta(tipo_pasajero='ADULTO_MAYOR')).status_code==422
    r=c.post('/api/v1/ventas/presencial',json=venta(tipo_pasajero='ADULTO_MAYOR',descuento_verificado=True,origen_orden=1,destino_orden=2))
    assert r.status_code==201 and r.json()['precio']==7.5
    assert c.post('/api/v1/ventas/presencial',json=venta(clave_operacion='operacion-prueba-0002',origen_orden=0,destino_orden=1)).status_code==201


def test_resumen_opciones_y_manifiesto_por_rol(entorno):
    c,sessions,estado=entorno
    assert c.get('/api/v1/panel/resumen').status_code==403
    assert c.get('/api/v1/panel/manifiesto').status_code==403
    estado['usuario']=2
    assert c.post('/api/v1/ventas/presencial',json=venta()).status_code==201
    for uid in [2,3,4,5]:
        estado['usuario']=uid
        r=c.get('/api/v1/panel/resumen');assert r.status_code==200,r.text
        assert r.json()['boletos_confirmados']==1
        opciones=c.get('/api/v1/panel/opciones').json()
        assert len(opciones['buses'])==(1 if uid in [3,4] else 2)
    estado['usuario']=4
    assert c.get('/api/v1/panel/manifiesto').status_code==403
    for uid in [2,3,5]:
        estado['usuario']=uid
        lista=c.get('/api/v1/panel/manifiesto').json()
        assert len(lista)==1 and lista[0]['asiento']==5 and lista[0]['abordado_en'] is None
        assert 'codigo' not in lista[0]
    with sessions() as db:
        db.add(Usuario(id=6,nombre='Ayudante',correo='ayudante@test.ec',cedula='9999999998',rol='ayudante',cooperativa_id=2))
        db.commit()
    estado['usuario']=6
    assert c.get('/api/v1/panel/manifiesto').json()==[]
    assert c.get('/api/v1/panel/resumen').json()['boletos_confirmados']==0


def test_geografia_provincias_conexiones_solo_catalogo_activo(entorno):
    c,sessions,estado=entorno
    geo=c.get('/api/v1/ubicaciones').json()
    assert len(geo['provincias'])==24
    assert sum(len(p['ciudades']) for p in geo['provincias'])==222
    data=c.get('/api/v1/destinos').json()
    ciudades={v['valor']:v for v in data['ciudades']}
    assert ciudades['Quito']['provincia']=='Pichincha'
    assert ciudades['Latacunga']['provincia']=='Cotopaxi'
    assert ciudades['Cuenca']['provincia']=='Azuay'
    assert {'origen':'Latacunga','destino':'Cuenca'} in data['conexiones']
    assert {'origen':'Cuenca','destino':'Quito'} not in data['conexiones']
    estado['usuario']=5
    c.delete('/api/v1/buses/1')
    assert c.get('/api/v1/destinos').json()['ciudades']==[]


def test_abordaje_valida_detalle_y_actualiza_manifiesto(entorno):
    c,sessions,estado=entorno
    estado['usuario']=2
    r=c.post('/api/v1/ventas/presencial',json=venta()).json()
    with sessions() as db:
        codigo=db.scalar(select(Boleto.codigo).where(Boleto.reserva_id==r['reserva_id']))
    estado['usuario']=3
    validacion=c.post('/api/v1/boletos/validar',json={'codigo':codigo})
    assert validacion.status_code==200 and validacion.json()['pasajero']=='Pasajero de ventanilla'
    assert validacion.json()['origen']=='Quito' and validacion.json()['destino']=='Cuenca'
    assert c.get('/api/v1/panel/resumen').json()['abordados']==0
    assert c.post('/api/v1/boletos/abordar',json={'codigo':codigo}).status_code==201
    assert c.get('/api/v1/panel/resumen').json()['abordados']==1
    assert c.get('/api/v1/panel/manifiesto').json()[0]['abordado_en'] is not None
    assert c.post('/api/v1/boletos/abordar',json={'codigo':codigo}).status_code==409


import os
import pytest

@pytest.mark.skipif(not os.getenv('TEST_DATABASE_URL','').startswith('mysql'),reason='Requiere bloqueos MySQL entre conexiones')
def test_dos_reintentos_simultaneos_emiten_una_sola_venta(entorno):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    c,sessions,estado=entorno
    estado['usuario']=2
    barrera=Barrier(2)
    def intentar(_):
        barrera.wait(timeout=10)
        return c.post('/api/v1/ventas/presencial',json=venta()).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(intentar,range(2)))==[200,201]
    with sessions() as db:
        for modelo in [Reserva,Pago,Boleto,VentaPresencial]:
            assert db.scalar(select(func.count()).select_from(modelo))==1


def test_boleto_presenta_hora_del_tramo_y_escapa_texto(entorno):
    c,_,estado=entorno
    estado['usuario']=2
    r=c.post('/api/v1/ventas/presencial',json=venta(origen_orden=1,destino_orden=2,pasajero_nombre='<script>Prueba</script>')).json()
    boleto=c.get(f"/api/v1/boletos/{r['reserva_id']}/descarga")
    assert boleto.status_code==200
    assert '11:30' in boleto.text and 'Latacunga' in boleto.text
    assert '<script>' not in boleto.text and '&lt;script&gt;' in boleto.text
    historial=c.get('/api/v1/reservas/historial').json()
    assert historial[0]['hora_salida']=='11:30:00'


def test_correo_ventanilla_reintenta_y_adjunta_el_mismo_qr(entorno, monkeypatch):
    c, sessions, estado = entorno
    estado['usuario'] = 2
    ruta = '/api/v1/ventas/presencial'
    assert c.post(ruta, json=venta(pasajero_correo='persona@test.ec,otra@test.ec')).status_code == 422
    payload = venta(pasajero_correo='viajero@test.ec')
    respuesta = c.post(ruta, json=payload)
    assert respuesta.status_code == 201
    reserva_id = respuesta.json()['reserva_id']
    assert respuesta.json()['correo_estado'] == 'PENDIENTE'
    assert c.post(ruta, json=payload).status_code == 200
    assert c.post(ruta, json=venta(pasajero_correo='otro@test.ec')).status_code == 409
    qr = c.get(f'/api/v1/boletos/{reserva_id}/qr').content
    mensajes = []

    class GmailSimulado:
        def __init__(self, host, port, *, timeout, context):
            assert (host, port) == ('smtp.gmail.com', 465)

        def login(self, remitente, clave):
            assert remitente == 'pasajes@gmail.com'

        def send_message(self, mensaje):
            mensajes.append(mensaje)
            if len(mensajes) == 1:
                raise TimeoutError()

        def close(self):
            pass

    monkeypatch.setattr(correo_boletos.smtplib, 'SMTP_SSL', GmailSimulado)
    assert correo_boletos.procesar_correo('pasajes@gmail.com', 'clave-de-prueba', sessions)
    assert not correo_boletos.procesar_correo('pasajes@gmail.com', 'clave-de-prueba', sessions)
    with sessions() as db:
        correo = db.get(CorreoBoleto, reserva_id)
        assert correo.intentos == 1 and correo.estado == 'PENDIENTE'
        assert db.get(Reserva, reserva_id).estado == 'CONFIRMADA'
        correo.disponible_en = correo_boletos._ahora() - timedelta(seconds=1)
        db.commit()
    assert correo_boletos.procesar_correo('pasajes@gmail.com', 'clave-de-prueba', sessions)
    assert not correo_boletos.procesar_correo('pasajes@gmail.com', 'clave-de-prueba', sessions)
    with sessions() as db:
        assert db.get(CorreoBoleto, reserva_id).estado == 'ENVIADO'
    assert mensajes[0]['Message-ID'] == mensajes[1]['Message-ID']
    assert str(mensajes[1]['To']) == 'viajero@test.ec'
    assert next(mensajes[1].iter_attachments()).get_payload(decode=True) == qr


def test_chofer_emite_y_registra_ingreso_en_salida_asignada(entorno):
    c, _, estado = entorno
    estado['usuario'] = 3
    salida = '/api/v1/ventas/presencial'
    assert c.post(salida, json=venta()).status_code == 403

    estado['usuario'] = 4
    jornada = c.post('/api/v1/jornadas', json={
        'fecha': str(hoy()), 'bus_id': 1, 'frecuencia_id': 1,
    })
    assert jornada.status_code == 201
    asignar = f"/api/v1/jornadas/{jornada.json()['id']}/chofer"
    assert c.patch(asignar, json={'chofer_id': 2}).status_code == 422
    assert c.patch(asignar, json={'chofer_id': 3}).status_code == 200

    estado['usuario'] = 3
    assert c.get('/api/v1/panel/mis-salidas', params={'fecha': str(hoy())}).json() == [1]
    assert c.post(salida, json=venta(fecha_viaje=str(hoy() + timedelta(days=1)))).status_code == 403
    respuesta = c.post(salida, json=venta())
    assert respuesta.status_code == 201
    reserva = respuesta.json()['reserva_id']
    ingreso = f'/api/v1/boletos/{reserva}/abordar'
    assert c.post(ingreso).status_code == 201
    assert c.post(ingreso).status_code == 409
    assert c.get('/api/v1/panel/manifiesto').json()[0]['abordado_en']



def test_ayudante_emite_solo_para_su_salida(entorno):
    c, sessions, estado = entorno
    with sessions() as db:
        db.add(Usuario(id=6, nombre='Ayudante', correo='ayudante@test.ec',
                       cedula='1710034072', rol='ayudante', cooperativa_id=1))
        db.commit()
    estado['usuario'] = 6
    ventas = '/api/v1/ventas/presencial'
    assert c.post(ventas, json=venta()).status_code == 403

    estado['usuario'] = 4
    jornada = c.post('/api/v1/jornadas', json={
        'fecha': str(hoy()), 'bus_id': 1, 'frecuencia_id': 1, 'chofer_id': 3,
    })
    assert jornada.status_code == 201
    tripulacion = f"/api/v1/jornadas/{jornada.json()['id']}/tripulacion"
    assert c.patch(tripulacion, json={'ayudante_id': 3}).status_code == 422
    asignacion = c.patch(tripulacion, json={'ayudante_id': 6})
    assert asignacion.status_code == 200
    assert asignacion.json()['chofer_id'] == 3

    estado['usuario'] = 6
    assert c.get('/api/v1/panel/mis-salidas', params={'fecha': str(hoy())}).json() == [1]
    assert c.post(ventas, json=venta(fecha_viaje=str(hoy() + timedelta(days=1)))).status_code == 403
    assert c.post(ventas, json=venta()).status_code == 201
