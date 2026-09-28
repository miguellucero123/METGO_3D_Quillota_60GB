from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    company_name: str
    phone: str
    sector: str
    
    @validator('password')
    def password_strength(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain uppercase')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain digit')
        return v

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class LeadCaptureRequest(BaseModel):
    first_name: str = ""
    last_name: str = ""
    email: EmailStr
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    company_name: str = ""
    sector: str = "sin_especificar"
    message: Optional[str] = None
    source: str = "website"

    @classmethod
    def desde_payload(cls, data: dict) -> "LeadCaptureRequest":
        """Acepta también los campos en español que envían los formularios de la SPA."""
        d = dict(data)
        nombre = str(d.pop("nombre", "") or "").strip()
        if nombre and not d.get("first_name"):
            first, _, last = nombre.partition(" ")
            d["first_name"] = first
            d["last_name"] = d.get("last_name") or last.strip()
        empresa = d.pop("empresa", None)
        if empresa and not d.get("company_name"):
            d["company_name"] = empresa
        telefono = d.pop("telefono", None)
        if telefono and not d.get("phone"):
            d["phone"] = telefono
            d.setdefault("whatsapp", telefono)
        mensaje = d.pop("mensaje", None)
        if mensaje and not d.get("message"):
            d["message"] = mensaje
        if not d.get("sector"):
            d["sector"] = "sin_especificar"
        return cls(**d)

class AlertConfigSchema(BaseModel):
    alert_type: str
    threshold: float
    comparison_operator: str = ">"
    channels: List[str] = ["whatsapp", "email"]
    
class CreateAlertRequest(BaseModel):
    name: str
    zone: str
    config: AlertConfigSchema
    recipient_phone: Optional[str] = None
    recipient_email: Optional[str] = None
