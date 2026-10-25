from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
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