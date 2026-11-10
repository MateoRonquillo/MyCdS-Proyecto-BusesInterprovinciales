"""Catálogos persistentes y administración con alcance por cooperativa."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_roles
from app.core.roles import Role, normalize_role
from app.db.database import get_db
from app.models.core_models import Bus, Cooperativa, Frecuencia, Ruta, Parada, Reserva, Jornada, Usuario, Configuracion, Notificacion
from app.schemas.gestion import BusDatos, CooperativaDatos, FrecuenciaDatos, RutaDatos, JornadaDatos, TripulacionJornadaDatos, ConfiguracionDatos
from app.services.operacion import hoy

router = APIRouter(tags=["gestión"])
GESTORES = (Role.ADMINISTRADOR, Role.USUARIO_COOPERATIVA)


def serializar(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def verificar_alcance(db, user, cooperativa_id):
    if normalize_role(user.rol) != "admin" and (not user.cooperativa_id or user.cooperativa_id != cooperativa_id):
        raise HTTPException(403, "La operación requiere pertenecer a esta cooperativa")


def guardar(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "El registro está duplicado o tiene relaciones que impiden esta operación") from None


def configurar_catalogo(nombre, modelo, esquema, roles):
    def alcance(db, user, obj):
        if modelo == Bus:
            verificar_alcance(db, user, obj.cooperativa_id)
        elif modelo == Frecuencia:
            bus = db.get(Bus, obj.bus_id)
            if not bus:
                raise HTTPException(422, "Bus no encontrado")
            verificar_alcance(db, user, bus.cooperativa_id)

    def representar(db, obj):
        datos = serializar(obj)
        if modelo == Ruta:
            datos["paradas"] = [serializar(p) for p in db.scalars(select(Parada).where(Parada.ruta_id == obj.id).order_by(Parada.orden))]
        return datos

    def listar(db: Session = Depends(get_db), user: Usuario = Depends(require_roles(*roles))):
        objetos = list(db.scalars(select(modelo).order_by(modelo.id)))
        if normalize_role(user.rol) != "admin" and modelo in (Bus, Frecuencia):
            ids = set(db.scalars(select(Bus.id).where(Bus.cooperativa_id == user.cooperativa_id))) if user.cooperativa_id else set()
            objetos = [o for o in objetos if (o.cooperativa_id == user.cooperativa_id if modelo == Bus else o.bus_id in ids)]
        return [representar(db, o) for o in objetos]

    def aplicar(db, user, payload, obj=None):
        datos = payload.model_dump(exclude={"paradas"})
        nuevo = modelo(**datos)
        alcance(db, user, nuevo)
        if obj:
            alcance(db, user, obj)
        if modelo == Bus:
            if not db.get(Cooperativa, nuevo.cooperativa_id):
                raise HTTPException(422, "Cooperativa no encontrada")
            if obj and (obj.capacidad_asientos != nuevo.capacidad_asientos or obj.cooperativa_id != nuevo.cooperativa_id or obj.asientos_vip != nuevo.asientos_vip):
                if db.scalar(select(Reserva.id).join(Frecuencia, Frecuencia.id == Reserva.frecuencia_id).where(Frecuencia.bus_id == obj.id).limit(1)):
                    raise HTTPException(409, "No se puede cambiar capacidad, plantilla o cooperativa de un bus con reservas")
        if modelo == Frecuencia:
            if not db.get(Ruta, nuevo.ruta_id):
                raise HTTPException(422, "Ruta no encontrada")
            if obj and any(getattr(obj, c) != datos[c] for c in ("ruta_id", "bus_id", "hora_salida", "precio")):
                if db.scalar(select(Reserva.id).where(Reserva.frecuencia_id == obj.id).limit(1)):
                    raise HTTPException(409, "La frecuencia tiene reservas; cree otra para cambiar su operación")
        if modelo == Ruta and obj:
            if db.scalar(select(Frecuencia.id).where(Frecuencia.ruta_id == obj.id).limit(1)):
                # Las rutas vinculadas conservan el itinerario vendido.
                actuales = representar(db, obj)
                paradas = [{k: p[k] for k in ("ciudad", "minutos", "proporcion_tarifa")} for p in actuales["paradas"]]
                if paradas != [p.model_dump() for p in payload.paradas] or any(getattr(obj, c) != datos[c] for c in ("origen", "destino", "duracion_estimada_horas")):
                    raise HTTPException(409, "El itinerario ya tiene frecuencias; cree otra ruta para modificarlo")
        if obj is None:
            obj = nuevo
            db.add(obj)
        else:
            for k, v in datos.items():
                setattr(obj, k, v)
        db.flush()
        if modelo == Ruta:
            db.execute(delete(Parada).where(Parada.ruta_id == obj.id))
            for orden, parada in enumerate(payload.paradas, 1):
                db.add(Parada(ruta_id=obj.id, orden=orden, **parada.model_dump()))
        guardar(db)
        db.refresh(obj)
        return representar(db, obj)

    def crear(payload, db: Session = Depends(get_db), user: Usuario = Depends(require_roles(*roles))):
        try:
            return aplicar(db, user, payload)
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "El registro está duplicado") from None

    def actualizar(item_id: int, payload, db: Session = Depends(get_db), user: Usuario = Depends(require_roles(*roles))):
        obj = db.get(modelo, item_id)
        if not obj:
            raise HTTPException(404, "Registro no encontrado")
        try:
            return aplicar(db, user, payload, obj)
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "El registro está duplicado") from None

    def eliminar(item_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_roles(*roles))):
        obj = db.get(modelo, item_id)
        if not obj:
            raise HTTPException(404, "Registro no encontrado")
        alcance(db, user, obj)
        # Baja lógica: conserva boletos e historial.
        obj.activo = False
        guardar(db)
        return Response(status_code=204)

    crear.__annotations__["payload"] = esquema
    actualizar.__annotations__["payload"] = esquema
    for endpoint, path, methods, code in [(listar, "", ["GET"], 200), (crear, "", ["POST"], 201), (actualizar, "/{item_id}", ["PUT"], 200), (eliminar, "/{item_id}", ["DELETE"], 204)]:
        endpoint.__name__ = f"{endpoint.__name__}_{nombre}"
        router.add_api_route(f"/{nombre}{path}", endpoint, methods=methods, status_code=code)


configurar_catalogo("cooperativas", Cooperativa, CooperativaDatos, (Role.ADMINISTRADOR,))
configurar_catalogo("buses", Bus, BusDatos, GESTORES)
configurar_catalogo("rutas", Ruta, RutaDatos, (Role.ADMINISTRADOR,))
configurar_catalogo("frecuencias", Frecuencia, FrecuenciaDatos, GESTORES)


@router.get("/jornadas")
def listar_jornadas(fecha: date, db: Session = Depends(get_db), user: Usuario = Depends(require_roles(*GESTORES))):
    query = select(Jornada).join(Bus, Bus.id == Jornada.bus_id).where(Jornada.fecha == fecha)
    if normalize_role(user.rol) != "admin":
        query = query.where(Bus.cooperativa_id == (user.cooperativa_id or -1))
    return [serializar(j) for j in db.scalars(query)]


def verificar_tripulante(db, usuario_id, bus, frecuencia_id, rol):
    if usuario_id is None:
        return
    persona = db.get(Usuario, usuario_id)
    if (not frecuencia_id or not persona or not persona.activo
            or normalize_role(persona.rol) != rol
            or persona.cooperativa_id != bus.cooperativa_id):
        raise HTTPException(422, f"Seleccione un {rol} activo de la cooperativa del bus y una salida")


@router.patch("/jornadas/{item_id}/chofer")
@router.patch("/jornadas/{item_id}/tripulacion")
def asignar_tripulacion(item_id: int, payload: TripulacionJornadaDatos, db: Session = Depends(get_db),
                        user: Usuario = Depends(require_roles(*GESTORES))):
    jornada = db.scalar(select(Jornada).where(Jornada.id == item_id).with_for_update())
    if not jornada:
        raise HTTPException(404, "Jornada no encontrada")
    if jornada.fecha < hoy():
        raise HTTPException(409, "No se puede modificar una jornada pasada")
    bus = db.get(Bus, jornada.bus_id)
    verificar_alcance(db, user, bus.cooperativa_id)
    cambios = payload.model_dump(exclude_unset=True)
    for campo, rol in (("chofer_id", Role.CHOFER), ("ayudante_id", Role.AYUDANTE)):
        if campo in cambios:
            verificar_tripulante(db, cambios[campo], bus, jornada.frecuencia_id, rol)
            setattr(jornada, campo, cambios[campo])
    guardar(db)
    return serializar(jornada)


@router.post("/jornadas", status_code=201)
def crear_jornada(payload: JornadaDatos, db: Session = Depends(get_db), user: Usuario = Depends(require_roles(*GESTORES))):
    if payload.fecha < hoy():
        raise HTTPException(422, "No se puede planificar en el pasado")
    bus = db.scalar(select(Bus).where(Bus.id == payload.bus_id).with_for_update())
    if not bus or not bus.activo:
        raise HTTPException(422, "Bus no disponible")
    verificar_alcance(db, user, bus.cooperativa_id)
    if payload.frecuencia_id:
        f = db.get(Frecuencia, payload.frecuencia_id)
        if not f or not f.activo or f.bus_id != bus.id:
            raise HTTPException(422, "Seleccione una frecuencia activa asignada a este bus")
    if db.scalar(select(Reserva.id).join(Frecuencia, Frecuencia.id == Reserva.frecuencia_id).where(Frecuencia.bus_id == bus.id, Reserva.fecha_viaje == payload.fecha, Reserva.estado.notin_(["CANCELADA", "EXPIRADA"]), Reserva.frecuencia_id != (payload.frecuencia_id or -1)).limit(1)):
        raise HTTPException(409, "La planificación dejaría reservas existentes sin salida")
    verificar_tripulante(db, payload.chofer_id, bus, payload.frecuencia_id, Role.CHOFER)
    verificar_tripulante(db, payload.ayudante_id, bus, payload.frecuencia_id, Role.AYUDANTE)
    j = Jornada(**payload.model_dump())
    db.add(j)
    guardar(db)
    db.refresh(j)
    return serializar(j)


@router.delete("/jornadas/{item_id}", status_code=204)
def eliminar_jornada(item_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_roles(*GESTORES))):
    j = db.get(Jornada, item_id)
    if not j:
        raise HTTPException(404, "Jornada no encontrada")
    verificar_alcance(db, user, db.get(Bus, j.bus_id).cooperativa_id)
    if j.fecha < hoy():
        raise HTTPException(409, "No se puede eliminar una jornada pasada")
    db.delete(j)
    guardar(db)
    return Response(status_code=204)


@router.get("/configuracion")
def leer_configuracion(db: Session = Depends(get_db)):
    obj = db.get(Configuracion, 1)
    return serializar(obj) if obj else dict(id=1, nombre="Pasajes EC", logo_url=None, color_principal="#146d83", soporte="", redes_sociales="")


@router.put("/configuracion")
def editar_configuracion(payload: ConfiguracionDatos, db: Session = Depends(get_db), user: Usuario = Depends(require_roles(Role.ADMINISTRADOR))):
    obj = db.get(Configuracion, 1)
    if not obj:
        obj = Configuracion(id=1)
        db.add(obj)
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    guardar(db)
    return serializar(obj)


@router.get("/notificaciones")
def listar_notificaciones(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return [serializar(n) for n in db.scalars(select(Notificacion).where(Notificacion.usuario_id == user.id).order_by(Notificacion.id.desc()).limit(100))]


@router.patch("/notificaciones/{item_id}/leer", status_code=204)
def leer_notificacion(item_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    n = db.get(Notificacion, item_id)
    if not n or n.usuario_id != user.id:
        raise HTTPException(404, "Notificación no encontrada")
    n.leida = True
    guardar(db)
    return Response(status_code=204)
