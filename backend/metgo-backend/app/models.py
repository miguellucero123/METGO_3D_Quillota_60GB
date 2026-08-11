from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, JSON, Text, Enum, Index, UniqueConstraint,
    ARRAY, Numeric
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()

# ============================================================================
# USUARIOS Y AUTENTICACIÓN
# ============================================================================

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        Index('idx_user_email', 'email'),
        Index('idx_user_created_at', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    company_name = Column(String(255))
    phone = Column(String(20))
    whatsapp = Column(String(20))
    sector = Column(String(50))  # "agricultura", "mineria", "izaje", "aire"
    
    # Suscripción
    plan_id = Column(Integer, ForeignKey('plans.id'))
    plan = relationship("Plan", back_populates="users")
    subscription_status = Column(String(50), default="trial")  # trial, active, paused, cancelled
    subscription_start = Column(DateTime, default=datetime.utcnow)
    subscription_end = Column(DateTime)
    
    # Stripe
    stripe_customer_id = Column(String(255), unique=True)
    stripe_subscription_id = Column(String(255))
    
    # Permisos
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_verified_email = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relaciones
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    zones = relationship("UserZone", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"

class APIKey(Base):
    __tablename__ = "api_keys"
    __table_args__ = (
        UniqueConstraint('key', name='uq_api_key'),
        Index('idx_api_key_user_id', 'user_id'),
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="api_keys")
    
    key = Column(String(255), unique=True, nullable=False)  # metgo_xxxxxxxxxxxxx
    name = Column(String(255))
    description = Column(Text)
    
    # Rate limit
    rate_limit_daily = Column(Integer, default=100)  # 100 calls/day freemium
    rate_limit_monthly = Column(Integer, default=3000)
    calls_used_today = Column(Integer, default=0)
    calls_used_month = Column(Integer, default=0)
    last_reset = Column(DateTime, default=datetime.utcnow)
    
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<APIKey {self.key[:10]}...>"

# ============================================================================
# PLANES Y PAGOS
# ============================================================================

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(Text)
    sector = Column(String(50))  # "agricultura", "mineria", "municipio"
    
    # Precios
    monthly_price = Column(Numeric(10, 2))  # USD
    annual_price = Column(Numeric(10, 2))
    setup_fee = Column(Numeric(10, 2), default=0)
    
    # Stripe
    stripe_product_id = Column(String(255))
    stripe_monthly_price_id = Column(String(255))
    stripe_annual_price_id = Column(String(255))
    
    # Límites
    max_zones = Column(Integer, default=1)
    max_alerts = Column(Integer, default=5)
    max_api_calls_daily = Column(Integer, default=100)
    max_users = Column(Integer, default=1)
    
    # Features
    features = Column(JSON, default=list)  # ["alertas_tiempo_real", "pronóstico_72h", ...]
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    users = relationship("User", back_populates="plan")
    
    def __repr__(self):
        return f"<Plan {self.name}>"

class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        Index('idx_payment_user_id', 'user_id'),
        Index('idx_payment_created_at', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="payments")
    
    # Stripe
    stripe_payment_id = Column(String(255), unique=True)
    stripe_invoice_id = Column(String(255))
    
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    plan_id = Column(Integer, ForeignKey('plans.id'))
    
    status = Column(String(50), default="pending")  # pending, succeeded, failed
    payment_method = Column(String(50))  # card, bank_transfer
    
    billing_period_start = Column(DateTime)
    billing_period_end = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Payment {self.stripe_payment_id}>"

# ============================================================================
# ZONAS Y DATOS CLIMÁTICOS
# ============================================================================

class UserZone(Base):
    __tablename__ = "user_zones"
    __table_args__ = (
        UniqueConstraint('user_id', 'zone_name', name='uq_user_zone'),
        Index('idx_user_zone_user_id', 'user_id'),
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="zones")
    
    zone_name = Column(String(100), nullable=False)  # "quillota", "copiapo", custom
    zone_type = Column(String(50))  # "predefined", "custom"
    
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ClimateData(Base):
    __tablename__ = "climate_data"
    __table_args__ = (
        Index('idx_climate_zone_timestamp', 'zone_name', 'timestamp'),
        Index('idx_climate_zone', 'zone_name'),
    )
    
    id = Column(Integer, primary_key=True)
    zone_name = Column(String(100), nullable=False)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False)
    
    # Variables principales
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)  # km/h
    wind_direction = Column(Integer)  # 0-360 grados
    wind_gust = Column(Float)
    pressure = Column(Float)
    precipitation = Column(Float)  # mm
    cloud_cover = Column(Float)  # %
    
    # Variables especializadas
    frost_index = Column(Float)  # Índice de riesgo de helada
    frost_probability = Column(Float)  # %
    wind_chill = Column(Float)  # Sensación térmica
    dew_point = Column(Float)
    
    # Calidad del aire
    mp10 = Column(Float)  # Material particulado
    mp25 = Column(Float)
    no2 = Column(Float)
    so2 = Column(Float)
    o3 = Column(Float)
    
    # Riego agrícola
    eto = Column(Float)  # Evapotranspiración
    soil_moisture = Column(Float)  # %
    rainfall_potential = Column(Float)  # mm
    
    # Metadata
    data_source = Column(String(50))  # "openmeteo", "era5", "gfs", "custom"
    is_forecast = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ForecastData(Base):
    __tablename__ = "forecast_data"
    __table_args__ = (
        Index('idx_forecast_zone_hour', 'zone_name', 'forecast_hour'),
        Index('idx_forecast_zone', 'zone_name'),
    )
    
    id = Column(Integer, primary_key=True)
    zone_name = Column(String(100), nullable=False)
    
    # Tiempos
    issued_at = Column(DateTime, nullable=False)  # Cuándo se emitió el pronóstico
    forecast_hour = Column(Integer)  # 0, 6, 12, 24, 48, 72 horas
    forecast_timestamp = Column(DateTime, nullable=False)  # Cuándo es el pronóstico
    
    # Pronóstico
    temperature = Column(Float)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Integer)
    precipitation_probability = Column(Float)  # %
    precipitation = Column(Float)  # mm
    
    # Índices de riesgo
    frost_risk = Column(String(20))  # "low", "moderate", "high", "extreme"
    frost_probability = Column(Float)
    wind_risk = Column(String(20))  # Para izaje
    rain_risk = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SubseasonalForecast(Base):
    """Pronóstico a largo plazo (20-90 días) vía MJO"""
    __tablename__ = "subseasonal_forecasts"
    __table_args__ = (
        Index('idx_subseasonal_zone_issued', 'zone_name', 'issued_at'),
    )
    
    id = Column(Integer, primary_key=True)
    zone_name = Column(String(100), nullable=False)
    
    issued_at = Column(DateTime, nullable=False)
    forecast_period_start = Column(DateTime)  # 20 días desde hoy
    forecast_period_end = Column(DateTime)  # 90 días desde hoy
    
    # Anomalías
    temperature_anomaly = Column(Float)  # +1.5°C
    precipitation_anomaly = Column(Float)  # -20%
    
    # Tendencia
    temperature_trend = Column(String(20))  # "above_normal", "normal", "below_normal"
    precipitation_trend = Column(String(20))
    
    # Probabilidades
    dry_probability = Column(Float)  # Probabilidad de sequía
    wet_probability = Column(Float)  # Probabilidad de lluvia excesiva
    frost_season_probability = Column(Float)  # Riesgo de heladas en período
    
    # MJO
    mjo_phase = Column(Integer)  # 1-8
    mjo_amplitude = Column(Float)  # 0-1
    mjo_region = Column(String(50))  # Qué región afecta
    
    confidence = Column(Float)  # 0-1 (confianza del pronóstico)
    model = Column(String(50))  # "PINN_PSAL_CL", "GFS", "SEAS5"
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# ALERTAS
# ============================================================================

