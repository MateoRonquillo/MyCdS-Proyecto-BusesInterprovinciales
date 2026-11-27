"""Demostración optativa e idempotente. Nunca se ejecuta durante el arranque."""
import argparse
import base64
import os
import secrets
from datetime import time, timedelta
from io import BytesIO

from PIL import Image, ImageDraw
from pwdlib import PasswordHash
from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.core_models import (
    Abordaje, Boleto, Bus, Cooperativa, Frecuencia, Jornada, Pago,
    PagoEstadoHistorial, Parada, Reserva, Ruta, Usuario,
)
from app.services.operacion import hoy, notificar, sincronizar_ocupacion, puntos_ruta
from app.services.tarifas import TipoPasajero, calcular_pasajero

DEMO_PASSWORD = "DemoPasajes2026!"
CUENTAS = [
    ("admin", "admin", "Administración demo", 1),
    ("cooperativa", "cooperativa", "Gestión Sierra demo", 2),
    ("oficinista", "oficinista", "Oficina demo", 3),
    ("cliente", "cliente", "Cliente principal demo", 4),
    ("chofer", "chofer", "Chofer Sierra demo", 5),
    ("ayudante", "ayudante", "Ayudante Sierra demo", 6),
    ("cliente2", "cliente", "Segundo cliente demo", 7),
]


def cedula_demo(numero):
    """Identificadores sintéticos para probar el dígito verificador, no identidad real."""
    base = f"170{numero:06d}"
    suma = sum((int(c) * 2 - 9 if int(c) * 2 > 9 else int(c) * 2) if i % 2 == 0 else int(c) for i, c in enumerate(base))
    return base + str((10 - suma % 10) % 10)


def comprobante_demo():
    imagen = Image.new("RGB", (700, 220), "white")
    dibujo = ImageDraw.Draw(imagen)
    dibujo.text((30, 35), "COMPROBANTE DE DEMOSTRACION", fill="black")
    dibujo.text((30, 80), "SIN VALIDEZ BANCARIA - DATOS SINTETICOS", fill="red")
    dibujo.text((30, 125), "Ejemplo para practicar revision, aprobacion y rechazo.", fill="black")
    archivo = BytesIO()
    imagen.save(archivo, format="PNG")
    return "data:image/png;base64," + base64.b64encode(archivo.getvalue()).decode("ascii")


def _obtener_o_crear(db, modelo, criterio, **datos):
    obj = db.scalar(select(modelo).filter_by(**criterio))
    if obj is None:
        obj = modelo(**criterio, **datos)
        db.add(obj)
        db.flush()
    return obj


