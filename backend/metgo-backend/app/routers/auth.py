from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, LeadCaptureRequest
from app.models import User, Lead
from app.services.auth_service import auth_service, get_current_user
from app.services.email_service import email_service

from app.config import settings

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    
    # Check si el email ya existe
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Crear usuario
    new_user = User(
        email=user_data.email,
        password_hash=auth_service.hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        company_name=user_data.company_name,
        phone=user_data.phone,
        sector=user_data.sector,
        subscription_status="trial"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Enviar email bienvenida
    email_service.send_welcome_email(user_email=new_user.email, user_name=new_user.first_name)
    
    # Generar token
    access_token, _ = auth_service.create_access_token(user_id=new_user.id, email=new_user.email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600 * settings.JWT_EXPIRATION_HOURS
    }

@router.post("/login", response_model=TokenResponse)
def login_user(user_data: UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    """Iniciar sesión"""
    
    ip_address = request.client.host if request.client else "unknown"
    
    # Control de fuerza bruta
    is_allowed, error_msg = auth_service.check_brute_force(user_data.email, ip_address, db)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_msg
        )
    
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not auth_service.verify_password(user_data.password, user.password_hash):
        auth_service.record_failed_login(user_data.email, ip_address, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Reset fallidos y actualizar último login
    auth_service.record_successful_login(user, ip_address, db)
    
    # Generar token
    access_token, _ = auth_service.create_access_token(user_id=user.id, email=user.email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600 * settings.JWT_EXPIRATION_HOURS
    }

@router.post("/leads", status_code=status.HTTP_201_CREATED)
def capture_lead(lead_data: LeadCaptureRequest, db: Session = Depends(get_db)):
    """Capturar lead comercial desde el hero/formulario"""
    
    # Revisar si ya existe
    existing_lead = db.query(Lead).filter(Lead.email == lead_data.email).first()
    if existing_lead:
        # Actualizar info o ignorar
        return {"status": "ok", "message": "Lead already exists", "lead_id": existing_lead.lead_id}
        
    new_lead = Lead(
        first_name=lead_data.first_name,
        last_name=lead_data.last_name,
        email=lead_data.email,
        phone=lead_data.phone,
        whatsapp=lead_data.whatsapp,
        company_name=lead_data.company_name,
        sector=lead_data.sector,
        source=lead_data.source,
        notes=lead_data.message
    )
    
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    
    return {"status": "ok", "message": "Lead captured successfully", "lead_id": new_lead.lead_id}
