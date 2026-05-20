from pydantic import BaseModel, Field, ConfigDict
from typing import List
from app.schemas.producto import ProductoResponse

class CarritoItemResponse(BaseModel):
    product: ProductoResponse
    quantity: int

class CarritoResponse(BaseModel):
    items: List[CarritoItemResponse]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
