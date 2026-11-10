import json
import base64
from html import escape
from datetime import datetime, timezone, timedelta
from io import BytesIO

import qrcode
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import get_current_user, require_roles
from app.core.roles import Role, normalize_role
from app.db.database import get_db
from app.services.operacion import hoy, puntos_ruta, notificar
from app.models.core_models import Abordaje, Bus, Cooperativa, Frecuencia, Ruta, Boleto, Pago, Reserva, Usuario

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

    _verificar_personal(db, reservation, user)
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
    _verificar_personal(db, reservation, _user)
    if reservation.fecha_viaje != hoy():
        raise HTTPException(409, "El boleto no corresponde a la fecha de hoy")
    if db.scalar(select(Abordaje.id).where(Abordaje.boleto_id == ticket.id)):
        raise HTTPException(409, "El boleto ya fue utilizado")
    frecuencia = db.get(Frecuencia, reservation.frecuencia_id)
    bus = db.get(Bus, frecuencia.bus_id)
    puntos = puntos_ruta(db, db.get(Ruta, frecuencia.ruta_id))
    return {
        "pasajero": reservation.pasajero_nombre,
        "tipo_pasajero": reservation.tipo_pasajero,
        "origen": puntos[reservation.origen_orden][0],
        "destino": puntos[reservation.destino_orden][0],
        "bus": f"{bus.numero_disco} · {bus.placa}",
        "valido": True,
        "reserva_id": reservation.id,
        "fecha_viaje": reservation.fecha_viaje,
        "asiento": reservation.asiento,
    }



def _verificar_personal(db, reservation, user):
    if normalize_role(user.rol) in {"chofer", "ayudante"}:
        frecuencia = db.get(Frecuencia, reservation.frecuencia_id)
        bus = db.get(Bus, frecuencia.bus_id)
        if not user.cooperativa_id or bus.cooperativa_id != user.cooperativa_id:
            raise HTTPException(403, "El boleto pertenece a otra cooperativa")


@router.post("/abordar", status_code=201)
def registrar_abordaje(payload: ValidarBoletoRequest, db: Session = Depends(get_db), user: Usuario = Depends(require_roles(*STAFF_ROLES))):
    datos = validate_ticket(payload, db, user)
    ticket = db.scalar(select(Boleto).where(Boleto.codigo == payload.codigo))
    db.add(Abordaje(boleto_id=ticket.id, registrado_por_id=user.id))
    reserva = db.get(Reserva, ticket.reserva_id)
    notificar(db, reserva.usuario_id, f"Abordaje registrado para reserva {reserva.id}.")
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "El boleto ya fue utilizado") from None
    return {**datos, "abordaje_registrado": True}


