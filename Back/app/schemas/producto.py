from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    precio: float = Field(..., gt=0)
    descripcion: str = Field(..., min_length=1)
    categoria: str = "Otros"
    plataforma: str = "Otro"
    activo: bool = True

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    precio: Optional[float] = Field(None, gt=0)
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    plataforma: Optional[str] = None
    activo: Optional[bool] = None
    imagen: Optional[str] = None

class ProductoResponse(ProductoBase):
    id: str = Field(..., serialization_alias="_id")
    imagen: Optional[str] = None
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")

    model_config = ConfigDict(
        from_attributes=True, 
        populate_by_name=True
    )
