from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class VehicleImageBase(BaseModel):
    url: str = Field(..., max_length=500, description="URL o path de la imagen")


class VehicleImageCreate(VehicleImageBase):
    vehicle_id: int
    pass


class VehicleImageUpdate(BaseModel):
    url: Optional[str] = Field(None, max_length=500)


class VehicleImage(VehicleImageBase):
    vehicle_id: int
    
    model_config = ConfigDict(from_attributes=True)


class VehicleImageResponse(BaseModel):
    id: int
    vehicle_id: int
    url: str
    
    model_config = ConfigDict(from_attributes=True)

