import unicodedata
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.operacion import hoy, puntos_ruta, bus_disponible
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
    cooperativa_id: int | None = Query(None, gt=0),
    tipo_asiento: str | None = Query(None, pattern="^(NORMAL|VIP)$"),
    chasis: str | None = None,
    carroceria: str | None = None,
    tipo_viaje: str | None = Query(None, pattern="^(DIRECTO|CON_PARADAS)$"),
    db: Session = Depends(get_db),
) -> ViajesResponse:
    if fecha < hoy():
        raise HTTPException(status_code=422, detail="La fecha del viaje no puede estar en el pasado")

    wanted_from, wanted_to = _norm(origen), _norm(destino)
    rutas = {r.id: r for r in db.scalars(select(Ruta).where(Ruta.activo.is_(True)))}
    filas = db.execute(select(Frecuencia, Bus, Cooperativa)
        .join(Bus, Bus.id == Frecuencia.bus_id)
        .join(Cooperativa, Cooperativa.id == Bus.cooperativa_id)
        .where(Frecuencia.activo.is_(True), Bus.activo.is_(True), Cooperativa.activo.is_(True))
        .order_by(Frecuencia.hora_salida)).all()
    items = []
    for frecuencia, bus, coop in filas:
        ruta = rutas.get(frecuencia.ruta_id)
        if not ruta:
            continue
        puntos = puntos_ruta(db, ruta)
        desde = next((i for i, p in enumerate(puntos) if _norm(p[0]) == wanted_from), None)
        hasta = next((i for i, p in enumerate(puntos) if _norm(p[0]) == wanted_to), None)
        if desde is None or hasta is None or desde >= hasta:
            continue
        try:
            bus_disponible(db, frecuencia, fecha)
        except HTTPException:
            continue
        if cooperativa_id and coop.id != cooperativa_id:
            continue
        if chasis and _norm(chasis) not in _norm(bus.chasis):
            continue
        if carroceria and _norm(carroceria) not in _norm(bus.carroceria):
            continue
        tipo = "CON_PARADAS" if len(puntos) > 2 else "DIRECTO"
        if tipo_viaje and tipo != tipo_viaje:
            continue
        ocupados = set(db.scalars(select(Reserva.asiento).where(
            Reserva.frecuencia_id == frecuencia.id, Reserva.fecha_viaje == fecha,
            Reserva.estado.notin_(["CANCELADA", "EXPIRADA"]),
            Reserva.origen_orden < hasta, Reserva.destino_orden > desde)))
        vip = {int(n) for n in bus.asientos_vip.split(",") if n}
        elegibles = set(range(1, bus.capacidad_asientos + 1))
        if tipo_asiento == "VIP":
            elegibles &= vip
        elif tipo_asiento == "NORMAL":
            elegibles -= vip
        if tipo_asiento and not elegibles:
            continue
        salida = datetime.combine(fecha, frecuencia.hora_salida) + timedelta(minutes=puntos[desde][1])
        llegada = datetime.combine(fecha, frecuencia.hora_salida) + timedelta(minutes=puntos[hasta][1])
        items.append(ViajeResponse(
            id=frecuencia.id, cooperativa=CooperativaViaje(id=coop.id, nombre=coop.nombre, color_principal=coop.color_principal, logo_url=coop.logo_url),
            origen=puntos[desde][0], destino=puntos[hasta][0], fecha=fecha,
            hora_salida=salida.strftime("%H:%M"), hora_llegada=llegada.strftime("%H:%M"),
            duracion_min=puntos[hasta][1] - puntos[desde][1],
            precio=round(frecuencia.precio * (puntos[hasta][2] - puntos[desde][2]), 2),
            asientos_disponibles=len(elegibles - ocupados), origen_orden=desde, destino_orden=hasta,
            bus_id=bus.id, placa=bus.placa, numero_disco=bus.numero_disco, chasis=bus.chasis,
            carroceria=bus.carroceria, fotografia_url=bus.fotografia_url, tipo_viaje=tipo,
            tipos_asiento=(["VIP"] if vip else []) + (["NORMAL"] if len(vip) < bus.capacidad_asientos else []),
            asientos_vip=sorted(vip),
        ))
    return ViajesResponse(items=items, total=len(items))