class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    TRIGGERED = "triggered"
    RESOLVED = "resolved"
    DELETED = "deleted"

class AlertChannel(str, enum.Enum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"

class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index('idx_alert_user_id', 'user_id'),
        Index('idx_alert_zone', 'zone'),
        Index('idx_alert_active', 'is_active'),
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="alerts")
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    zone = Column(String(100), nullable=False)
    
    # Tipo de alerta
    alert_type = Column(String(50), nullable=False)  # "frost", "rain", "wind", "air_quality", "custom"
    
    # Umbral
    threshold = Column(Float, nullable=False)
    comparison_operator = Column(String(10))  # "<", ">", "<=", ">=", "=="
    
    # Canales
    channels = Column(ARRAY(String), default=list)  # ["whatsapp", "email"]
    recipient_phone = Column(String(20))
    recipient_email = Column(String(255))
    recipient_webhook = Column(String(500))
    
    # Frecuencia
    trigger_count = Column(Integer, default=1)  # Cuántas veces consecutivas debe ocurrir
    min_interval_minutes = Column(Integer, default=60)  # Intervalo mínimo entre disparos
    
    # Horario
    active_from = Column(Integer)  # 0-24 (hora del día)
    active_until = Column(Integer)
    days_of_week = Column(ARRAY(Integer))  # 0=lunes, 6=domingo
    
    # Estado
    status = Column(String(20), default="active")
    is_active = Column(Boolean, default=True)
    
    # Control
    times_triggered = Column(Integer, default=0)
    last_triggered = Column(DateTime)
    last_notified = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    trigger_logs = relationship("AlertLog", back_populates="alert", cascade="all, delete-orphan")

