from sqlalchemy.orm import Session
from app.schemas.vehicle import VehicleCreate
from app.repositories.vehicle_image import vehicle_image_crud


class VehicleImageService:

    @staticmethod
    def create_vehicle_images(db: Session, *, vehicle_data: VehicleCreate,
                              id: int) -> bool:
        for image in getattr(vehicle_data, "images", []):
            vehicle_image_crud.createImage(db, image=image,  id=id)

        return True
    
vehicle_image_service = VehicleImageService()