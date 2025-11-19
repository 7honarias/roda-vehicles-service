from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Brand
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse
from app.repositories.brand import brand_crud


class BrandService:
    
    @staticmethod
    def create_brand(db: Session, *, brand_data: BrandCreate) -> Brand:

        return brand_crud.create_with_name_check(db, obj_in=brand_data)
    
    @staticmethod
    def get_brand(db: Session, *, brand_id: int) -> Optional[Brand]:
        return brand_crud.get(db, id=brand_id)
    
    @staticmethod
    def get_brands(db: Session, *, skip: int = 0, limit: int = 100) -> List[Brand]:
        return brand_crud.get_multi_ordered(db, skip=skip, limit=limit)
    
    @staticmethod
    def update_brand(db: Session, *, brand_id: int, brand_data: BrandUpdate) -> Optional[Brand]:
        db_brand = brand_crud.get(db, id=brand_id)
        if not db_brand:
            return None
        
        return brand_crud.update_with_name_check(db, db_obj=db_brand, obj_in=brand_data)
    
    @staticmethod
    def delete_brand(db: Session, *, brand_id: int) -> bool:
        db_brand = brand_crud.get(db, id=brand_id)
        if not db_brand:
            return False
        
        brand_crud.remove(db, id=brand_id)
        return True
    
    @staticmethod
    def search_brands(db: Session, *, search_term: str, skip: int = 0, limit: int = 100) -> List[Brand]:
        return brand_crud.search_by_name(db, search_term=search_term, skip=skip, limit=limit)
    
    @staticmethod
    def count_brands(db: Session) -> int:
        return brand_crud.count(db)
    
    @staticmethod
    def get_brand_with_vehicles(db: Session, *, brand_id: int) -> Optional[Brand]:
        return (
            db.query(Brand)
            .filter(Brand.id == brand_id)
            .first()
        )


brand_service = BrandService()