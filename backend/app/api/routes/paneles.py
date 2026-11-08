"""Consultas operativas y venta presencial transaccional por rol."""
import hashlib
import json
import secrets
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from pydantic import Field, ConfigDict
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import require_roles
from app.core.roles import Role, normalize_role
from app.db.database import get_db
from app.models.core_models import (Usuario, Cooperativa, Bus, Ruta, Frecuencia, Jornada,
    Reserva, Pago, PagoEstadoHistorial, Boleto, Abordaje, VentaPresencial)
from app.schemas.reservas import ReservaCreate
from app.services.operacion import hoy, tramo, puntos_ruta, bus_disponible, cedula_valida, sincronizar_ocupacion, notificar
from app.services.tarifas import calcular_pasajero, TipoPasajero

router = APIRouter(tags=["paneles"])
INTERNOS = (Role.ADMINISTRADOR, Role.USUARIO_COOPERATIVA, Role.OFICINISTA, Role.CHOFER, Role.AYUDANTE)


def buses_visibles(db, user):
    query = select(Bus)
    if normalize_role(user.rol) in {'cooperativa', 'chofer', 'ayudante'}:
        query = query.where(Bus.cooperativa_id == (user.cooperativa_id or -1))
    return list(db.scalars(query))


@router.get('/panel/opciones')
def opciones_panel(db: Session = Depends(get_db), user: Usuario = Depends(require_roles(*INTERNOS))):
    buses = buses_visibles(db, user)
    ids = [b.id for b in buses]
    coops = {b.cooperativa_id for b in buses}
    if user.cooperativa_id:
        coops.add(user.cooperativa_id)
    todas = normalize_role(user.rol) in {'admin', 'oficinista'}
    return {
        'cooperativas': [{'id': c.id, 'nombre': c.nombre} for c in db.scalars(select(Cooperativa).where(True if todas else Cooperativa.id.in_(coops)))],
        'buses': [{'id': b.id, 'nombre': f'{b.numero_disco} · {b.placa}', 'cooperativa_id': b.cooperativa_id} for b in buses],
        'rutas': [{'id': r.id, 'nombre': f'{r.origen} → {r.destino}'} for r in db.scalars(select(Ruta))],
        'frecuencias': [{'id': f.id, 'bus_id': f.bus_id, 'ruta_id': f.ruta_id, 'hora_salida': f.hora_salida}
            for f in db.scalars(select(Frecuencia).where(Frecuencia.bus_id.in_(ids)))],
    }


@router.get('/panel/resumen')
def resumen_panel(fecha: date | None = None, db: Session = Depends(get_db), user: Usuario = Depends(require_roles(*INTERNOS))):
    fecha = fecha or hoy()
    buses = buses_visibles(db, user)
    ids = [b.id for b in buses]
    frecuencias = list(db.scalars(select(Frecuencia).where(Frecuencia.bus_id.in_(ids))))
    fids = [f.id for f in frecuencias]
    reservas = list(db.scalars(select(Reserva).where(Reserva.frecuencia_id.in_(fids), Reserva.fecha_viaje == fecha)))
    confirmadas = [r for r in reservas if r.estado == 'CONFIRMADA']
    revisiones = db.scalar(select(func.count(Pago.id)).join(Reserva, Reserva.id == Pago.reserva_id).where(
        Reserva.frecuencia_id.in_(fids), Pago.estado == 'PENDIENTE')) or 0
    abordados = db.scalar(select(func.count(Abordaje.id)).join(Boleto, Boleto.id == Abordaje.boleto_id)
        .join(Reserva, Reserva.id == Boleto.reserva_id).where(Reserva.frecuencia_id.in_(fids), Reserva.fecha_viaje == fecha)) or 0
    salidas = []
    for f in sorted(frecuencias, key=lambda f: f.hora_salida):
        if not f.activo:
            continue
        try:
            bus = bus_disponible(db, f, fecha)
        except HTTPException:
            continue
        ruta = db.get(Ruta, f.ruta_id)
        ocupadas = {r.asiento for r in reservas if r.frecuencia_id == f.id and r.estado not in {'CANCELADA','EXPIRADA'}}
        salidas.append({'id': f.id, 'ruta': f'{ruta.origen} → {ruta.destino}', 'hora': f.hora_salida,
            'bus': f'{bus.numero_disco} · {bus.placa}', 'capacidad': bus.capacidad_asientos,
            'asientos_con_reserva': len(ocupadas), 'precio': f.precio})
    return {'fecha': fecha, 'buses_activos': sum(bool(b.activo) for b in buses),
        'frecuencias_activas': len(salidas), 'reservas': len(reservas), 'boletos_confirmados': len(confirmadas),
        'pagos_por_revisar': revisiones, 'abordados': abordados,
        'importe_confirmado': round(sum(r.precio for r in confirmadas), 2), 'salidas': salidas}


