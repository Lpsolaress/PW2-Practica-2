import json
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Optional, Literal, List, Any
from datetime import datetime

class UsuarioBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: Literal["usuario", "administrador"] = "usuario"

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)

class UsuarioUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[Literal["usuario", "administrador"]] = None
    profile_picture: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    id: str = Field(..., serialization_alias="_id")
    profile_picture: Optional[str] = Field("", serialization_alias="profilePicture")
    addresses: List[dict] = []
    paymentMethods: List[dict] = Field([], serialization_alias="paymentMethods")
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")

    model_config = ConfigDict(
        from_attributes=True, 
        populate_by_name=True
    )

    @model_validator(mode="before")
    @classmethod
    def enrich_data(cls, data: Any) -> Any:
        # Si es un objeto ORM
        if hasattr(data, "addresses_data") and (not hasattr(data, "addresses") or not data.addresses):
            try:
                addrs = json.loads(data.addresses_data or "[]")
                if not addrs:
                    addrs = [{"_id": "default-pickup", "street": "Recoger en: Tienda Principal Nuba (Centro)"}]
                data.addresses = addrs
            except:
                data.addresses = [{"_id": "default-pickup", "street": "Recoger en: Tienda Principal Nuba (Centro)"}]

        if hasattr(data, "payment_methods_data") and (not hasattr(data, "paymentMethods") or not data.paymentMethods):
            try:
                pays = json.loads(data.payment_methods_data or "[]")
                if not pays:
                    pays = [{"_id": "default-applepay", "type": "otro", "cardholder": "Apple Pay", "last4": "8888"}]
                data.paymentMethods = pays
            except:
                data.paymentMethods = [{"_id": "default-applepay", "type": "otro", "cardholder": "Apple Pay", "last4": "8888"}]
        
        return data
