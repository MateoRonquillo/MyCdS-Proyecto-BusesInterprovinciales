from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import get_current_user
from app.core.roles import Role, normalize_role
from app.db.database import get_db
from app.models.core_models import Bus, Cooperativa, Frecuencia, Pago, PagoEstadoHistorial, Reserva, Ruta, Usuario
from app.schemas.reservas import (
    AsientoEstado,
    DisponibilidadAsientosResponse,
    EstadoReserva,
    HistorialCompraItem,
    ReservaCreate,
    ReservaEstadoUpdate,
    ReservaResponse,
    ReservaUpdate,
)
from app.services.tarifas import calcular_pasajero
from app.services.operacion import hoy, tramo, bus_disponible, sincronizar_ocupacion, notificar, cedula_valida

router = APIRouter(prefix="/reservas", tags=["reservas"])
STAFF_ROLES = (Role.ADMINISTRADOR, Role.OFICINISTA)
TRANSICIONES_VALIDAS: dict[str, set[str]] = {
    "PENDIENTE": {"PAGO_EN_REVISION", "PAGADA", "CONFIRMADA", "CANCELADA", "EXPIRADA"},
    "PAGO_EN_REVISION": {"PAGADA", "CONFIRMADA", "PENDIENTE", "CANCELADA", "EXPIRADA"},
    "PAGADA": {"CONFIRMADA", "CANCELADA"},
    "CONFIRMADA": {"CANCELADA"},
    "CANCELADA": set(),
    "EXPIRADA": set(),
}

def _corregir_reservas_expiradas(db: Session) -> None:
    """Garantiza consistencia en BD pasando a EXPIRADA reservas pendientes o en revisión cuya fecha ya venció."""
    stmt = select(Reserva).where(
        Reserva.estado.in_(["PENDIENTE", "PAGO_EN_REVISION"]),
        Reserva.fecha_viaje < hoy(),
    )
    expiradas = db.scalars(stmt).all()
    if expiradas:
        for r in expiradas:
            r.estado = "EXPIRADA"
            sincronizar_ocupacion(db, r)
        db.commit()


def _owned_reservation(db: Session, reservation_id: int, user: Usuario) -> Reserva:
    reservation = db.scalar(select(Reserva).where(Reserva.id == reservation_id).with_for_update())
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    staff_roles = {normalize_role(role) for role in STAFF_ROLES}
    if normalize_role(user.rol) not in staff_roles and reservation.usuario_id != user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para consultar esta reserva")
    return reservation


def _sincronizar_reserva_expirada(db: Session, reservation: Reserva) -> bool:
    """Marca reservas vencidas según la fecha del viaje antes de operar con ellas."""
    if reservation.estado in {"PENDIENTE", "PAGO_EN_REVISION"} and reservation.fecha_viaje < hoy():
        reservation.estado = "EXPIRADA"
        db.commit()
        return True
    return False


def _check_seat(
    db: Session,
    frequency: Frecuencia,
    travel_date: date,
    seat: int,
    exclude_id: int | None = None,
    origen_orden: int = 0,
    destino_orden: int | None = None,
) -> None:
    bus = bus_disponible(db, frequency, travel_date)
    _, destino_orden = tramo(db, frequency, origen_orden, destino_orden)
    if seat > bus.capacidad_asientos:
        raise HTTPException(status_code=422, detail="El asiento supera la capacidad del bus")
    query = select(Reserva.id).where(
        Reserva.frecuencia_id == frequency.id,
        Reserva.fecha_viaje == travel_date,
        Reserva.asiento == seat,
        Reserva.estado.notin_(["CANCELADA", "EXPIRADA"]),
        Reserva.origen_orden < destino_orden,
        Reserva.destino_orden > origen_orden,
    )
    if exclude_id is not None:
        query = query.where(Reserva.id != exclude_id)
    if db.scalar(query) is not None:
        raise HTTPException(status_code=409, detail="El asiento ya está reservado para este viaje")

