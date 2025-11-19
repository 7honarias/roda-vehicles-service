from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.vehicle_image_model import VehicleImage as VehicleImageModel
from app.schemas.vehicle import VehicleCreate
from app.schemas.vehicle_image import VehicleImageCreate, VehicleImageUpdate
from app.repositories.base import CRUDBase


class CRUDVehicleImage(CRUDBase[VehicleImageModel, VehicleImageCreate, VehicleImageUpdate]):

    def createImage(self, db: Session, *, image: str, id:id) -> VehicleImageModel:
        obj_in = VehicleImageCreate(
            url=image,
            vehicle_id=id
        )
        return self.create(db, obj_in=obj_in)


    def get_by_vehicle_id(self, db: Session, *, vehicle_id: int) -> List[VehicleImageModel]:
        return db.query(VehicleImageModel).filter(VehicleImageModel.vehicle_id == vehicle_id).all()


vehicle_image_crud = CRUDVehicleImage(VehicleImageModel)