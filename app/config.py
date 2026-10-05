# 3. Configuración y Base de Datos 

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hinchas en Ruta API"
    SECRET_KEY: str = "CAMBIA_ESTA_CLAVE_SECRETA_SUPER_SEGURA_EN_PRODUCCION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    
    # Por defecto usa SQLite local; para PostgreSQL cambiar a:
    # postgresql://usuario:password@localhost:5432/futbol_carpool
    DATABASE_URL: str = "sqlite:///./futbol_carpool.db"

    class Config:
        env_file = ".env"

settings = Settings()