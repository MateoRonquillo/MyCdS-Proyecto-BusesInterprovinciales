from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy import Text, Column, Integer, String, Boolean, ForeignKey, Float, Time, Date, DateTime, UniqueConstraint, func
from app.db.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    cedula = Column(String(15), unique=True, nullable=False)
    rol = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True)
    cooperativa_id = Column(Integer, ForeignKey("cooperativas.id"), nullable=True)

class Cooperativa(Base):
    __tablename__ = "cooperativas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    logo_url = Column(String(255), nullable=True)
    color_principal = Column(String(7), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")

class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(20), unique=True, nullable=False)
    numero_disco = Column(String(10), nullable=False)
    capacidad_asientos = Column(Integer, nullable=False)
    cooperativa_id = Column(Integer, ForeignKey("cooperativas.id"), nullable=False)
    activo = Column(Boolean, default=True)

    chasis = Column(String(80), nullable=False, default="", server_default="")
    carroceria = Column(String(80), nullable=False, default="", server_default="")
    fotografia_url = Column(String(500), nullable=True)
    asientos_vip = Column(String(500), nullable=False, default="", server_default="")

class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
    origen = Column(String(100), nullable=False)
    destino = Column(String(100), nullable=False)
    duracion_estimada_horas = Column(Float, nullable=False)
    activo = Column(Boolean, default=True)

class Frecuencia(Base):
    __tablename__ = "frecuencias"

    id = Column(Integer, primary_key=True, index=True)
    ruta_id = Column(Integer, ForeignKey("rutas.id"), nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    hora_salida = Column(Time, nullable=False)
    precio = Column(Float, nullable=False)
    activo = Column(Boolean, default=True)

    resolucion_ant = Column(String(150), nullable=True)

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    frecuencia_id = Column(Integer, ForeignKey("frecuencias.id"), nullable=False, index=True)
    fecha_viaje = Column(Date, nullable=False)
    asiento = Column(Integer, nullable=False)
    tipo_pasajero = Column(
        String(30), nullable=False, default="GENERAL", server_default="GENERAL"
    )
    precio = Column(Float, nullable=False)
    estado = Column(String(30), nullable=False, default="PENDIENTE")

    origen_orden = Column(Integer, nullable=False, default=0, server_default="0")
    destino_orden = Column(Integer, nullable=False, default=1, server_default="1")
    pasajero_nombre = Column(String(100), nullable=True)
    pasajero_cedula = Column(String(15), nullable=True)


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False, index=True)
    registrado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    revisado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    metodo_pago = Column(String(20), nullable=False)
    monto = Column(Float, nullable=False)
    referencia = Column(String(100), nullable=True)
    estado = Column(String(20), nullable=False, default="PENDIENTE", index=True)
    motivo_rechazo = Column(String(255), nullable=True)
    comprobante = Column(Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=True)
    creado_en = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    revisado_en = Column(DateTime(timezone=True), nullable=True)


class PagoEstadoHistorial(Base):
    __tablename__ = "pagos_estado_historial"

    id = Column(Integer, primary_key=True, index=True)
    pago_id = Column(Integer, ForeignKey("pagos.id"), nullable=False, index=True)
    estado_anterior = Column(String(20), nullable=True)
    estado_nuevo = Column(String(20), nullable=False)
    cambiado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    motivo = Column(String(255), nullable=True)
    cambiado_en = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Boleto(Base):
    __tablename__ = "boletos"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False, unique=True, index=True)
    codigo = Column(String(64), nullable=False, unique=True, index=True)
    creado_en = Column(DateTime(timezone=True), nullable=False, server_default=func.now())



class Parada(Base):
    __tablename__ = "paradas"
    __table_args__ = (UniqueConstraint("ruta_id", "orden", name="uq_parada_orden"),)
    id = Column(Integer, primary_key=True)
    ruta_id = Column(Integer, ForeignKey("rutas.id"), nullable=False)
    orden = Column(Integer, nullable=False)
    ciudad = Column(String(100), nullable=False)
    minutos = Column(Integer, nullable=False)
    proporcion_tarifa = Column(Float, nullable=False)


class OcupacionAsiento(Base):
    __tablename__ = "ocupaciones_asientos"
    __table_args__ = (UniqueConstraint("frecuencia_id", "fecha_viaje", "asiento", "segmento", name="uq_ocupacion_segmento"),)
    id = Column(Integer, primary_key=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False, index=True)
    frecuencia_id = Column(Integer, ForeignKey("frecuencias.id"), nullable=False)
    fecha_viaje = Column(Date, nullable=False)
    asiento = Column(Integer, nullable=False)
    segmento = Column(Integer, nullable=False)


class Jornada(Base):
    __tablename__ = "jornadas"
    __table_args__ = (UniqueConstraint("bus_id", "fecha", name="uq_jornada_bus"), UniqueConstraint("frecuencia_id", "fecha", name="uq_jornada_frecuencia"))
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    frecuencia_id = Column(Integer, ForeignKey("frecuencias.id"), nullable=True)


class Abordaje(Base):
    __tablename__ = "abordajes"
    id = Column(Integer, primary_key=True)
    boleto_id = Column(Integer, ForeignKey("boletos.id"), nullable=False, unique=True)
    registrado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Notificacion(Base):
    __tablename__ = "notificaciones"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    mensaje = Column(String(500), nullable=False)
    leida = Column(Boolean, nullable=False, default=False, server_default="0")
    creado_en = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Configuracion(Base):
    __tablename__ = "configuracion"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, default="Pasajes EC")
    logo_url = Column(String(500), nullable=True)
    color_principal = Column(String(7), nullable=False, default="#146d83")
    soporte = Column(String(150), nullable=False, default="")
    redes_sociales = Column(String(500), nullable=False, default="")


class VentaPresencial(Base):
    __tablename__ = "ventas_presenciales"
    id = Column(Integer, primary_key=True)
    clave = Column(String(64), nullable=False, unique=True)
    huella = Column(String(64), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False, unique=True)
    pago_id = Column(Integer, ForeignKey("pagos.id"), nullable=False, unique=True)
