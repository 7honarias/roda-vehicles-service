from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BrandBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nombre de la marca")
    country: Optional[str] = Field(None, max_length=50, description="País de origen")
    logo_path: Optional[str] = Field(None, description="URL del logo de la marca")


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=50)


class Brand(BrandBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class BrandResponse(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    logo_path: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class BrandWithVehicles(Brand):
    vehicles: list["VehicleResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


from .vehicle import VehicleResponse
BrandWithVehicles.model_rebuild()