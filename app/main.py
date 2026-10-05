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

# Lista de dominios permitidos para conectar con la API

origins = [
    "https://viajes.fpsevillistas.com",
    "http://viajes.fpsevillistas.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

# Permitir peticiones desde el frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # En producción especificar el dominio del frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    # allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(matches.router)
app.include_router(trips.router)

@app.get("/")
def root():
    return {"message": "API de Viajes de Fútbol operativa", "docs": "/docs"}
