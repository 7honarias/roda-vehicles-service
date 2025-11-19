from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from .brand import BrandResponse
from .vehicle_image import VehicleImageResponse


class VehicleBase(BaseModel):
    nombre: str = Field(..., max_length=100, description="Nombre del vehículo")
    referencia: str = Field(..., max_length=50, description="Referencia única del vehículo")
    precio: float = Field(..., gt=0, description="Precio del vehículo (>0)")
    tipo: str = Field(..., description="Tipo de vehículo")
    marca_id: int = Field(..., gt=0, description="ID de la marca")


class VehicleCreate(VehicleBase):
    images: Optional[List[VehicleImageResponse]] = Field(
        default=None, 
        description="Lista de imágenes del vehículo (máximo 3)"
    )


class VehicleUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    referencia: Optional[str] = Field(None, max_length=50)
    precio: Optional[float] = Field(None, gt=0)
    tipo: Optional[str] = None
    marca_id: Optional[int] = Field(None, gt=0)


class Vehicle(VehicleBase):
    id: int
    brand: BrandResponse
    
    model_config = ConfigDict(from_attributes=True)


class VehicleResponse(BaseModel):
    id: int
    nombre: str
    referencia: str
    precio: float
    tipo: str
    marca_id: int
    brand: BrandResponse
    images: List[VehicleImageResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class VehicleFilters(BaseModel):
    marca_id: Optional[int] = Field(None, gt=0, description="Filtrar por marca")
    tipo: Optional[str] = Field(None, description="Filtrar por tipo")
    precio_min: Optional[float] = Field(None, gt=0, description="Precio mínimo")
    precio_max: Optional[float] = Field(None, gt=0, description="Precio máximo")


class VehicleListResponse(BaseModel):
    vehicles: list[VehicleResponse]
    total: int
    page: int
    per_page: int
    pages: int