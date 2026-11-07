from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import get_current_user
from app.core.roles import Role, normalize_role
from app.db.database import get_db
from app.models.core_models import Bus, Cooperativa, Frecuencia, Reserva, Ruta, Usuario
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
    """Garantiza consistencia en BD pasando a EXPIRADA reservas pendientes cuya fecha ya venció."""
    stmt = select(Reserva).where(Reserva.estado == "PENDIENTE", Reserva.fecha_viaje < date.today())
    expiradas = db.scalars(stmt).all()
    if expiradas:
        for r in expiradas:
            r.estado = "EXPIRADA"
        db.commit()


def _owned_reservation(db: Session, reservation_id: int, user: Usuario) -> Reserva:
    reservation = db.get(Reserva, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    staff_roles = {normalize_role(role) for role in STAFF_ROLES}
    if normalize_role(user.rol) not in staff_roles and reservation.usuario_id != user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para consultar esta reserva")
    return reservation


def _check_seat(
    db: Session,
    frequency: Frecuencia,
    travel_date: date,
    seat: int,
    exclude_id: int | None = None,
) -> None:
    bus = db.get(Bus, frequency.bus_id)
    if bus is None or not bus.activo:
        raise HTTPException(status_code=409, detail="El bus de esta frecuencia no está disponible")
    if seat > bus.capacidad_asientos:
        raise HTTPException(status_code=422, detail="El asiento supera la capacidad del bus")
    query = select(Reserva.id).where(
        Reserva.frecuencia_id == frequency.id,
        Reserva.fecha_viaje == travel_date,
        Reserva.asiento == seat,
        Reserva.estado.not_in(["CANCELADA", "EXPIRADA"]),
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
    db: Session = Depends(get_db),
) -> DisponibilidadAsientosResponse:
    frequency = db.get(Frecuencia, frequency_id)
    if frequency is None or not frequency.activo:
        raise HTTPException(status_code=404, detail="Frecuencia no encontrada o inactiva")

    bus = db.get(Bus, frequency.bus_id)
    if bus is None or not bus.activo:
        raise HTTPException(status_code=409, detail="El bus asignado a la frecuencia no está disponible")

    # Consultar los números de asientos ocupados para esa fecha (excluyendo canceladas)
    query = select(Reserva.asiento).where(
        Reserva.frecuencia_id == frequency.id,
        Reserva.fecha_viaje == fecha,
        Reserva.estado.not_in(["CANCELADA", "EXPIRADA"]),
    )
    occupied_seats = sorted(list(db.scalars(query)))
    all_seats = list(range(1, bus.capacidad_asientos + 1))
    available_seats = [s for s in all_seats if s not in occupied_seats]
    seat_map = [
        AsientoEstado(numero=s, ocupado=(s in occupied_seats))
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
    if payload.fecha_viaje < date.today():
        raise HTTPException(status_code=422, detail="La fecha del viaje no puede estar en el pasado")
    frequency = db.get(Frecuencia, payload.frecuencia_id)
    if frequency is None or not frequency.activo:
        raise HTTPException(status_code=404, detail="Frecuencia no encontrada o inactiva")
    _check_seat(db, frequency, payload.fecha_viaje, payload.asiento)
    passenger_type = payload.tipo_pasajero
    _, _, amount = calcular_pasajero(frequency.precio, passenger_type)
    reservation = Reserva(
        usuario_id=user.id,
        frecuencia_id=frequency.id,
        fecha_viaje=payload.fecha_viaje,
        asiento=payload.asiento,
        tipo_pasajero=passenger_type.value,
        precio=float(amount),
        estado="PENDIENTE",
    )
    db.add(reservation)
    try:
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
    return [HistorialCompraItem(**row) for row in rows]

@router.get("/{reservation_id}", response_model=ReservaResponse, summary="Consultar una reserva")
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Reserva:
    return _owned_reservation(db, reservation_id, user)


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
    if reservation.estado != "PENDIENTE":
        raise HTTPException(status_code=409, detail="Solo se pueden modificar reservas pendientes")
    frequency = db.get(Frecuencia, reservation.frecuencia_id)
    if frequency is None or not frequency.activo:
        raise HTTPException(status_code=409, detail="La frecuencia ya no está disponible")
    _check_seat(db, frequency, reservation.fecha_viaje, payload.asiento, exclude_id=reservation.id)
    reservation.asiento = payload.asiento
    try:
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
    if reservation.estado == "CANCELADA":
        raise HTTPException(status_code=409, detail="La reserva ya está cancelada")
    if reservation.estado not in {"PENDIENTE", "PAGO_EN_REVISION"}:
        raise HTTPException(status_code=409, detail="Solo se pueden cancelar reservas pendientes o en revisión de pago")
    reservation.estado = "CANCELADA"
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

    reservation = db.get(Reserva, reservation_id)
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
        if reservation.fecha_viaje < date.today():
            reservation.estado = "EXPIRADA"
            db.commit()
            raise HTTPException(
                status_code=409,
                detail="La fecha del viaje ya venció; la reserva ha expirado y no puede pagarse ni confirmarse",
            )

    reservation.estado = nuevo_estado
    db.commit()
    db.refresh(reservation)
    return reservation