@router.get('/panel/manifiesto')
def manifiesto(fecha: date | None = None, frecuencia_id: int | None = Query(None, gt=0),
    db: Session = Depends(get_db), user: Usuario = Depends(require_roles(Role.ADMINISTRADOR, Role.OFICINISTA, Role.CHOFER, Role.AYUDANTE))):
    fecha = fecha or hoy()
    ids = [b.id for b in buses_visibles(db, user)]
    query = (select(Reserva, Frecuencia, Bus, Ruta, Abordaje.creado_en)
        .join(Frecuencia, Frecuencia.id == Reserva.frecuencia_id).join(Bus, Bus.id == Frecuencia.bus_id)
        .join(Ruta, Ruta.id == Frecuencia.ruta_id).join(Boleto, Boleto.reserva_id == Reserva.id)
        .outerjoin(Abordaje, Abordaje.boleto_id == Boleto.id)
        .where(Reserva.fecha_viaje == fecha, Reserva.estado == 'CONFIRMADA', Bus.id.in_(ids),
            select(Pago.id).where(Pago.reserva_id == Reserva.id, Pago.estado == 'APROBADO').exists())
        .order_by(Frecuencia.hora_salida, Reserva.asiento))
    if frecuencia_id:
        query = query.where(Reserva.frecuencia_id == frecuencia_id)
    items = []
    for r, f, b, ruta, acceso in db.execute(query):
        puntos = puntos_ruta(db, ruta)
        items.append({'reserva_id': r.id, 'frecuencia_id': f.id, 'pasajero': r.pasajero_nombre,
            'cedula': r.pasajero_cedula, 'asiento': r.asiento, 'tipo_pasajero': r.tipo_pasajero,
            'origen': puntos[r.origen_orden][0], 'destino': puntos[r.destino_orden][0],
            'hora_salida': f.hora_salida, 'bus': f'{b.numero_disco} · {b.placa}', 'abordado_en': acceso})
    return items


class VentaRequest(ReservaCreate):
    model_config = ConfigDict(extra='forbid')
    pasajero_nombre: str = Field(min_length=3, max_length=100)
    pasajero_cedula: str = Field(min_length=10, max_length=10)
    clave_operacion: str = Field(min_length=16, max_length=64, pattern=r'^[a-zA-Z0-9-]+$')
    descuento_verificado: bool = False


def respuesta_venta(db, venta):
    reserva = db.get(Reserva, venta.reserva_id)
    return {'reserva_id': reserva.id, 'pago_id': venta.pago_id, 'precio': reserva.precio,
        'asiento': reserva.asiento, 'estado': reserva.estado}


