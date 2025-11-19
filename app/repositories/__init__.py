from .base import CRUDBase
from .brand import brand_crud, CRUDBrand
from .vehicle import vehicle_crud, CRUDVehicle
from .vehicle_image import vehicle_image_crud, CRUDVehicleImage

__all__ = [
    "CRUDBase",
    "brand_crud", 
    "CRUDBrand",
    "vehicle_crud", 
    "vehicle_image_crud",
    "CrUDVehicleImage",
    "CRUDVehicle"
]