from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Time, Date, DateTime, UniqueConstraint, Computed, func
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

class Cooperativa(Base):
    __tablename__ = "cooperativas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    logo_url = Column(String(255), nullable=True)
    color_principal = Column(String(7), nullable=True)
    
class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(20), unique=True, nullable=False)
    numero_disco = Column(String(10), nullable=False)
    capacidad_asientos = Column(Integer, nullable=False)
    cooperativa_id = Column(Integer, ForeignKey("cooperativas.id"), nullable=False)
    activo = Column(Boolean, default=True)

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


class Reserva(Base):
    __tablename__ = "reservas"
    __table_args__ = (
        UniqueConstraint(
            "frecuencia_id",
            "fecha_viaje",
            "asiento_activo",
            name="uq_reserva_asiento_activo",
        ),
    )

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

    asiento_activo = Column(
        Integer,
        Computed(
            "CASE WHEN estado = 'CANCELADA' THEN NULL ELSE asiento END",
            persisted=True,
        ),
        nullable=True,
    )


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

