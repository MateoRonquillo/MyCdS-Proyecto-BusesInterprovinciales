from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.roles import Role, normalize_role
from app.db.database import get_db
from app.models.core_models import Bus, Frecuencia, Reserva, Usuario
from app.schemas.reservas import ReservaCreate, ReservaResponse, ReservaUpdate
from app.services.tarifas import calcular_importe

router = APIRouter(prefix="/reservas", tags=["reservas"])
STAFF_ROLES = (Role.ADMINISTRADOR, Role.OFICINISTA)


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
        Reserva.estado != "CANCELADA",
    )
    if exclude_id is not None:
        query = query.where(Reserva.id != exclude_id)
    if db.scalar(query) is not None:
        raise HTTPException(status_code=409, detail="El asiento ya está reservado para este viaje")


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
    reservation = Reserva(
        usuario_id=user.id,
        frecuencia_id=frequency.id,
        fecha_viaje=payload.fecha_viaje,
        asiento=payload.asiento,
        precio=float(calcular_importe(frequency.precio, 1)[0]),
        estado="PENDIENTE",
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@router.get("", response_model=list[ReservaResponse], summary="Listar reservas")
def list_reservations(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[Reserva]:
    query = select(Reserva).order_by(Reserva.fecha_viaje, Reserva.id)
    if normalize_role(user.rol) not in {normalize_role(role) for role in STAFF_ROLES}:
        query = query.where(Reserva.usuario_id == user.id)
    return list(db.scalars(query))


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
    db.commit()
    db.refresh(reservation)
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
    if reservation.estado != "PENDIENTE":
        raise HTTPException(status_code=409, detail="Solo se pueden cancelar reservas pendientes")
    reservation.estado = "CANCELADA"
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
