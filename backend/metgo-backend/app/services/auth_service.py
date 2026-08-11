import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import secrets

from app.config import settings
from app.database import get_db
from app.models import User, LoginAttempt, FailedLogin
from app.schemas import UserResponse, TokenResponse

logger = logging.getLogger(__name__)

# Hash passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthService:
    """Servicio de autenticación y autorización"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash una contraseña"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> Tuple[str, datetime]:
        """Crear JWT token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        
        to_encode = {
            "user_id": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt, expire
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verificar JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.error(f"Invalid token: {e}")
            return None
    
    @staticmethod
    def check_brute_force(email: str, ip_address: str, db) -> Tuple[bool, Optional[str]]:
        """Verificar intentos fallidos de login (prevenir fuerza bruta)"""
        
        failed_login = db.query(FailedLogin).filter(
            FailedLogin.email == email,
            FailedLogin.ip_address == ip_address
        ).first()
        
        if failed_login and failed_login.is_blocked:
            if failed_login.block_until and datetime.utcnow() < failed_login.block_until:
                remaining_minutes = int((failed_login.block_until - datetime.utcnow()).total_seconds() / 60)
                return False, f"Account temporarily blocked. Try again in {remaining_minutes} minutes."
            else:
                # Desbloquear
                failed_login.is_blocked = False
                db.commit()
        
        return True, None
    
    @staticmethod
    def record_failed_login(email: str, ip_address: str, db):
        """Registrar intento fallido"""
        
        failed_login = db.query(FailedLogin).filter(
            FailedLogin.email == email,
            FailedLogin.ip_address == ip_address
        ).first()
        
        if failed_login:
            failed_login.attempt_count += 1
            failed_login.last_attempt = datetime.utcnow()
            
            # Bloquear después de 5 intentos
            if failed_login.attempt_count >= 5:
                failed_login.is_blocked = True
                failed_login.block_until = datetime.utcnow() + timedelta(minutes=15)
                logger.warning(f"Account blocked: {email} from {ip_address}")
        else:
            failed_login = FailedLogin(
                email=email,
                ip_address=ip_address,
                attempt_count=1
            )
            db.add(failed_login)
        
        db.commit()
    
    @staticmethod
    def record_successful_login(user: User, ip_address: str, db):
        """Registrar login exitoso"""
        
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Limpiar intentos fallidos
        failed_login = db.query(FailedLogin).filter(
            FailedLogin.email == user.email,
            FailedLogin.ip_address == ip_address
        ).first()
        if failed_login:
            db.delete(failed_login)
            db.commit()
        
        logger.info(f"Successful login: {user.email} from {ip_address}")

# Dependency para obtener usuario actual
async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db = Depends(get_db)
) -> User:
    """Obtener usuario actual desde JWT token"""
    
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Obtener usuario actual y verificar que es admin"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

# Dependency para API Key
async def get_api_key_user(
    api_key: str = None,
    db = Depends(get_db)
) -> User:
    """Obtener usuario desde API Key"""
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required"
        )
    
    from app.models import APIKey
    
    api_key_obj = db.query(APIKey).filter(
        APIKey.key == api_key,
        APIKey.is_active == True
    ).first()
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    user = db.query(User).filter(User.id == api_key_obj.user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Actualizar último uso
    api_key_obj.last_used = datetime.utcnow()
    db.commit()
    
    return user

auth_service = AuthService()
