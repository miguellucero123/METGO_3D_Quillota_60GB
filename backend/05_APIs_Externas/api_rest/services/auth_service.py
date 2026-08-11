import logging
from datetime import datetime, timedelta
import bcrypt
import jwt
import os
from typing import Tuple, Optional

from integracion.supabase_store import rest_select, rest_insert, rest_patch, rest_delete

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_secret_key_metgo_3d_2024")
ALGORITHM = "HS256"

class AuthService:
    
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def generate_token(user_id: int, email: str, role: str = 'user') -> str:
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def check_brute_force(email: str, ip_address: str) -> Tuple[bool, Optional[str]]:
        """Verifica en Supabase si el usuario está bloqueado por demasiados intentos."""
        records = rest_select("failed_logins", params={"email": f"eq.{email}"}, limit=1)
        if not records:
            return True, None
            
        record = records[0]
        if record.get("is_blocked"):
            block_until_str = record.get("block_until")
            if block_until_str:
                # Simplificación de parseo de fecha
                try:
                    block_until = datetime.fromisoformat(block_until_str.replace("Z", "+00:00"))
                    # Si datetime.now(timezone.utc) es menor, sigue bloqueado
                    # (Aquí asumimos utcnow para simplificar, se requiere cuidado con timezones)
                    if datetime.utcnow().timestamp() < block_until.timestamp():
                        return False, "Account temporarily blocked. Please try again later."
                except Exception as e:
                    logger.error(f"Error parsing date {block_until_str}: {e}")
            
            # Si pasó el tiempo o hubo error, desbloquear
            rest_patch("failed_logins", {"email": f"eq.{email}"}, {"is_blocked": False, "attempt_count": 0})
            
        return True, None
        
    @staticmethod
    def record_failed_login(email: str, ip_address: str):
        """Registra un intento fallido y bloquea si es necesario."""
        records = rest_select("failed_logins", params={"email": f"eq.{email}"}, limit=1)
        now_iso = datetime.utcnow().isoformat()
        
        if records:
            record = records[0]
            new_count = record.get("attempt_count", 0) + 1
            patch_data = {
                "attempt_count": new_count,
                "last_attempt": now_iso
            }
            if new_count >= 5:
                patch_data["is_blocked"] = True
                patch_data["block_until"] = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
            
            rest_patch("failed_logins", {"email": f"eq.{email}"}, patch_data)
        else:
            insert_data = {
                "email": email,
                "ip_address": ip_address,
                "attempt_count": 1,
                "first_attempt": now_iso,
                "last_attempt": now_iso
            }
            rest_insert("failed_logins", insert_data)

    @staticmethod
    def record_successful_login(email: str):
        """Limpia los intentos fallidos al tener éxito."""
        rest_delete("failed_logins", {"email": f"eq.{email}"})

auth_service = AuthService()
