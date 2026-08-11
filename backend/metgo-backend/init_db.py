from app.database import engine
from app.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """
    Crea todas las tablas en la base de datos basándose en los modelos de SQLAlchemy.
    ¡ADVERTENCIA! Si las tablas ya existen, SQLAlchemy no las sobreescribirá 
    a menos que se borren primero, pero es seguro ejecutarlo.
    """
    try:
        logger.info("Creando tablas en la base de datos PostgreSQL...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ ¡Tablas creadas exitosamente!")
    except Exception as e:
        logger.error(f"❌ Error al crear las tablas: {e}")
        logger.error("Asegúrate de que DATABASE_URL en tu archivo .env o config.py es correcto.")

if __name__ == "__main__":
    init_db()