def run_seed(db, password=DEMO_PASSWORD):
    if len(password) < 12:
        raise ValueError("La contraseña demo debe tener al menos 12 caracteres")
    cooperativas = [
        _obtener_o_crear(db, Cooperativa, {"nombre": nombre}, color_principal=color)
        for nombre, color in [("DEMO Sierra Centro", "#146d83"), ("DEMO Costa Express", "#c27913"), ("DEMO Austro", "#6c48a0")]
    ]
    usuarios = {}
    for alias, rol, nombre, numero in CUENTAS:
        correo = f"{alias}.demo@example.test"
        coop_id = cooperativas[0].id if rol in {"cooperativa", "chofer", "ayudante"} else None
        user = db.scalar(select(Usuario).where(Usuario.correo == correo))
        if user is None:
            if db.scalar(select(Usuario.id).where(Usuario.cedula == cedula_demo(numero))):
                raise ValueError("Una cédula sintética ya pertenece a otra cuenta; no se modificó esa cuenta")
            user = Usuario(nombre=nombre, correo=correo, cedula=cedula_demo(numero), rol=rol,
                cooperativa_id=coop_id, password_hash=PasswordHash.recommended().hash(password))
            db.add(user)
            db.flush()
        elif user.rol != rol or user.cooperativa_id != coop_id or user.cedula != cedula_demo(numero):
            raise ValueError(f"La cuenta {correo} ya existe con otro perfil; no se sobrescribirá")
        # Una segunda ejecución conserva contraseña, estado y perfil existentes.
        usuarios[alias] = user

    rutas_datos = [
        ("Quito", "Cuenca", 8, [("Latacunga", 90, .25), ("Riobamba", 210, .5)]),
        ("Ambato", "Quito", 2.5, [("Latacunga", 60, .4)]),
        ("Guayaquil", "Cuenca", 4, []),
        ("Quito", "Loja", 12, [("Latacunga", 90, .15), ("Riobamba", 210, .35), ("Cuenca", 480, .7)]),
    ]
    rutas = []
    for origen, destino, duracion, paradas in rutas_datos:
        # Solo reutiliza itinerarios idénticos; nunca añade paradas a rutas vendidas.
        ruta = next((r for r in db.scalars(select(Ruta).where(Ruta.origen == origen, Ruta.destino == destino,
            Ruta.duracion_estimada_horas == duracion)) if [(p.ciudad, p.minutos, round(p.proporcion_tarifa, 6)) for p in db.scalars(select(Parada).where(Parada.ruta_id == r.id).order_by(Parada.orden))] == paradas), None)
        if ruta is None:
            ruta = Ruta(origen=origen, destino=destino, duracion_estimada_horas=duracion)
            db.add(ruta)
            db.flush()
            for orden, (ciudad, minutos, proporcion) in enumerate(paradas, 1):
                db.add(Parada(ruta_id=ruta.id, orden=orden, ciudad=ciudad, minutos=minutos, proporcion_tarifa=proporcion))
            db.flush()
        rutas.append(ruta)

    frecuencias = []
    # Un bus por frecuencia; las de Sierra pertenecen a las cuentas internas demo.
    planes = [(0, 0, time(8), 20), (0, 0, time(13), 22), (0, 1, time(10), 5),
              (1, 2, time(9), 12), (2, 3, time(6), 30), (0, 1, time(16), 6)]
    for numero, (coop, ruta, hora, tarifa) in enumerate(planes, 1):
        placa = f"DEMO-{numero:03d}"
        bus = _obtener_o_crear(db, Bus, {"placa": placa}, numero_disco=f"D{numero:02d}",
            capacidad_asientos=40 if numero % 2 else 32, cooperativa_id=cooperativas[coop].id,
            chasis="Volvo" if numero % 2 else "Mercedes-Benz",
            carroceria="Marcopolo" if numero % 2 else "Busscar", asientos_vip="1,2,3,4")
        if bus.cooperativa_id != cooperativas[coop].id:
            raise ValueError(f"La placa {placa} pertenece a otro catálogo; no se sobrescribirá")
        frecuencia = _obtener_o_crear(db, Frecuencia, {"resolucion_ant": f"DEMO-SIN-VALIDEZ-{numero:03d}"},
            ruta_id=rutas[ruta].id, bus_id=bus.id, hora_salida=hora, precio=tarifa)
        if frecuencia.bus_id != bus.id or frecuencia.ruta_id != rutas[ruta].id:
            raise ValueError("Una frecuencia demo tiene otra asignación; revisar sin sobrescribir")
        frecuencias.append(frecuencia)
        for delta in range(3):
            fecha = hoy() + timedelta(days=delta)
            jornada = _obtener_o_crear(db, Jornada, {"bus_id": bus.id, "fecha": fecha},
                frecuencia_id=frecuencia.id)
            if numero == 1 and jornada.frecuencia_id == frecuencia.id:
                for alias, columna in (("chofer", Jornada.chofer_id), ("ayudante", Jornada.ayudante_id)):
                    usuario_id = usuarios[alias].id
                    if getattr(jornada, columna.key) is None and not db.scalar(
                        select(Jornada.id).where(Jornada.fecha == fecha, columna == usuario_id)
                    ):
                        setattr(jornada, columna.key, usuario_id)

    # Etiquetas persistentes para no duplicar ni restablecer compras ya revisadas.
    escenarios = [
        ("Pendiente de pago", "cliente", 0, 1, 5, 0, 3, "PENDIENTE", None, False),
        ("Transferencia por revisar", "cliente", 1, 1, 6, 0, 3, "PAGO_EN_REVISION", "PENDIENTE", False),
        ("Boleto preferencial aprobado", "cliente", 2, 1, 2, 0, 2, "CONFIRMADA", "APROBADO", False),
        ("Tramo Latacunga-Riobamba", "cliente", 0, 1, 7, 1, 2, "PENDIENTE", None, False),
        ("Abordaje disponible hoy", "cliente", 0, 0, 8, 0, 3, "CONFIRMADA", "APROBADO", False),
        ("Abordaje ya utilizado hoy", "cliente", 0, 0, 9, 0, 3, "CONFIRMADA", "APROBADO", True),
        ("Reserva cancelada", "cliente", 3, 1, 4, 0, 1, "CANCELADA", None, False),
        ("Deposito rechazado para reintentar", "cliente", 4, 2, 10, 0, 4, "PENDIENTE", "RECHAZADO", False),
        ("Compra privada del segundo cliente", "cliente2", 5, 1, 3, 0, 2, "CONFIRMADA", "APROBADO", False),
    ]
    creadas = 0
    for etiqueta, alias, indice, delta, asiento, origen, destino, estado, estado_pago, usado in escenarios:
        usuario = usuarios[alias]
        fecha = hoy() + timedelta(days=delta)
        marcador = f"DEMO: {etiqueta}"
        if db.scalar(select(Reserva.id).where(Reserva.usuario_id == usuario.id, Reserva.pasajero_nombre == marcador,
                                             Reserva.fecha_viaje == fecha)):
            continue
        frecuencia = frecuencias[indice]
        puntos = puntos_ruta(db, rutas[planes[indice][1]])
        tipo = TipoPasajero.ADULTO_MAYOR if "preferencial" in etiqueta else TipoPasajero.GENERAL
        base = round(frecuencia.precio * (puntos[destino][2] - puntos[origen][2]), 2)
        _, _, precio = calcular_pasajero(base, tipo)
        reserva = Reserva(usuario_id=usuario.id, frecuencia_id=frecuencia.id, fecha_viaje=fecha,
            asiento=asiento, origen_orden=origen, destino_orden=destino, precio=float(precio),
            estado=estado, tipo_pasajero=tipo.value, pasajero_nombre=marcador, pasajero_cedula=usuario.cedula)
        db.add(reserva)
        db.flush()
        sincronizar_ocupacion(db, reserva)
        if estado_pago:
            pago = Pago(reserva_id=reserva.id, registrado_por_id=usuario.id, metodo_pago="TRANSFERENCIA",
                monto=reserva.precio, referencia=f"DEMO-REF-{reserva.id}", estado=estado_pago,
                comprobante=comprobante_demo(), revisado_por_id=usuarios["oficinista"].id if estado_pago != "PENDIENTE" else None,
                motivo_rechazo="DEMO: comprobante ilegible, vuelva a adjuntarlo" if estado_pago == "RECHAZADO" else None)
            db.add(pago)
            db.flush()
            db.add(PagoEstadoHistorial(pago_id=pago.id, estado_anterior=None, estado_nuevo="PENDIENTE", cambiado_por_id=usuario.id))
            if estado_pago != "PENDIENTE":
                db.add(PagoEstadoHistorial(pago_id=pago.id, estado_anterior="PENDIENTE", estado_nuevo=estado_pago,
                    cambiado_por_id=usuarios["oficinista"].id, motivo=pago.motivo_rechazo))
        if estado == "CONFIRMADA":
            boleto = Boleto(reserva_id=reserva.id, codigo=secrets.token_urlsafe(32))
            db.add(boleto)
            db.flush()
            if usado:
                db.add(Abordaje(boleto_id=boleto.id, registrado_por_id=usuarios["chofer"].id))
        notificar(db, usuario.id, f"{marcador}. Estado: {estado}. Datos sintéticos de demostración.")
        creadas += 1
    db.commit()
    return {"cuentas": len(usuarios), "cooperativas": len(cooperativas), "frecuencias": len(frecuencias), "compras_nuevas": creadas}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Autoriza cargar cuentas y compras sintéticas en este entorno local")
    args = parser.parse_args()
    if not args.demo:
        parser.error("La carga es optativa: añada --demo únicamente en desarrollo o demostración")
    with SessionLocal() as db:
        try:
            resultado = run_seed(db, os.getenv("DEMO_PASSWORD", DEMO_PASSWORD))
        except Exception:
            db.rollback()
            raise
    print(f"Demostración cargada: {resultado}")
    print("Credenciales y escenarios: docs/datos-demo.md. Las cuentas existentes conservan su contraseña.")


if __name__ == "__main__":
    main()
