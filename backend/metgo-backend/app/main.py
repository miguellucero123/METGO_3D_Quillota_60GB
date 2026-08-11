from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Rutas
from app.routers import auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API de Producción para METGO 3D"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar en producción a los dominios correctos (ej: localhost:5173, metgo3d.com)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "ok", "version": settings.VERSION}
