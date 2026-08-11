from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ============================================================================
# USUARIOS
# ============================================================================

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    company_name: str
    phone: str
    sector: str  # "agricultura", "mineria", "izaje", "aire"
    
    @validator('password')
    def password_strength(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain uppercase')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain digit')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan@agricola.cl",
                "password": "SecurePass123!",
                "first_name": "Juan",
                "last_name": "Pérez",
                "company_name": "Agricola Los Andes",
                "phone": "+569123456789",
                "sector": "agricultura"
            }
        }

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    company_name: Optional[str]
    phone: Optional[str]
    sector: Optional[str]
    subscription_status: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+569123456789",
                "whatsapp": "+569123456789"
            }
        }

# ============================================================================
# AUTENTICACIÓN
# ============================================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None

class JWTPayload(BaseModel):
    user_id: int
    email: str
    exp: datetime

# ============================================================================
# PLANES
# ============================================================================

class PlanResponse(BaseModel):
    id: int
    name: str
    description: str
    sector: str
    monthly_price: float
    annual_price: float
    max_zones: int
    max_alerts: int
    max_api_calls_daily: int
    features: List[str]
    
    class Config:
        from_attributes = True

class PlanListResponse(BaseModel):
    plans: List[PlanResponse]
    total: int

# ============================================================================
# PAGOS
# ============================================================================

class CreateSubscriptionRequest(BaseModel):
    plan_id: int
    billing_cycle: str = "monthly"  # "monthly", "annual"
    
    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": 1,
                "billing_cycle": "monthly"
            }
        }

class SubscriptionResponse(BaseModel):
    subscription_id: str
    customer_id: str
    status: str
    next_billing_date: Optional[datetime]
    client_secret: Optional[str]
    
    class Config:
        from_attributes = True

class PaymentHistoryResponse(BaseModel):
    id: int
    amount: float
    currency: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# ALERTAS
# ============================================================================

class AlertConfigSchema(BaseModel):
    alert_type: str  # "frost", "rain", "wind", "air_quality"
    threshold: float
    comparison_operator: str = ">"  # ">", "<", ">=", "<=", "=="
    channels: List[str] = ["whatsapp", "email"]
    trigger_count: int = 1
    min_interval_minutes: int = 60
    active_from: Optional[int] = None  # 0-24
    active_until: Optional[int] = None
    days_of_week: Optional[List[int]] = None  # 0=Monday, 6=Sunday

class CreateAlertRequest(BaseModel):
    name: str
    zone: str
    config: AlertConfigSchema
    recipient_phone: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_webhook: Optional[str] = None
    
    @validator('recipient_phone')
    def validate_phone(cls, v):
        if v and not v.startswith('+'):
            raise ValueError('Phone must start with +')
        return v
    
    @validator('recipient_email')
    def validate_email(cls, v):
        if v:
            EmailStr().validate(v)
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Alerta Helada Quillota",
                "zone": "quillota",
                "config": {
                    "alert_type": "frost",
                    "threshold": -1.0,
                    "channels": ["whatsapp", "email"]
                },
                "recipient_phone": "+56912345678",
                "recipient_email": "user@example.com"
            }
        }

class AlertResponse(BaseModel):
    id: int
    name: str
    zone: str
    alert_type: str
    threshold: float
    status: str
    is_active: bool
    times_triggered: int
    last_triggered: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int
    page: int
    page_size: int

class AlertLogResponse(BaseModel):
    id: int
    triggered_at: datetime
    value_measured: float
    threshold: float
    notification_status: str
    channels_sent: List[str]
    
    class Config:
        from_attributes = True

class TriggerAlertRequest(BaseModel):
    alert_id: int
    value: float
    triggered_at: Optional[datetime] = None

# ============================================================================
# DATOS CLIMÁTICOS
# ============================================================================

class ClimateDataResponse(BaseModel):
    zone: str
    timestamp: datetime
    temperature: Optional[float]
    humidity: Optional[float]
    wind_speed: Optional[float]
    wind_direction: Optional[int]
    wind_gust: Optional[float]
    precipitation: Optional[float]
    frost_index: Optional[float]
    frost_probability: Optional[float]
    mp10: Optional[float]  # Calidad del aire
    eto: Optional[float]  # Riego
    
    class Config:
        from_attributes = True