class AlertLog(Base):
    """Registro de cada vez que una alerta se dispara"""
    __tablename__ = "alert_logs"
    __table_args__ = (
        Index('idx_alert_log_alert_id', 'alert_id'),
        Index('idx_alert_log_timestamp', 'timestamp'),
    )
    
    id = Column(Integer, primary_key=True)
    alert_id = Column(Integer, ForeignKey('alerts.id'), nullable=False)
    alert = relationship("Alert", back_populates="trigger_logs")
    
    triggered_at = Column(DateTime, default=datetime.utcnow)
    value_measured = Column(Float)
    threshold = Column(Float)
    
    # Notificación enviada
    notification_status = Column(String(50))  # "sent", "failed", "pending"
    channels_sent = Column(ARRAY(String), default=list)
    
    # Respuesta del usuario
    user_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    
    # Error details si aplica
    error_message = Column(Text)
    
    timestamp = Column(DateTime, default=datetime.utcnow)

class AlertTemplate(Base):
    """Plantillas predefinidas de alertas"""
    __tablename__ = "alert_templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    zone = Column(String(100))  # "quillota", "general" (para todas)
    alert_type = Column(String(50))
    description = Column(Text)
    
    threshold = Column(Float)
    channels = Column(ARRAY(String), default=["whatsapp", "email"])
    
    # Mensaje personalizado
    message_subject = Column(String(255))
    message_template = Column(Text)  # Con variables: {value}, {threshold}, {zone}
    message_whatsapp = Column(Text)
    
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# AUDITORÍA Y SEGURIDAD
# ============================================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index('idx_audit_user_id', 'user_id'),
        Index('idx_audit_created_at', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship("User", back_populates="audit_logs")
    
    action = Column(String(100), nullable=False)  # "login", "create_alert", "api_call", etc
    resource_type = Column(String(50))  # "alert", "api_key", "subscription"
    resource_id = Column(String(100))
    
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    status = Column(String(20))  # "success", "failed"
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    __table_args__ = (
        Index('idx_login_attempt_email', 'email'),
        Index('idx_login_attempt_ip', 'ip_address'),
    )
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255))
    ip_address = Column(String(50))
    
    success = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class FailedLogin(Base):
    """Control de intentos fallidos para prevenir fuerza bruta"""
    __tablename__ = "failed_logins"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255))
    ip_address = Column(String(50))
    attempt_count = Column(Integer, default=1)
    first_attempt = Column(DateTime, default=datetime.utcnow)
    last_attempt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_blocked = Column(Boolean, default=False)
    block_until = Column(DateTime)

# ============================================================================
# LEADS Y CRM
# ============================================================================