@router.get("/{reserva_id}/descarga", response_class=HTMLResponse)
def descargar_boleto(reserva_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    # Reutiliza los controles de propiedad, pago y confirmación del QR.
    get_ticket_qr(reserva_id, db, user)
    r = db.get(Reserva, reserva_id)
    ticket = db.scalar(select(Boleto).where(Boleto.reserva_id == r.id))
    f = db.get(Frecuencia, r.frecuencia_id)
    bus = db.get(Bus, f.bus_id)
    puntos = puntos_ruta(db, db.get(Ruta, f.ruta_id))
    image = qrcode.make(json.dumps({"tipo": "boleto-interprovincial", "codigo": ticket.codigo}, separators=(",", ":")))
    out = BytesIO()
    image.save(out, format="PNG")
    qr = base64.b64encode(out.getvalue()).decode("ascii")
    cooperativa = db.get(Cooperativa, bus.cooperativa_id)
    salida = datetime.combine(r.fecha_viaje, f.hora_salida) + timedelta(minutes=puntos[r.origen_orden][1])
    llegada = datetime.combine(r.fecha_viaje, f.hora_salida) + timedelta(minutes=puntos[r.destino_orden][1])
    asiento_tipo = "VIP" if str(r.asiento) in bus.asientos_vip.split(",") else "Normal"
    css = """
    *{box-sizing:border-box}body{margin:0;padding:40px 20px;background:#f1f3ef;color:#20362e;font:14px Arial,sans-serif}
    main{max-width:740px;margin:auto;background:white;border:1px solid #dce4dc;border-radius:12px;overflow:hidden}
    header{padding:28px 32px;border-bottom:1px solid #dce4dc;display:flex;justify-content:space-between;align-items:center;gap:15px}
    .brand{font-size:20px;font-weight:700}.label{text-transform:uppercase;font-size:10px;letter-spacing:1.5px;color:#64786d}
    .body{padding:32px}.route{display:flex;justify-content:space-between;gap:20px;align-items:center;margin:20px 0 30px}
    h1{font-size:28px;font-weight:500;letter-spacing:-1px;margin:0}h2{font-size:22px;margin:8px 0;font-weight:500}
    .badge{background:#e6f2e9;color:#215a39;padding:7px 10px;border-radius:5px;font-size:11px;white-space:nowrap}
    .details{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;padding:22px 0;border-block:1px solid #dce4dc}
    .details strong{display:block;font-size:14px;margin-top:7px;font-weight:500}.access{display:grid;grid-template-columns:1fr 180px;align-items:center;gap:25px;padding-top:25px}
    .access img{width:180px;height:180px}.price{font-size:30px;font-weight:500;letter-spacing:-1px}.note{font-size:12px;line-height:1.7;color:#64786d}
    footer{border-top:1px dashed #dce4dc;background:#f8faf6;padding:20px 32px;font-size:11px;line-height:1.8;color:#64786d}
    @media(max-width:540px){body{padding:15px}.body,header,footer{padding:22px}.route h2{font-size:18px}.details{grid-template-columns:1fr 1fr}.access{grid-template-columns:1fr}.access img{margin:auto}}
    @media print{body{padding:0;background:white}main{max-width:none;border:1px solid #dce4dc;break-inside:avoid}@page{size:A5;margin:10mm}}
    """
    def campo(etiqueta, valor):
        return f'<div><span class="label">{escape(etiqueta)}</span><strong>{escape(str(valor))}</strong></div>'
    campos = "".join([
        campo("Pasajero", r.pasajero_nombre or "No registrado"), campo("Documento", r.pasajero_cedula or "No registrado"),
        campo("Asiento", f"{r.asiento} · {asiento_tipo}"), campo("Salida", salida.strftime("%d/%m/%Y · %H:%M")),
        campo("Llegada estimada", llegada.strftime("%d/%m/%Y · %H:%M")), campo("Bus", f"{bus.numero_disco} · {bus.placa}")])
    html = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Boleto {r.id}</title><style>{css}</style></head>
    <body><main><header><div><div class="brand">{escape(cooperativa.nombre)}</div><p class="label">Transporte interprovincial · Ecuador</p></div><span class="badge">Boleto confirmado · #{r.id:06d}</span></header>
    <div class="body"><p class="label">Tu próximo viaje</p><h1>Boleto de viaje</h1><div class="route"><div><span class="label">Origen</span><h2>{escape(puntos[r.origen_orden][0])}</h2></div><span aria-hidden="true">→</span><div><span class="label">Destino</span><h2>{escape(puntos[r.destino_orden][0])}</h2></div></div>
    <div class="details">{campos}</div><div class="access"><div><p class="label">Total pagado</p><div class="price">USD {r.precio:.2f}</div><p class="note">Tarifa: {escape(r.tipo_pasajero.replace('_', ' ').lower())}.<br>Presenta tu cédula y este código al abordar.<br>El acceso se registra una sola vez.</p></div><img alt="Código QR de abordaje del boleto {r.id}" src="data:image/png;base64,{qr}"></div></div>
    <footer>Conserva este boleto en tu dispositivo o imprímelo desde el navegador. La llegada es estimada. Este documento acredita el viaje y no sustituye un comprobante tributario.</footer></main></body></html>'''
    return HTMLResponse(html, headers={"Content-Disposition": f'attachment; filename="boleto-{r.id}.html"', "Cache-Control": "no-store"})
