from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Brand
from app.schemas.brand import BrandCreate, BrandUpdate
from app.repositories.base import CRUDBase


class CRUDBrand(CRUDBase[Brand, BrandCreate, BrandUpdate]):
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Brand]:
        return db.query(Brand).filter(func.lower(Brand.name) == name.lower()).first()
    
    def create_with_name_check(self, db: Session, *, obj_in: BrandCreate) -> Brand:
        existing = self.get_by_name(db, name=obj_in.name)
        if existing:
            raise ValueError(f"Ya existe una marca con el nombre '{obj_in.name}'")
        return self.create(db, obj_in=obj_in)
    
    def update_with_name_check(self, db: Session, *, db_obj: Brand, obj_in: BrandUpdate) -> Brand:
        if obj_in.name and obj_in.name != db_obj.name:
            existing = self.get_by_name(db, name=obj_in.name)
            if existing:
                raise ValueError(f"Ya existe una marca con el nombre '{obj_in.name}'")
        
        return self.update(db, db_obj=db_obj, obj_in=obj_in)
    
    def get_multi_ordered(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Brand]:
        return db.query(Brand).order_by(Brand.name).offset(skip).limit(limit).all()
    
    def search_by_name(self, db: Session, *, search_term: str, skip: int = 0, limit: int = 100) -> List[Brand]:
        return (
            db.query(Brand)
            .filter(Brand.name.ilike(f"%{search_term}%"))
            .order_by(Brand.name)
            .offset(skip)
            .limit(limit)
            .all()
        )


brand_crud = CRUDBrand(Brand)