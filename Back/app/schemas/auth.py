import json
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Literal, Optional, List, Any
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class RegistroRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Literal["usuario", "administrador"] = "usuario"

class UsuarioSimpleResponse(BaseModel):
    id: str = Field(..., serialization_alias="_id")
    username: str
    email: EmailStr
    role: str
    profile_picture: Optional[str] = Field("", serialization_alias="profilePicture")
    addresses: List[dict] = []
    paymentMethods: List[dict] = Field([], serialization_alias="paymentMethods")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def enrich_data(cls, data: Any) -> Any:
        # Si es un objeto ORM (SQLAlchemy)
        if hasattr(data, "addresses_data"):
            try:
                # Solo inyectar si no tiene ya el atributo addresses o está vacío
                if not hasattr(data, "addresses") or not data.addresses:
                    addrs = json.loads(data.addresses_data or "[]")
                    if not addrs:
                        addrs = [{"_id": "default-pickup", "street": "Recoger en: Tienda Principal Nuba (Centro)"}]
                    data.addresses = addrs
            except Exception:
                data.addresses = [{"_id": "default-pickup", "street": "Recoger en: Tienda Principal Nuba (Centro)"}]

        if hasattr(data, "payment_methods_data"):
            try:
                if not hasattr(data, "paymentMethods") or not data.paymentMethods:
                    pays = json.loads(data.payment_methods_data or "[]")
                    if not pays:
                        pays = [{"_id": "default-applepay", "type": "otro", "cardholder": "Apple Pay", "last4": "8888"}]
                    data.paymentMethods = pays
            except Exception:
                data.paymentMethods = [{"_id": "default-applepay", "type": "otro", "cardholder": "Apple Pay", "last4": "8888"}]
        
        return data

class TokenResponse(BaseModel):
    token: str
    usuario: UsuarioSimpleResponse
    mensaje: str

class PerfilResponse(BaseModel):
    usuario: UsuarioSimpleResponse

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
