from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models import Vehicle, VehicleType
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleFilters
from app.repositories.base import CRUDBase


class CRUDVehicle(CRUDBase[Vehicle, VehicleCreate, VehicleUpdate]):
    
    def get_by_referencia(self, db: Session, *, referencia: str) -> Optional[Vehicle]:
        return db.query(Vehicle).filter(Vehicle.referencia == referencia).first()
    
    def create_with_referencia_check(self, db: Session, *, obj_in: VehicleCreate) -> Vehicle:
        existing = self.get_by_referencia(db, referencia=obj_in.referencia)
        if existing:
            raise ValueError(f"Ya existe un vehículo con la referencia '{obj_in.referencia}'")
        
        try:
            VehicleType(obj_in.tipo)
        except ValueError:
            raise ValueError(f"Tipo de vehículo '{obj_in.tipo}' no es válido")
        
        return self.create(db, obj_in=obj_in)
    
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        filters: Optional[VehicleFilters] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> tuple[List[Vehicle], int]:
        query = db.query(Vehicle)
        total_query = db.query(func.count(Vehicle.id))
        
        if filters:
            if filters.marca_id:
                query = query.filter(Vehicle.marca_id == filters.marca_id)
                total_query = total_query.filter(Vehicle.marca_id == filters.marca_id)
            
            if filters.tipo:
                query = query.filter(Vehicle.tipo == filters.tipo)
                total_query = total_query.filter(Vehicle.tipo == filters.tipo)
            
            if filters.precio_min is not None:
                query = query.filter(Vehicle.precio >= filters.precio_min)
                total_query = total_query.filter(Vehicle.precio >= filters.precio_min)
            
            if filters.precio_max is not None:
                query = query.filter(Vehicle.precio <= filters.precio_max)
                total_query = total_query.filter(Vehicle.precio <= filters.precio_max)
        
        total = total_query.scalar()
        vehicles = query.order_by(Vehicle.nombre).offset(skip).limit(limit).all()
        
        return vehicles, total
    
    def get_by_marca(self, db: Session, *, marca_id: int, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        return (
            db.query(Vehicle)
            .filter(Vehicle.marca_id == marca_id)
            .order_by(Vehicle.nombre)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_tipo(self, db: Session, *, tipo: str, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        try:
            VehicleType(tipo)
        except ValueError:
            raise ValueError(f"Tipo de vehículo '{tipo}' no es válido")
        
        return (
            db.query(Vehicle)
            .filter(Vehicle.tipo == tipo)
            .order_by(Vehicle.nombre)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_precio_range(
        self, 
        db: Session, 
        *, 
        precio_min: float, 
        precio_max: float, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Vehicle]:
        return (
            db.query(Vehicle)
            .filter(and_(Vehicle.precio >= precio_min, Vehicle.precio <= precio_max))
            .order_by(Vehicle.precio)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_by_nombre(self, db: Session, *, search_term: str, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        return (
            db.query(Vehicle)
            .filter(Vehicle.nombre.ilike(f"%{search_term}%"))
            .order_by(Vehicle.nombre)
            .offset(skip)
            .limit(limit)
            .all()
        )


vehicle_crud = CRUDVehicle(Vehicle)