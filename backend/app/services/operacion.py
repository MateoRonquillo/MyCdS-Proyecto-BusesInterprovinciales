"""Reglas compartidas para rutas, ocupación por tramo y avisos transaccionales."""
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.core_models import Bus, Cooperativa, Frecuencia, Jornada, Notificacion, OcupacionAsiento, Parada, Reserva, Ruta


def hoy():
    return datetime.now(ZoneInfo("America/Guayaquil")).date()


def puntos_ruta(db: Session, ruta: Ruta):
    paradas = list(db.scalars(select(Parada).where(Parada.ruta_id == ruta.id).order_by(Parada.orden)))
    return [(ruta.origen, 0, 0.0)] + [(p.ciudad, p.minutos, p.proporcion_tarifa) for p in paradas] + [(ruta.destino, round(ruta.duracion_estimada_horas * 60), 1.0)]


def tramo(db, frecuencia, origen=0, destino=None):
    ruta = db.get(Ruta, frecuencia.ruta_id)
    if ruta is None or not ruta.activo:
        raise HTTPException(409, "La ruta no está disponible")
    puntos = puntos_ruta(db, ruta)
    destino = len(puntos) - 1 if destino is None else destino
    if not 0 <= origen < destino < len(puntos):
        raise HTTPException(422, "El tramo de viaje no es válido")
    return puntos, destino


def bus_disponible(db, frecuencia, fecha):
    bus = db.get(Bus, frecuencia.bus_id)
    coop = db.get(Cooperativa, bus.cooperativa_id) if bus else None
    if not bus or not bus.activo or not coop or not coop.activo:
        raise HTTPException(409, "El bus de esta frecuencia no está disponible")
    jornada = db.scalar(select(Jornada).where(Jornada.bus_id == bus.id, Jornada.fecha == fecha))
    if jornada and jornada.frecuencia_id != frecuencia.id:
        raise HTTPException(409, "El bus está en parada o asignado a otra frecuencia ese día")
    return bus


def sincronizar_ocupacion(db, reserva):
    db.execute(delete(OcupacionAsiento).where(OcupacionAsiento.reserva_id == reserva.id))
    if reserva.estado not in {"CANCELADA", "EXPIRADA"}:
        for segmento in range(reserva.origen_orden, reserva.destino_orden):
            db.add(OcupacionAsiento(reserva_id=reserva.id, frecuencia_id=reserva.frecuencia_id,
                fecha_viaje=reserva.fecha_viaje, asiento=reserva.asiento, segmento=segmento))


def notificar(db, usuario_id, mensaje):
    db.add(Notificacion(usuario_id=usuario_id, mensaje=mensaje))


def cedula_valida(cedula):
    if not cedula or len(cedula) != 10 or not cedula.isascii() or not cedula.isdigit():
        return False
    if not (1 <= int(cedula[:2]) <= 24 or cedula[:2] == "30") or int(cedula[2]) >= 6:
        return False
    total = sum((int(c) * 2 - 9 if int(c) * 2 > 9 else int(c) * 2) if i % 2 == 0 else int(c) for i, c in enumerate(cedula[:9]))
    return (10 - total % 10) % 10 == int(cedula[9])
