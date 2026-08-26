import sys
import os

# Asegurar que el entorno reconozca el módulo de la app
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'metgo-backend'))

from app.database import SessionLocal
from app.models import User, UserZone
from werkzeug.security import generate_password_hash

def create_admin():
    db = SessionLocal()
    email = 'miguel.lucero@metgo3d.com'
    
    existing = db.query(User).filter(User.email == email).first()
    
    if not existing:
        u = User(
            email=email,
            password_hash=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='Puertos',
            is_active=True,
            is_admin=True,
            is_verified_email=True,
            sector='izaje'
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        
        # Asignar acceso al puerto Iquique
        uz = UserZone(user_id=u.id, zone_name='puerto_iquique')
        db.add(uz)
        db.commit()
        print("\n✅ ¡Usuario ADMIN creado exitosamente!")
    else:
        existing.password_hash = generate_password_hash('admin123')
        existing.is_admin = True
        existing.is_verified_email = True
        
        # Asignar zona si no la tiene
        has_zone = any(z.zone_name == 'puerto_iquique' for z in existing.zones)
        if not has_zone:
            uz = UserZone(user_id=existing.id, zone_name='puerto_iquique')
            db.add(uz)
        db.commit()
        print("\n✅ ¡Usuario ADMIN actualizado exitosamente!")

    print("--------------------------------------------------")
    print(" 📧 Usuario: admin@ventora.com")
    print(" 🔑 Clave:   admin123")
    print("--------------------------------------------------\n")

if __name__ == "__main__":
    create_admin()