@router.get(
    "/disponibilidad/{frequency_id}",
    response_model=DisponibilidadAsientosResponse,
    summary="Consultar disponibilidad y mapa de asientos de un viaje",
)
def get_seat_availability(
    frequency_id: int,
    fecha: date = Query(..., description="Fecha del viaje a consultar (YYYY-MM-DD)"),
    origen_orden: int = Query(0, ge=0),
    destino_orden: int | None = Query(None, gt=0),
    db: Session = Depends(get_db),
) -> DisponibilidadAsientosResponse:
    frequency = db.get(Frecuencia, frequency_id)
    if frequency is None or not frequency.activo:
        raise HTTPException(status_code=404, detail="Frecuencia no encontrada o inactiva")

    bus = bus_disponible(db, frequency, fecha)
    _, destino_orden = tramo(db, frequency, origen_orden, destino_orden)

    # Consultar los números de asientos ocupados para esa fecha (excluyendo canceladas)
    query = select(Reserva.asiento).where(
        Reserva.frecuencia_id == frequency.id,
        Reserva.fecha_viaje == fecha,
        Reserva.estado.notin_(["CANCELADA", "EXPIRADA"]),
        Reserva.origen_orden < destino_orden,
        Reserva.destino_orden > origen_orden,
    )
    occupied_seats = sorted(set(db.scalars(query)))
    all_seats = list(range(1, bus.capacidad_asientos + 1))
    available_seats = [s for s in all_seats if s not in occupied_seats]
    seat_map = [
        AsientoEstado(numero=s, ocupado=(s in occupied_seats), tipo="VIP" if str(s) in bus.asientos_vip.split(",") else "NORMAL")
        for s in all_seats
    ]

    return DisponibilidadAsientosResponse(
        frecuencia_id=frequency.id,
        fecha_viaje=fecha,
        capacidad_total=bus.capacidad_asientos,
        asientos_ocupados=occupied_seats,
        asientos_disponibles=available_seats,
        mapa_asientos=seat_map,
    )
@router.post(
    "",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una reserva",
)
def create_reservation(
    payload: ReservaCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Reserva:
    if payload.fecha_viaje < hoy():
        raise HTTPException(status_code=422, detail="La fecha del viaje no puede estar en el pasado")
    frequency = db.scalar(select(Frecuencia).where(Frecuencia.id == payload.frecuencia_id).with_for_update())
    if frequency is None or not frequency.activo:
        raise HTTPException(status_code=404, detail="Frecuencia no encontrada o inactiva")
    if normalize_role(user.rol) not in {"admin", "oficinista", "cliente"}:
        raise HTTPException(403, "Este rol no puede realizar ventas")
    puntos, destino = tramo(db, frequency, payload.origen_orden, payload.destino_orden)
    _check_seat(db, frequency, payload.fecha_viaje, payload.asiento, origen_orden=payload.origen_orden, destino_orden=destino)
    if payload.pasajero_cedula and not cedula_valida(payload.pasajero_cedula):
        raise HTTPException(422, "Cédula ecuatoriana inválida")
    if payload.tipo_pasajero.value != "GENERAL" and not cedula_valida(payload.pasajero_cedula):
        raise HTTPException(422, "Debe registrar una cédula válida para solicitar el descuento")
    passenger_type = payload.tipo_pasajero
    _, _, amount = calcular_pasajero(round(frequency.precio * (puntos[destino][2] - puntos[payload.origen_orden][2]), 2), passenger_type)
    reservation = Reserva(
        usuario_id=user.id,
        frecuencia_id=frequency.id,
        fecha_viaje=payload.fecha_viaje,
        asiento=payload.asiento,
        tipo_pasajero=passenger_type.value,
        precio=float(amount),
        estado="PENDIENTE",
        origen_orden=payload.origen_orden,
        destino_orden=destino,
        pasajero_nombre=payload.pasajero_nombre or user.nombre,
        pasajero_cedula=payload.pasajero_cedula or user.cedula,
    )
    db.add(reservation)
    try:
        db.flush()
        sincronizar_ocupacion(db, reservation)
        notificar(db, reservation.usuario_id, f"Reserva {reservation.id} creada; pendiente de pago.")
        db.commit()
        db.refresh(reservation)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El asiento ya está reservado para este viaje",
        )
    return reservation