@router.post('/ventas/presencial', status_code=201)
def venta_presencial(payload: VentaRequest, response: Response, db: Session = Depends(get_db),
    user: Usuario = Depends(require_roles(Role.ADMINISTRADOR, Role.OFICINISTA))):
    huella = hashlib.sha256(json.dumps(payload.model_dump(mode='json'), sort_keys=True).encode()).hexdigest()
    # Serializar ventas del mismo viaje y reintentos en MySQL.
    frecuencia = db.scalar(select(Frecuencia).where(Frecuencia.id == payload.frecuencia_id).with_for_update())
    existente = db.scalar(select(VentaPresencial).where(VentaPresencial.clave == payload.clave_operacion).with_for_update())
    if existente:
        if existente.usuario_id != user.id:
            raise HTTPException(403, 'La operación pertenece a otro usuario')
        if existente.huella != huella:
            raise HTTPException(409, 'La operación ya existe con otros datos; inicie una nueva venta')
        response.status_code = 200
        return respuesta_venta(db, existente)
    if payload.fecha_viaje < hoy():
        raise HTTPException(422, 'No se puede vender un viaje pasado')
    if not frecuencia or not frecuencia.activo:
        raise HTTPException(404, 'Frecuencia no disponible')
    if not cedula_valida(payload.pasajero_cedula):
        raise HTTPException(422, 'Cédula ecuatoriana inválida')
    if payload.tipo_pasajero != TipoPasajero.GENERAL and not payload.descuento_verificado:
        raise HTTPException(422, 'Verifique la cédula y el respaldo del descuento')
    bus = bus_disponible(db, frecuencia, payload.fecha_viaje)
    puntos, destino = tramo(db, frecuencia, payload.origen_orden, payload.destino_orden)
    if payload.asiento > bus.capacidad_asientos:
        raise HTTPException(422, 'El asiento supera la capacidad del bus')
    if db.scalar(select(Reserva.id).where(Reserva.frecuencia_id == frecuencia.id,
        Reserva.fecha_viaje == payload.fecha_viaje, Reserva.asiento == payload.asiento,
        Reserva.estado.notin_(['CANCELADA','EXPIRADA']), Reserva.origen_orden < destino,
        Reserva.destino_orden > payload.origen_orden)):
        raise HTTPException(409, 'El asiento ya está reservado para este viaje')
    _, _, precio = calcular_pasajero(round(frecuencia.precio * (puntos[destino][2] - puntos[payload.origen_orden][2]),2), payload.tipo_pasajero)
    try:
        reserva = Reserva(usuario_id=user.id, frecuencia_id=frecuencia.id, fecha_viaje=payload.fecha_viaje,
            asiento=payload.asiento, origen_orden=payload.origen_orden, destino_orden=destino,
            pasajero_nombre=payload.pasajero_nombre.strip(), pasajero_cedula=payload.pasajero_cedula,
            tipo_pasajero=payload.tipo_pasajero.value, precio=float(precio), estado='CONFIRMADA')
        db.add(reserva)
        db.flush()
        sincronizar_ocupacion(db, reserva)
        pago = Pago(reserva_id=reserva.id, registrado_por_id=user.id, revisado_por_id=user.id,
            metodo_pago='EFECTIVO', monto=float(precio), estado='APROBADO', revisado_en=datetime.now(timezone.utc))
        db.add(pago)
        db.flush()
        db.add_all([PagoEstadoHistorial(pago_id=pago.id, estado_anterior=None, estado_nuevo='PENDIENTE', cambiado_por_id=user.id),
            PagoEstadoHistorial(pago_id=pago.id, estado_anterior='PENDIENTE', estado_nuevo='APROBADO', cambiado_por_id=user.id),
            Boleto(reserva_id=reserva.id, codigo=secrets.token_urlsafe(32))])
        venta = VentaPresencial(clave=payload.clave_operacion, huella=huella, usuario_id=user.id,
            reserva_id=reserva.id, pago_id=pago.id)
        db.add(venta)
        notificar(db, user.id, f'Venta presencial confirmada. Boleto de reserva {reserva.id} disponible.')
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'El asiento o la operación ya fueron registrados; actualice la disponibilidad') from None
    return respuesta_venta(db, venta)
