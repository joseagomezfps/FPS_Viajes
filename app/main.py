# 8. Punto de Entrada (app/main.py)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings
from app.routers import auth, matches, trips

# Crea las tablas automáticamente al arrancar (en producción se suele usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API para coordinar viajes compartidos aficionados a partidos de fútbol"
)

# Permitir peticiones desde el frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(matches.router)
app.include_router(trips.router)

@app.get("/")
def root():
    return {"message": "API de Viajes de Fútbol operativa", "docs": "/docs"}