class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        Index('idx_lead_email', 'email'),
        Index('idx_lead_created_at', 'created_at'),
        UniqueConstraint('email', name='uq_lead_email'),
    )
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    
    # Info personal
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    whatsapp = Column(String(20))
    
    # Info profesional
    company_name = Column(String(255))
    company_size = Column(String(50))  # "1-10", "11-50", "51-200", "200+"
    job_title = Column(String(100))
    sector = Column(String(50))  # "agricultura", "mineria", "izaje", "aire"
    
    # Generación
    source = Column(String(50))  # "website", "linkedin", "email", "referral"
    campaign = Column(String(100))  # "demo-agricultura", "webinar-mineria"
    
    # CRM
    status = Column(String(50), default="new")  # "new", "contacted", "qualified", "opportunity", "customer", "lost"
    hubspot_contact_id = Column(String(255))
    hubspot_deal_id = Column(String(255))
    
    # Interés
    product_interest = Column(String(100))  # "plan_campo", "plan_faena", "api"
    estimated_budget = Column(String(50))  # "$1k-5k", "$5k-10k", "$10k+"
    estimated_deal_value = Column(Numeric(10, 2))
    
    # Timeline
    decision_timeline = Column(String(50))  # "immediate", "1-3-months", "3-6-months", "future"
    
    # Notas
    notes = Column(Text)
    
    # Seguimiento
    last_contacted = Column(DateTime)
    next_follow_up = Column(DateTime)
    assigned_to = Column(String(100))  # Email del vendedor
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Lead {self.email}>"

# ============================================================================
# INTEGRACIONES Y WEBHOOKS
# ============================================================================

class Webhook(Base):
    __tablename__ = "webhooks"
    __table_args__ = (
        Index('idx_webhook_user_id', 'user_id'),
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    url = Column(String(500), nullable=False)
    events = Column(ARRAY(String), default=list)  # ["alert.triggered", "data.updated"]
    secret = Column(String(255))  # Para verificar webhook
    
    is_active = Column(Boolean, default=True)
    
    retry_count = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=300)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WebhookLog(Base):
    __tablename__ = "webhook_logs"
    
    id = Column(Integer, primary_key=True)
    webhook_id = Column(Integer, ForeignKey('webhooks.id'))
    
    event = Column(String(100))
    payload = Column(JSON)
    
    response_code = Column(Integer)
    response_body = Column(Text)
    
    status = Column(String(20))  # "success", "failed", "pending"
    attempts = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# ANÁLISIS Y REPORTES
# ============================================================================

class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        Index('idx_report_user_id', 'user_id'),
        Index('idx_report_created_at', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    zone = Column(String(100))
    report_type = Column(String(50))  # "weekly", "monthly", "custom", "frost_season"
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    # Estadísticas
    total_alerts_triggered = Column(Integer, default=0)
    total_notifications_sent = Column(Integer, default=0)
    alert_effectiveness = Column(Float)  # % de alertas que resultaron en acción
    
    # Datos climáticos
    temperature_avg = Column(Float)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    total_precipitation = Column(Float)
    frost_events = Column(Integer, default=0)
    
    # Documento
    report_content = Column(JSON)  # Datos tabulares del reporte
    pdf_url = Column(String(500))  # S3 URL
    
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)

# ============================================================================
# FEEDBACK Y SOPORTE
# ============================================================================

class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        Index('idx_feedback_user_id', 'user_id'),
        Index('idx_feedback_created_at', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    type = Column(String(50))  # "bug", "feature_request", "improvement", "general"
    title = Column(String(255))
    description = Column(Text)
    
    rating = Column(Integer)  # 1-5 stars
    
    status = Column(String(50), default="new")  # "new", "reviewing", "in_progress", "completed"
    
    attachments = Column(ARRAY(String))  # URLs de archivos
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    __table_args__ = (
        Index('idx_support_user_id', 'user_id'),
        Index('idx_support_status', 'status'),
    )
    
    id = Column(Integer, primary_key=True)
    ticket_number = Column(String(20), unique=True)  # "TK-00001"
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    subject = Column(String(255))
    description = Column(Text)
    category = Column(String(50))  # "technical", "billing", "feature_request", "general"
    
    priority = Column(String(20))  # "low", "medium", "high", "urgent"
    status = Column(String(20), default="open")  # "open", "in_progress", "waiting_user", "resolved", "closed"
    
    assigned_to = Column(String(100))  # Email del soporte
    
    messages = Column(JSON, default=list)  # Array de mensajes
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
