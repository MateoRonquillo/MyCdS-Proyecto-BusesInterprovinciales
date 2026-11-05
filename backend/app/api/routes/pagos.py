from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_roles
from app.core.roles import Role, normalize_role
from app.db.database import get_db
from app.models.core_models import Boleto, Pago, PagoEstadoHistorial, Reserva, Usuario
from app.schemas.pagos import (
    EstadoPago,
    PagoCreate,
    PagoEstadoHistorialResponse,
    PagoResponse,
    RechazoPagoRequest,
)

router = APIRouter(prefix="/pagos", tags=["pagos"])
STAFF_ROLES = (Role.ADMINISTRADOR, Role.OFICINISTA)
STAFF_ROLE_VALUES = {normalize_role(role) for role in STAFF_ROLES}
CENTAVO = Decimal("0.01")


def _get_payment(db: Session, payment_id: int) -> Pago:
    payment = db.get(Pago, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return payment


def _get_payment_for_update(db: Session, payment_id: int) -> Pago:
    payment = db.scalar(select(Pago).where(Pago.id == payment_id).with_for_update())
    if payment is None:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return payment


def _get_reservation_for_update(db: Session, reservation_id: int) -> Reserva:
    reservation = db.scalar(
        select(Reserva).where(Reserva.id == reservation_id).with_for_update()
    )
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reservation


def _ensure_payment_access(db: Session, payment: Pago, user: Usuario) -> None:
    if normalize_role(user.rol) in STAFF_ROLE_VALUES:
        return
    reservation = db.get(Reserva, payment.reserva_id)
    if reservation is None or reservation.usuario_id != user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para consultar este pago")


def _record_status_change(
    db: Session,
    payment: Pago,
    previous_status: str | None,
    changed_by: Usuario,
    reason: str | None = None,
) -> None:
    db.add(
        PagoEstadoHistorial(
            pago_id=payment.id,
            estado_anterior=previous_status,
            estado_nuevo=payment.estado,
            cambiado_por_id=changed_by.id,
            motivo=reason,
        )
    )


@router.post(
    "",
    response_model=PagoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un pago para revisión",
)
def create_payment(
    payload: PagoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Pago:
    reservation = _get_reservation_for_update(db, payload.reserva_id)
    is_staff = normalize_role(user.rol) in STAFF_ROLE_VALUES
    if not is_staff and reservation.usuario_id != user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para pagar esta reserva")
    if reservation.estado != "PENDIENTE":
        raise HTTPException(status_code=409, detail="La reserva no está pendiente de pago")
    pending_payment = db.scalar(
        select(Pago.id).where(
            Pago.reserva_id == reservation.id,
            Pago.estado == EstadoPago.PENDIENTE.value,
        )
    )
    if pending_payment is not None:
        raise HTTPException(status_code=409, detail="La reserva ya tiene un pago en revisión")

    expected = Decimal(str(reservation.precio)).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    submitted = payload.monto.quantize(CENTAVO, rounding=ROUND_HALF_UP)
    if submitted != expected:
        raise HTTPException(
            status_code=422,
            detail=f"El monto debe coincidir con el total de la reserva ({expected})",
        )

    payment = Pago(
        reserva_id=reservation.id,
        registrado_por_id=user.id,
        metodo_pago=payload.metodo_pago.value,
        monto=float(submitted),
        referencia=payload.referencia,
        estado=EstadoPago.PENDIENTE.value,
    )
    reservation.estado = "PAGO_EN_REVISION"
    db.add(payment)
    db.flush()
    _record_status_change(db, payment, None, user)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("", response_model=list[PagoResponse], summary="Listar pagos")
def list_payments(
    estado: EstadoPago | None = Query(default=None),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[Pago]:
    query = select(Pago).order_by(Pago.creado_en.desc(), Pago.id.desc())
    if normalize_role(user.rol) not in STAFF_ROLE_VALUES:
        query = query.join(Reserva, Pago.reserva_id == Reserva.id).where(
            Reserva.usuario_id == user.id
        )
    if estado is not None:
        query = query.where(Pago.estado == estado.value)
    return list(db.scalars(query))


@router.get("/{payment_id}", response_model=PagoResponse, summary="Consultar un pago")
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Pago:
    payment = _get_payment(db, payment_id)
    _ensure_payment_access(db, payment, user)
    return payment


@router.get(
    "/{payment_id}/historial",
    response_model=list[PagoEstadoHistorialResponse],
    summary="Consultar el historial de estados de un pago",
)
def get_payment_status_history(
    payment_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[PagoEstadoHistorial]:
    payment = _get_payment(db, payment_id)
    _ensure_payment_access(db, payment, user)
    query = (
        select(PagoEstadoHistorial)
        .where(PagoEstadoHistorial.pago_id == payment.id)
        .order_by(PagoEstadoHistorial.cambiado_en, PagoEstadoHistorial.id)
    )
    return list(db.scalars(query))


@router.post(
    "/{payment_id}/aprobar",
    response_model=PagoResponse,
    summary="Aprobar un pago y confirmar la reserva",
)
def approve_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    reviewer: Usuario = Depends(require_roles(*STAFF_ROLES)),
) -> Pago:
    payment = _get_payment_for_update(db, payment_id)
    reservation = _get_reservation_for_update(db, payment.reserva_id)
    if payment.estado != EstadoPago.PENDIENTE.value:
        raise HTTPException(status_code=409, detail="El pago ya fue revisado")
    if reservation.estado != "PAGO_EN_REVISION":
        raise HTTPException(status_code=409, detail="La reserva no está en revisión de pago")
    previous_status = payment.estado
    payment.estado = EstadoPago.APROBADO.value
    payment.revisado_por_id = reviewer.id
    payment.revisado_en = datetime.now(timezone.utc)
    reservation.estado = "CONFIRMADA"
    ticket = db.scalar(select(Boleto).where(Boleto.reserva_id == reservation.id))
    if ticket is None:
        db.add(Boleto(reserva_id=reservation.id, codigo=secrets.token_urlsafe(32)))
    _record_status_change(db, payment, previous_status, reviewer)
    db.commit()
    db.refresh(payment)
    return payment


@router.post(
    "/{payment_id}/rechazar",
    response_model=PagoResponse,
    summary="Rechazar un pago y devolver la reserva a pendiente",
)
def reject_payment(
    payment_id: int,
    payload: RechazoPagoRequest,
    db: Session = Depends(get_db),
    reviewer: Usuario = Depends(require_roles(*STAFF_ROLES)),
) -> Pago:
    payment = _get_payment_for_update(db, payment_id)
    reservation = _get_reservation_for_update(db, payment.reserva_id)
    if payment.estado != EstadoPago.PENDIENTE.value:
        raise HTTPException(status_code=409, detail="El pago ya fue revisado")
    if reservation.estado != "PAGO_EN_REVISION":
        raise HTTPException(status_code=409, detail="La reserva no está en revisión de pago")
    previous_status = payment.estado
    payment.estado = EstadoPago.RECHAZADO.value
    payment.motivo_rechazo = payload.motivo
    payment.revisado_por_id = reviewer.id
    payment.revisado_en = datetime.now(timezone.utc)
    reservation.estado = "PENDIENTE"
    _record_status_change(db, payment, previous_status, reviewer, payload.motivo)
    db.commit()
    db.refresh(payment)
    return payment
