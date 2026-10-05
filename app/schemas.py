# 5. Esquemas de Datos Pydantic (app/schemas.py)
# Controlan qué entra por la API y qué se devuelve (ocultando datos sensibles como contraseñas).
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from app.models import BookingStatus

# --- USUARIO ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    favorite_team: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- TOKEN ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- PARTIDO ---
class MatchBase(BaseModel):
    home_team: str
    away_team: str
    stadium: str
    city: str
    match_date: datetime

class MatchCreate(MatchBase):
    pass

class MatchResponse(MatchBase):
    id: int
    class Config:
        from_attributes = True

# --- VIAJE ---
class TripBase(BaseModel):
    match_id: int
    origin_city: str
    meeting_point: str
    departure_time: datetime
    return_time: Optional[datetime] = None
    total_seats: int
    price_per_seat: float = 0.0
    vehicle_info: Optional[str] = None
    notes: Optional[str] = None

class TripCreate(TripBase):
    pass

class TripResponse(TripBase):
    id: int
    driver_id: int
    available_seats: int
    driver: UserPublic
    match: MatchResponse
    created_at: datetime
    class Config:
        from_attributes = True

# --- RESERVA ---
class BookingCreate(BaseModel):
    trip_id: int
    seats_requested: int = 1
    message: Optional[str] = None

class BookingStatusUpdate(BaseModel):
    status: BookingStatus

class BookingResponse(BaseModel):
    id: int
    trip_id: int
    passenger_id: int
    seats_requested: int
    status: BookingStatus
    message: Optional[str]
    created_at: datetime
    passenger: UserPublic
    trip: Optional[TripResponse] = None ## añadido 5.10.2026-13.54
    class Config:
        from_attributes = True