"""Selección geográfica del catálogo INEC y recorridos realmente configurados."""
import json
import unicodedata
from pathlib import Path
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.core_models import Ruta, Frecuencia, Bus, Cooperativa
from app.services.operacion import puntos_ruta

router = APIRouter(tags=['destinos'])
CATALOGO = json.loads((Path(__file__).resolve().parents[2] / 'data' / 'ubicaciones_ecuador.json').read_text())


def normalizar(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.strip().casefold()) if unicodedata.category(c) != 'Mn')


@router.get('/ubicaciones')
def ubicaciones():
    return CATALOGO


@router.get('/destinos')
def destinos(db: Session = Depends(get_db)):
    indice = {}
    for provincia in CATALOGO['provincias']:
        for ciudad in provincia['ciudades']:
            item = {'ciudad_id':ciudad['id'], 'ciudad':ciudad['nombre'], 'provincia_id':provincia['id'], 'provincia':provincia['nombre']}
            for alias in [ciudad['valor'], *ciudad['alias']]:
                indice[normalizar(alias)] = item
    rutas = db.scalars(select(Ruta).join(Frecuencia, Frecuencia.ruta_id == Ruta.id)
        .join(Bus, Bus.id == Frecuencia.bus_id).join(Cooperativa, Cooperativa.id == Bus.cooperativa_id)
        .where(Ruta.activo.is_(True), Frecuencia.activo.is_(True), Bus.activo.is_(True), Cooperativa.activo.is_(True)).distinct())
    ciudades, conexiones, sin_clasificar = {}, set(), set()
    for ruta in rutas:
        puntos = puntos_ruta(db, ruta)
        for i, p in enumerate(puntos):
            clave = normalizar(p[0])
            if clave not in indice:
                sin_clasificar.add(p[0])
                continue
            ciudades[p[0]] = {**indice[clave], 'valor':p[0]}
            for destino in puntos[i+1:]:
                if normalizar(destino[0]) in indice:
                    conexiones.add((p[0],destino[0]))
    return {'ciudades':sorted(ciudades.values(), key=lambda c:(c['provincia'],c['ciudad'])),
        'conexiones':[{'origen':o,'destino':d} for o,d in sorted(conexiones)],
        'sin_clasificar':sorted(sin_clasificar)}
