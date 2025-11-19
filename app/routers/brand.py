from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.params import File
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.schemas.brand import Brand, BrandCreate, BrandUpdate, BrandResponse, BrandWithVehicles
from app.services.brand_service import brand_service
from jose import jwt

from app.services.files import FileService

router = APIRouter(prefix="/brands", tags=["brands"])
security = HTTPBearer()

JWT_SECRET = settings.SECRET_KEY
JWT_ALGORITHM = settings.ALGORITHM


def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        role = payload.get("role").upper()
        print("User role from token:", role)

        if role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado, rol insuficiente"
            )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    return True

@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_admin)])
async def create_brand(
    *,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),  
    name: str = Form(...),
    country: str = Form(...)
) -> BrandResponse:
    try:
        is_valid, message = FileService.validate_file_upload(file)
        brand_in = BrandCreate(name=name, country=country, logo_path=None)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
        success, message, urls = await FileService.upload_brand_images(
            photo=file,
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)
        if "brand_photo_url" in urls:
            brand_in.logo_path = urls["brand_photo_url"]
        brand = brand_service.create_brand(db, brand_data=brand_in)
        return brand
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{brand_id}", response_model=BrandResponse, dependencies=[Depends(verify_admin)])
def update_brand(
    *,
    db: Session = Depends(get_db),
    brand_id: int,
    brand_in: BrandUpdate
) -> BrandResponse:
    try:
        brand = brand_service.update_brand(db, brand_id=brand_id, brand_data=brand_in)
        if not brand:
            raise HTTPException(status_code=404, detail="Marca no encontrada")
        return brand
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_admin)])
def delete_brand(
    *,
    db: Session = Depends(get_db),
    brand_id: int
) -> None:
    success = brand_service.delete_brand(db, brand_id=brand_id)
    if not success:
        raise HTTPException(status_code=404, detail="Marca no encontrada")


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(
    *,
    db: Session = Depends(get_db),
    brand_id: int
) -> BrandResponse:
    brand = brand_service.get_brand(db, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    return brand


@router.get("/", response_model=List[BrandResponse])
def get_brands(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str = Query(None)
) -> List[BrandResponse]:
    if search:
        return brand_service.search_brands(db, search_term=search, skip=skip, limit=limit)
    else:
        return brand_service.get_brands(db, skip=skip, limit=limit)


@router.get("/{brand_id}/with-vehicles", response_model=BrandWithVehicles)
def get_brand_with_vehicles(
    *,
    db: Session = Depends(get_db),
    brand_id: int
) -> BrandWithVehicles:
    brand = brand_service.get_brand_with_vehicles(db, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    return brand


@router.get("/stats/count", response_model=dict)
def count_brands(db: Session = Depends(get_db)) -> dict:
    count = brand_service.count_brands(db)
    return {"total_brands": count}
