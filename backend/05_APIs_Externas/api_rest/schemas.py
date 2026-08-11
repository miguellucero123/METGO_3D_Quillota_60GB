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
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    company_name: str
    sector: str
    message: Optional[str] = None
    source: str = "website"

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
