import unicodedata
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.core_models import Bus, Cooperativa, Frecuencia, Reserva, Ruta
from app.schemas.viajes import CooperativaViaje, ViajeResponse, ViajesResponse

router = APIRouter(prefix="/viajes", tags=["viajes"])


def _norm(texto: str) -> str:
    """Minúsculas y sin tildes, para comparar ciudades."""
    sin_tildes = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn").strip().lower()


@router.get(
    "",
    response_model=ViajesResponse,
    summary="Buscar viajes por origen, destino y fecha",
)
def search_trips(
    origen: str = Query(min_length=1),
    destino: str = Query(min_length=1),
    fecha: date = Query(..., description="Fecha del viaje (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
) -> ViajesResponse:
    if fecha < date.today():
        raise HTTPException(status_code=422, detail="La fecha del viaje no puede estar en el pasado")

    wanted_from, wanted_to = _norm(origen), _norm(destino)
    rutas = {
        r.id: r
        for r in db.scalars(select(Ruta).where(Ruta.activo.is_(True)))
        if _norm(r.origen) == wanted_from and _norm(r.destino) == wanted_to
    }
    if not rutas:
        return ViajesResponse(items=[], total=0)

    filas = db.execute(
        select(Frecuencia, Bus, Cooperativa)
        .join(Bus, Bus.id == Frecuencia.bus_id)
        .join(Cooperativa, Cooperativa.id == Bus.cooperativa_id)
        .where(
            Frecuencia.ruta_id.in_(list(rutas)),
            Frecuencia.activo.is_(True),
            Bus.activo.is_(True),
        )
        .order_by(Frecuencia.hora_salida)
    ).all()

    ocupados: dict[int, int] = {}
    if filas:
        ocupados = dict(
            db.execute(
                select(Reserva.frecuencia_id, func.count(Reserva.id))
                .where(
                    Reserva.frecuencia_id.in_([f.id for f, _, _ in filas]),
                    Reserva.fecha_viaje == fecha,
                    Reserva.estado != "CANCELADA",
                )
                .group_by(Reserva.frecuencia_id)
            ).all()
        )

    items = []
    for frecuencia, bus, coop in filas:
        ruta = rutas[frecuencia.ruta_id]
        duracion = round(ruta.duracion_estimada_horas * 60)
        salida = datetime.combine(fecha, frecuencia.hora_salida)
        llegada = salida + timedelta(minutes=duracion)
        items.append(
            ViajeResponse(
                id=frecuencia.id,
                cooperativa=CooperativaViaje(
                    id=coop.id,
                    nombre=coop.nombre,
                    color_principal=coop.color_principal,
                    logo_url=coop.logo_url,
                ),
                origen=ruta.origen,
                destino=ruta.destino,
                fecha=fecha,
                hora_salida=salida.strftime("%H:%M"),
                hora_llegada=llegada.strftime("%H:%M"),
                duracion_min=duracion,
                precio=round(frecuencia.precio, 2),
                asientos_disponibles=max(0, bus.capacidad_asientos - ocupados.get(frecuencia.id, 0)),
            )
        )
    return ViajesResponse(items=items, total=len(items))