@router.get("", response_model=list[ReservaResponse], summary="Listar reservas")
def list_reservations(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[Reserva]:
    _corregir_reservas_expiradas(db)  
    query = select(Reserva).order_by(Reserva.fecha_viaje, Reserva.id)
    if normalize_role(user.rol) not in {normalize_role(role) for role in STAFF_ROLES}:
        query = query.where(Reserva.usuario_id == user.id)
    return list(db.scalars(query))

@router.get(
    "/historial",
    response_model=list[HistorialCompraItem],
    summary="Consultar historial detallado de compras del usuario",
)
def get_purchase_history(
    estado: str | None = Query(None, description="Filtrar por estado opcional (ej: PENDIENTE, PAGADA)"),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[HistorialCompraItem]:
    _corregir_reservas_expiradas(db)  
    query = (
        select(
            Reserva.id.label("reserva_id"),
            Reserva.frecuencia_id,
            Cooperativa.nombre.label("cooperativa"),
            Bus.numero_disco,
            Ruta.origen,
            Ruta.destino,
            Frecuencia.hora_salida,
            Reserva.fecha_viaje,
            Reserva.asiento,
            Reserva.tipo_pasajero,
            Reserva.origen_orden,
            Reserva.destino_orden,
            Reserva.pasajero_nombre,
            Reserva.pasajero_cedula,
            Reserva.precio,
            Reserva.estado,
        )
        .join(Frecuencia, Reserva.frecuencia_id == Frecuencia.id)
        .join(Bus, Frecuencia.bus_id == Bus.id)
        .join(Cooperativa, Bus.cooperativa_id == Cooperativa.id)
        .join(Ruta, Frecuencia.ruta_id == Ruta.id)
        .order_by(Reserva.fecha_viaje.desc(), Reserva.id.desc())
    )

    # Si es cliente normal, solo ve sus propias compras; si es personal, ve todas
    if normalize_role(user.rol) not in {normalize_role(role) for role in STAFF_ROLES}:
        query = query.where(Reserva.usuario_id == user.id)

    if estado:
        query = query.where(Reserva.estado == estado.upper())

    rows = db.execute(query).mappings().all()
    resultado = []
    from app.services.operacion import puntos_ruta
    for row in rows:
        datos = dict(row)
        f = db.get(Frecuencia, datos["frecuencia_id"])
        puntos = puntos_ruta(db, db.get(Ruta, f.ruta_id))
        origen_orden = datos.pop("origen_orden")
        datos["hora_salida"] = (datetime.combine(datos["fecha_viaje"], f.hora_salida) + timedelta(minutes=puntos[origen_orden][1])).time()
        datos["origen"] = puntos[origen_orden][0]
        datos["destino"] = puntos[datos.pop("destino_orden")][0]
        resultado.append(HistorialCompraItem(**datos))
    return resultado

@router.get("/{reservation_id}", response_model=ReservaResponse, summary="Consultar una reserva")
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Reserva:
    reservation = _owned_reservation(db, reservation_id, user)
    _sincronizar_reserva_expirada(db, reservation)
    return reservation


@router.put(
    "/{reservation_id}",
    response_model=ReservaResponse,
    summary="Cambiar el asiento de una reserva",
)
def update_reservation(
    reservation_id: int,
    payload: ReservaUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Reserva:
    reservation = _owned_reservation(db, reservation_id, user)
    _sincronizar_reserva_expirada(db, reservation)
    if reservation.estado != "PENDIENTE":
        raise HTTPException(status_code=409, detail="Solo se pueden modificar reservas pendientes")
    frequency = db.scalar(select(Frecuencia).where(Frecuencia.id == reservation.frecuencia_id).with_for_update())
    if frequency is None or not frequency.activo:
        raise HTTPException(status_code=409, detail="La frecuencia ya no está disponible")
    _check_seat(db, frequency, reservation.fecha_viaje, payload.asiento, exclude_id=reservation.id, origen_orden=reservation.origen_orden, destino_orden=reservation.destino_orden)
    reservation.asiento = payload.asiento
    try:
        sincronizar_ocupacion(db, reservation)
        db.commit()
        db.refresh(reservation)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El asiento ya está reservado para este viaje",
        )
    return reservation


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Cancelar una reserva")
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Response:
    reservation = _owned_reservation(db, reservation_id, user)
    _sincronizar_reserva_expirada(db, reservation)
    if reservation.estado == "CANCELADA":
        raise HTTPException(status_code=409, detail="La reserva ya está cancelada")
    if reservation.estado not in {"PENDIENTE", "PAGO_EN_REVISION"}:
        raise HTTPException(status_code=409, detail="Solo se pueden cancelar reservas pendientes o en revisión de pago")

    # Sincronizar pago pendiente si la reserva estaba en revisión
    query_pago = select(Pago).where(Pago.reserva_id == reservation.id, Pago.estado == "PENDIENTE")
    pago_asociado = db.scalar(query_pago)
    if pago_asociado is not None:
        pago_asociado.estado = "RECHAZADO"
        pago_asociado.motivo_rechazo = "Cancelado por anulación de la reserva"
        pago_asociado.revisado_por_id = user.id
        pago_asociado.revisado_en = datetime.now(timezone.utc)
        db.add(
            PagoEstadoHistorial(
                pago_id=pago_asociado.id,
                estado_anterior="PENDIENTE",
                estado_nuevo="RECHAZADO",
                cambiado_por_id=user.id,
                motivo="Cancelado por anulación de la reserva",
            )
        )

    reservation.estado = "CANCELADA"
    sincronizar_ocupacion(db, reservation)
    notificar(db, reservation.usuario_id, f"Reserva {reservation.id} cancelada.")
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.patch(
    "/{reservation_id}/estado",
    response_model=ReservaResponse,
    summary="Actualizar y corregir el estado de una reserva garantizando consistencia",
)
def update_reservation_status(
    reservation_id: int,
    payload: ReservaEstadoUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Reserva:
    staff_roles = {normalize_role(role) for role in STAFF_ROLES}
    if normalize_role(user.rol) not in staff_roles:
        raise HTTPException(status_code=403, detail="No tiene permisos para modificar estados de reserva")

    reservation = db.scalar(select(Reserva).where(Reserva.id == reservation_id).with_for_update())
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    estado_actual = reservation.estado.upper()
    nuevo_estado = payload.estado.value.upper()

    if estado_actual == nuevo_estado:
        return reservation

    permitidos = TRANSICIONES_VALIDAS.get(estado_actual, set())
    if nuevo_estado not in permitidos:
        raise HTTPException(
            status_code=409,
            detail=f"Transición de estado inválida: no se puede cambiar de {estado_actual} a {nuevo_estado}",
        )

    # Validar que no se pague o confirme una reserva cuyo viaje ya venció
    if estado_actual in {"PENDIENTE", "PAGO_EN_REVISION"} and nuevo_estado in {"PAGADA", "CONFIRMADA"}:
        if reservation.fecha_viaje < hoy():
            reservation.estado = "EXPIRADA"
            sincronizar_ocupacion(db, reservation)
            db.commit()
            raise HTTPException(
                status_code=409,
                detail="La fecha del viaje ya venció; la reserva ha expirado y no puede pagarse ni confirmarse",
            )

    if nuevo_estado in {"PAGADA", "CONFIRMADA"}:
        raise HTTPException(409, "Use la aprobación de pagos para confirmar y emitir el boleto")
    reservation.estado = nuevo_estado
    sincronizar_ocupacion(db, reservation)
    notificar(db, reservation.usuario_id, f"Reserva {reservation.id}: {nuevo_estado}.")
    db.commit()
    db.refresh(reservation)
    return reservation