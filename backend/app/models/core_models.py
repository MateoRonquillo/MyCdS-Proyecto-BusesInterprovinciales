from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Time, Date
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