class ForecastDataResponse(BaseModel):
    zone: str
    issued_at: datetime
    forecast_hour: int
    forecast_timestamp: datetime
    temperature: Optional[float]
    temperature_min: Optional[float]
    temperature_max: Optional[float]
    humidity: Optional[float]
    wind_speed: Optional[float]
    precipitation_probability: Optional[float]
    precipitation: Optional[float]
    frost_risk: str  # "low", "moderate", "high", "extreme"
    frost_probability: Optional[float]
    
    class Config:
        from_attributes = True

class SubseasonalForecastResponse(BaseModel):
    zone: str
    issued_at: datetime
    forecast_period_start: datetime
    forecast_period_end: datetime
    temperature_anomaly: Optional[float]
    precipitation_anomaly: Optional[float]
    temperature_trend: str  # "above_normal", "normal", "below_normal"
    precipitation_trend: str
    mjo_phase: int
    mjo_amplitude: float
    confidence: float
    
    class Config:
        from_attributes = True

class DataQueryRequest(BaseModel):
    zone: str
    start_date: datetime
    end_date: datetime
    variables: List[str] = ["temperature", "humidity", "wind_speed"]
    frequency: str = "hourly"  # "hourly", "daily", "weekly"
    
    @root_validator(skip_on_failure=True)
    def validate_dates(cls, values):
        start = values.get('start_date')
        end = values.get('end_date')
        if start and end and start >= end:
            raise ValueError('start_date must be before end_date')
        return values

# ============================================================================
# API KEYS
# ============================================================================

class APIKeyCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Production API Key",
                "description": "Key for production environment"
            }
        }

class APIKeyResponse(BaseModel):
    id: int
    key: str  # Solo primeras 10 caracteres para seguridad
    name: str
    rate_limit_daily: int
    rate_limit_monthly: int
    calls_used_today: int
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime]
    
    class Config:
        from_attributes = True

class APIKeyListResponse(BaseModel):
    keys: List[APIKeyResponse]
    total: int

class APIUsageResponse(BaseModel):
    period: str  # "daily", "monthly"
    total_calls: int
    rate_limit: int
    usage_percentage: float
    reset_at: datetime

# ============================================================================
# LEADS Y CRM
# ============================================================================

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
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Juan",
                "last_name": "Pérez",
                "email": "juan@example.com",
                "phone": "+569123456789",
                "company_name": "Agricola Los Andes",
                "sector": "agricultura",
                "message": "Interesado en demo",
                "source": "website"
            }
        }

class LeadResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    company_name: str
    sector: str
    status: str
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# REPORTES
# ============================================================================

class ReportRequestSchema(BaseModel):
    zone: str
    report_type: str  # "weekly", "monthly", "custom"
    period_start: datetime
    period_end: datetime
    include_alerts: bool = True
    include_climate_summary: bool = True
    include_charts: bool = True
    send_email: bool = False

class ReportResponse(BaseModel):
    id: int
    zone: str
    report_type: str
    period_start: datetime
    period_end: datetime
    total_alerts_triggered: int
    total_notifications_sent: int
    temperature_avg: float
    total_precipitation: float
    pdf_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# WEBHOOKS
# ============================================================================

class WebhookCreateRequest(BaseModel):
    url: str
    events: List[str]  # ["alert.triggered", "data.updated"]
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://tu-dominio.com/webhook",
                "events": ["alert.triggered", "data.updated"]
            }
        }

class WebhookResponse(BaseModel):
    id: int
    url: str
    events: List[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# ERRORES
# ============================================================================

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    request_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Unauthorized",
                "detail": "Invalid API key",
                "error_code": "INVALID_API_KEY",
                "request_id": "req_123456789"
            }
        }

# ============================================================================
# PAGINACIÓN
# ============================================================================

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: str = "desc"  # "asc", "desc"
