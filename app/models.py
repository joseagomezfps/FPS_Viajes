# 4. Modelos de Base de Datos (app/models.py)
# Definimos las 4 tablas clave con sus relaciones:
from datetime import datetime
import enum
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    ForeignKey, Text, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.database import Base

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(30), nullable=True)
    favorite_team = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trips_offered = relationship("Trip", back_populates="driver", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="passenger", cascade="all, delete-orphan")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String(100), nullable=False, index=True)
    away_team = Column(String(100), nullable=False, index=True)
    stadium = Column(String(150), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    match_date = Column(DateTime, nullable=False)

    trips = relationship("Trip", back_populates="match", cascade="all, delete-orphan")

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)

    origin_city = Column(String(100), nullable=False, index=True)
    meeting_point = Column(String(255), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    return_time = Column(DateTime, nullable=True)

    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    price_per_seat = Column(Float, default=0.0)
    vehicle_info = Column(String(150), nullable=True)  # Ej: "Seat León gris"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    driver = relationship("User", back_populates="trips_offered")
    match = relationship("Match", back_populates="trips")
    bookings = relationship("Booking", back_populates="trip", cascade="all, delete-orphan")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    seats_requested = Column(Integer, default=1, nullable=False)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="bookings")
    passenger = relationship("User", back_populates="bookings")