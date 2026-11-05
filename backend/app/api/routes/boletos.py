import json
from io import BytesIO

import qrcode
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_roles
from app.core.roles import Role, normalize_role
from app.db.database import get_db
from app.models.core_models import Boleto, Pago, Reserva, Usuario

router = APIRouter(prefix="/boletos", tags=["boletos"])
STAFF_ROLES = (Role.ADMINISTRADOR, Role.OFICINISTA, Role.CHOFER, Role.AYUDANTE)
OWNER_OR_STAFF = {normalize_role(role) for role in STAFF_ROLES}


class ValidarBoletoRequest(BaseModel):
    codigo: str = Field(min_length=20, max_length=64)


def _approved_payment_exists(db: Session, reservation_id: int) -> bool:
    return db.scalar(
        select(Pago.id).where(
            Pago.reserva_id == reservation_id,
            Pago.estado == "APROBADO",
        ).limit(1)
    ) is not None


@router.get("/{reserva_id}/qr", summary="Descargar el QR de un boleto pagado")
def get_ticket_qr(
    reserva_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> StreamingResponse:
    reservation = db.get(Reserva, reserva_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    if normalize_role(user.rol) not in OWNER_OR_STAFF and reservation.usuario_id != user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para consultar este boleto")
    if reservation.estado != "CONFIRMADA" or not _approved_payment_exists(db, reservation.id):
        raise HTTPException(status_code=409, detail="El boleto estará disponible cuando el pago sea aprobado")
    ticket = db.scalar(select(Boleto).where(Boleto.reserva_id == reservation.id))
    if ticket is None:
        raise HTTPException(status_code=404, detail="Boleto no encontrado")

    # El QR contiene solamente un identificador aleatorio, nunca datos personales.
    payload = json.dumps({"tipo": "boleto-interprovincial", "codigo": ticket.codigo}, separators=(",", ":"))
    image = qrcode.make(payload)
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="boleto-{reservation.id}.png"'},
    )


@router.post("/validar", summary="Validar un boleto en el abordaje")
def validate_ticket(
    payload: ValidarBoletoRequest,
    db: Session = Depends(get_db),
    _user: Usuario = Depends(require_roles(*STAFF_ROLES)),
) -> dict[str, object]:
    ticket = db.scalar(select(Boleto).where(Boleto.codigo == payload.codigo))
    if ticket is None:
        raise HTTPException(status_code=404, detail="Código de boleto inválido")
    reservation = db.get(Reserva, ticket.reserva_id)
    if (
        reservation is None
        or reservation.estado != "CONFIRMADA"
        or not _approved_payment_exists(db, ticket.reserva_id)
    ):
        raise HTTPException(status_code=409, detail="El boleto no está habilitado para abordar")
    return {
        "valido": True,
        "reserva_id": reservation.id,
        "fecha_viaje": reservation.fecha_viaje,
        "asiento": reservation.asiento,
    }
