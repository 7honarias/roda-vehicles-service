from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from jose import jwt
from app.schemas.vehicle import (
    Vehicle, VehicleCreate, VehicleUpdate, VehicleResponse, 
    VehicleFilters, VehicleListResponse
)
from app.services.files import FileService
from app.services.vehicle_service import vehicle_service
from app.services.vehicle_images_service import VehicleImageService

router = APIRouter(prefix="/vehicles", tags=["vehicles"])
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

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED,  dependencies=[Depends(verify_admin)])
async def create_vehicle(
    *,
    file_one: UploadFile = File(...),
    file_two: UploadFile = File(...),
    file_three: UploadFile = File(...),
    nombre: str = Form(...),
    referencia: str = Form(...),
    precio: float = Form(...),
    tipo: str = Form(...),
    marca_id: int = Form(...),
    db: Session = Depends(get_db),
) -> VehicleResponse:
    try:
        vehicle_in = VehicleCreate(
            nombre=nombre,
            referencia=referencia,
            precio=precio,
            tipo=tipo,
            marca_id=marca_id,
            images=[]
        )
        files = [file_one, file_two, file_three]
        success, message, urls = await FileService.upload_vehicle_images(files)
        if not success:
            print("File upload failed here:", message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)
        vehicle = vehicle_service.create_vehicle(db, vehicle_data=vehicle_in)
        vehicle_in.images = urls

        VehicleImageService.create_vehicle_images(db, vehicle_data=vehicle_in, id=vehicle.id)
        return vehicle
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int
) -> VehicleResponse:
    """Obtener un vehículo por ID"""
    vehicle = vehicle_service.get_vehicle(db, vehicle_id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehicle


@router.get("/", response_model=VehicleListResponse)
def get_vehicles(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros"),
    marca_id: Optional[int] = Query(None, gt=0, description="Filtrar por marca"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    precio_min: Optional[float] = Query(None, gt=0, description="Precio mínimo"),
    precio_max: Optional[float] = Query(None, gt=0, description="Precio máximo"),
    search: Optional[str] = Query(None, description="Buscar por nombre")
) -> VehicleListResponse:
    """Obtener lista de vehículos con filtros y paginación"""
    
    # Construir filtros
    filters = None
    if any([marca_id, tipo, precio_min, precio_max]):
        filters = VehicleFilters(
            marca_id=marca_id,
            tipo=tipo,
            precio_min=precio_min,
            precio_max=precio_max
        )
    
    # Si hay término de búsqueda, usar búsqueda por nombre
    if search:
        vehicles = vehicle_service.search_vehicles(db, search_term=search, skip=skip, limit=limit)
        
        # Calcular total manualmente para búsqueda
        total = len(vehicles)
        page = (skip // limit) + 1 if limit > 0 else 1
        pages = (total + limit - 1) // limit if limit > 0 else 1
        
        return VehicleListResponse(
            vehicles=vehicles,
            total=total,
            page=page,
            per_page=limit,
            pages=pages
        )
    else:
        return vehicle_service.get_vehicles_with_filters(
            db, 
            filters=filters, 
            skip=skip, 
            limit=limit
        )


@router.get("/by-marca/{marca_id}", response_model=List[VehicleResponse])
def get_vehicles_by_marca(
    *,
    db: Session = Depends(get_db),
    marca_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> List[VehicleResponse]:
    """Obtener vehículos por marca específica"""
    vehicles = vehicle_service.get_vehicles_by_marca(
        db, 
        marca_id=marca_id, 
        skip=skip, 
        limit=limit
    )
    return vehicles


@router.get("/by-tipo/{tipo}", response_model=List[VehicleResponse])
def get_vehicles_by_tipo(
    *,
    db: Session = Depends(get_db),
    tipo: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> List[VehicleResponse]:
    """Obtener vehículos por tipo específico"""
    try:
        vehicles = vehicle_service.get_vehicles_by_tipo(
            db, 
            tipo=tipo, 
            skip=skip, 
            limit=limit
        )
        return vehicles
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/by-precio-range", response_model=List[VehicleResponse])
def get_vehicles_by_precio_range(
    *,
    db: Session = Depends(get_db),
    precio_min: float = Query(..., gt=0),
    precio_max: float = Query(..., gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> List[VehicleResponse]:
    """Obtener vehículos por rango de precio"""
    if precio_min > precio_max:
        raise HTTPException(status_code=400, detail="El precio mínimo no puede ser mayor al máximo")
    
    vehicles = vehicle_service.get_vehicles_by_precio_range(
        db, 
        precio_min=precio_min, 
        precio_max=precio_max, 
        skip=skip, 
        limit=limit
    )
    return vehicles


@router.put("/{vehicle_id}", response_model=VehicleResponse,  dependencies=[Depends(verify_admin)])
def update_vehicle(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    vehicle_in: VehicleUpdate
) -> VehicleResponse:
    """Actualizar un vehículo"""
    try:
        vehicle = vehicle_service.update_vehicle(db, vehicle_id=vehicle_id, vehicle_data=vehicle_in)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")
        return vehicle
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT,  dependencies=[Depends(verify_admin)])
def delete_vehicle(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int
) -> None:
    """Eliminar un vehículo"""
    success = vehicle_service.delete_vehicle(db, vehicle_id=vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")


@router.get("/types/available", response_model=List[str])
def get_available_vehicle_types() -> List[str]:
    """Obtener tipos de vehículos disponibles"""
    return vehicle_service.get_available_types()


@router.get("/stats/count", response_model=dict)
def count_vehicles(db: Session = Depends(get_db)) -> dict:
    """Contar total de vehículos"""
    count = vehicle_service.count_vehicles(db)
    return {"total_vehicles": count}