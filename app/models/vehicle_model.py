from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.vehicle_type_enum import VehicleType

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    referencia = Column(String(50), unique=True, nullable=False, index=True)
    precio = Column(Float, nullable=False)
    tipo = Column(Enum(VehicleType), nullable=False)
    marca_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    brand = relationship("Brand", back_populates="vehicles")
    images = relationship("VehicleImage", back_populates="vehicle", cascade="all, delete-orphan")  # string está bien

    def __repr__(self):
        return f"<Vehicle(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo}')>"
