"""Cola transaccional de boletos y entrega por Gmail SMTP."""
import asyncio
import json
import logging
import os
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from email.errors import MessageError
from email.headerregistry import Address
from email.message import EmailMessage
from hashlib import sha256
from io import BytesIO
from uuid import uuid4

import qrcode
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.core_models import Boleto, Bus, Cooperativa, CorreoBoleto, Frecuencia, Pago, Reserva, Ruta
from app.services.operacion import hoy, puntos_ruta

logger = logging.getLogger(__name__)
MAX_INTENTOS = 5


def direccion_correo(value: str | None) -> str | None:
    if not value or len(value) > 254 or any(c.isspace() for c in value) or not value.isascii():
        return None
    try:
        address = Address(addr_spec=value)
    except (ValueError, MessageError):
        return None
    if not address.username or '.' not in address.domain or address.addr_spec != value:
        return None
    return value


def encolar_boleto(db: Session, reserva_id: int, destinatario: str | None) -> None:
    correo = direccion_correo(destinatario)
    if correo and db.get(CorreoBoleto, reserva_id) is None:
        db.add(CorreoBoleto(reserva_id=reserva_id, destinatario=correo))


def generar_qr_boleto(codigo: str) -> bytes:
    payload = json.dumps({'tipo': 'boleto-interprovincial', 'codigo': codigo}, separators=(',', ':'))
    output = BytesIO()
    qrcode.make(payload).save(output, format='PNG')
    return output.getvalue()


def _mensaje(db: Session, correo: CorreoBoleto, remitente: str) -> EmailMessage | None:
    fila = db.execute(
        select(Reserva, Boleto, Frecuencia, Bus, Ruta, Cooperativa)
        .join(Boleto, Boleto.reserva_id == Reserva.id)
        .join(Frecuencia, Frecuencia.id == Reserva.frecuencia_id)
        .join(Bus, Bus.id == Frecuencia.bus_id)
        .join(Ruta, Ruta.id == Frecuencia.ruta_id)
        .join(Cooperativa, Cooperativa.id == Bus.cooperativa_id)
        .where(Reserva.id == correo.reserva_id, Reserva.estado == 'CONFIRMADA',
               Reserva.fecha_viaje >= hoy(),
               select(Pago.id).where(Pago.reserva_id == Reserva.id, Pago.estado == 'APROBADO').exists())
    ).one_or_none()
    if fila is None:
        return None
    reserva, boleto, frecuencia, bus, ruta, cooperativa = fila
    puntos = puntos_ruta(db, ruta)
    origen, destino = puntos[reserva.origen_orden], puntos[reserva.destino_orden]
    salida = datetime.combine(reserva.fecha_viaje, frecuencia.hora_salida) + timedelta(minutes=origen[1])
    mensaje = EmailMessage()
    mensaje['From'] = Address('Pasajes EC', addr_spec=remitente)
    mensaje['To'] = Address(addr_spec=correo.destinatario)
    mensaje['Subject'] = f'Boleto confirmado #{reserva.id:06d} · Pasajes EC'
    identificador = sha256(boleto.codigo.encode()).hexdigest()
    mensaje['Message-ID'] = f'<boleto-{identificador}@{remitente.rsplit("@", 1)[1]}>'
    mensaje.set_content(
        f'Tu boleto está confirmado.\n\n'
        f'Pasajero: {reserva.pasajero_nombre or "Sin nombre registrado"}\n'
        f'Cooperativa: {cooperativa.nombre}\n'
        f'Viaje: {origen[0]} → {destino[0]}\n'
        f'Salida: {salida:%d/%m/%Y %H:%M} (hora de Ecuador continental)\n'
        f'Bus: {bus.numero_disco} · {bus.placa}\n'
        f'Asiento: {reserva.asiento}\n'
        f'Total pagado: USD {reserva.precio:.2f}\n\n'
        'Presenta el QR adjunto y tu documento de identidad al abordar. '
        'El código es personal y solo puede utilizarse una vez.\n'
    )
    mensaje.add_attachment(generar_qr_boleto(boleto.codigo), maintype='image', subtype='png',
                            filename=f'boleto-{reserva.id}.png')
    return mensaje


def _enviar(mensaje: EmailMessage, remitente: str, clave: str) -> None:
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10, context=ssl.create_default_context())
    try:
        smtp.login(remitente, clave)
        smtp.send_message(mensaje)
    finally:
        # El resultado de DATA es el que confirma la aceptación por Gmail.
        smtp.close()


def _ahora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)


def procesar_correo(remitente: str, clave: str, sesiones=SessionLocal) -> bool:
    """Reclama un correo antes de usar SMTP y permite recuperar reclamos vencidos."""
    ahora = _ahora()
    reclamo = uuid4().hex
    with sesiones() as db:
        disponible = (CorreoBoleto.estado == 'PENDIENTE', CorreoBoleto.disponible_en <= ahora)
        reserva_id = db.scalar(select(CorreoBoleto.reserva_id).where(*disponible)
                              .order_by(CorreoBoleto.disponible_en, CorreoBoleto.reserva_id).limit(1))
        if reserva_id is None:
            return False
        tomado = db.execute(update(CorreoBoleto).where(CorreoBoleto.reserva_id == reserva_id, *disponible)
                            .values(reclamo=reclamo, disponible_en=ahora + timedelta(minutes=5)))
        if tomado.rowcount != 1:
            return False
        db.commit()

    intentos = 0
    try:
        with sesiones() as db:
            correo = db.get(CorreoBoleto, reserva_id)
            if correo is None or correo.reclamo != reclamo:
                return True
            intentos = correo.intentos
            mensaje = _mensaje(db, correo, remitente)
        if mensaje is not None:
            _enviar(mensaje, remitente, clave)
        cambios = {'estado': 'ENVIADO' if mensaje is not None else 'NO_APLICA', 'reclamo': None}
    except Exception as exc:
        intentos += 1
        permanente = isinstance(exc, smtplib.SMTPRecipientsRefused) and all(
            codigo >= 500 for codigo, _ in exc.recipients.values())
        cambios = {'intentos': intentos, 'reclamo': None,
                   'estado': 'FALLIDO' if permanente or intentos >= MAX_INTENTOS else 'PENDIENTE',
                   'disponible_en': _ahora() + timedelta(seconds=30 * 2 ** (intentos - 1))}
        logger.warning('Correo de boleto %s, intento %s: %s', reserva_id, intentos, type(exc).__name__)

    with sesiones() as db:
        db.execute(update(CorreoBoleto).where(CorreoBoleto.reserva_id == reserva_id,
                                             CorreoBoleto.reclamo == reclamo).values(**cambios))
        db.commit()
    return True


async def entregar_boletos(detener: asyncio.Event) -> None:
    remitente = direccion_correo(os.getenv('GMAIL_SMTP_USER', '').strip())
    clave = ''.join(os.getenv('GMAIL_SMTP_APP_PASSWORD', '').split())
    if not remitente or not clave:
        return
    while not detener.is_set():
        try:
            if await asyncio.to_thread(procesar_correo, remitente, clave):
                continue
        except Exception as exc:
            logger.warning('Cola de boletos temporalmente indisponible: %s', type(exc).__name__)
        try:
            await asyncio.wait_for(detener.wait(), timeout=5)
        except TimeoutError:
            pass
