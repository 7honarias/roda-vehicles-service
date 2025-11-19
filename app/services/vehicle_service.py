from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleFilters, VehicleListResponse
from app.repositories.vehicle import vehicle_crud


class VehicleService:
    
    @staticmethod
    def create_vehicle(db: Session, *, vehicle_data: VehicleCreate) -> Vehicle:
        return vehicle_crud.create_with_referencia_check(db, obj_in=vehicle_data)
    
    @staticmethod
    def get_vehicle(db: Session, *, vehicle_id: int) -> Optional[Vehicle]:
        return vehicle_crud.get(db, id=vehicle_id)
    
    @staticmethod
    def get_vehicles(db: Session, *, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        vehicles, _ = vehicle_crud.get_multi_with_filters(db, skip=skip, limit=limit)
        return vehicles
    
    @staticmethod
    def get_vehicles_with_filters(
        db: Session,
        *,
        filters: Optional[VehicleFilters] = None,
        skip: int = 0,
        limit: int = 100
    ) -> VehicleListResponse:
        vehicles, total = vehicle_crud.get_multi_with_filters(
            db,
            filters=filters,
            skip=skip,
            limit=limit
        )
        
        page = (skip // limit) + 1 if limit > 0 else 1
        pages = (total + limit - 1) // limit if limit > 0 else 1
        
        return VehicleListResponse(
            vehicles=vehicles,
            total=total,
            page=page,
            per_page=limit,
            pages=pages
        )
    
    @staticmethod
    def update_vehicle(db: Session, *, vehicle_id: int, vehicle_data: VehicleUpdate) -> Optional[Vehicle]:
        db_vehicle = vehicle_crud.get(db, id=vehicle_id)
        if not db_vehicle:
            return None
        
        if vehicle_data.tipo and vehicle_data.tipo != db_vehicle.tipo:
            from app.models import VehicleType
            try:
                VehicleType(vehicle_data.tipo)
            except ValueError:
                raise ValueError(f"Tipo de vehículo '{vehicle_data.tipo}' no es válido")
        
        return vehicle_crud.update(db, db_obj=db_vehicle, obj_in=vehicle_data)
    
    @staticmethod
    def delete_vehicle(db: Session, *, vehicle_id: int) -> bool:
        db_vehicle = vehicle_crud.get(db, id=vehicle_id)
        if not db_vehicle:
            return False
        
        vehicle_crud.remove(db, id=vehicle_id)
        return True

    @staticmethod
    def get_vehicles_by_marca(db: Session, *, marca_id: int,
                              skip: int = 0, limit: int = 100) -> List[Vehicle]:
        return vehicle_crud.get_by_marca(
            db, marca_id=marca_id, skip=skip, limit=limit)
    
    @staticmethod
    def get_vehicles_by_tipo(db: Session, *, tipo: str, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        return vehicle_crud.get_by_tipo(db, tipo=tipo, skip=skip, limit=limit)
    
    @staticmethod
    def get_vehicles_by_precio_range(
        db: Session,
        *,
        precio_min: float, 
        precio_max: float, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Vehicle]:
        return vehicle_crud.get_by_precio_range(
            db,
            precio_min=precio_min,
            precio_max=precio_max,
            skip=skip,
            limit=limit
        )

    @staticmethod
    def search_vehicles(db: Session, *, search_term: str, skip: int = 0,
                         limit: int = 100) -> List[Vehicle]:
        return vehicle_crud.search_by_nombre(db, search_term=search_term,
                                              skip=skip, limit=limit)

    @staticmethod
    def count_vehicles(db: Session) -> int:
        return vehicle_crud.count(db)
    
    @staticmethod
    def get_available_types() -> List[str]:
        from app.models import VehicleType
        return [tipo.value for tipo in VehicleType]


vehicle_service = VehicleService()
