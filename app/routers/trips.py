# 7. Endpoints Principales

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, security

router = APIRouter(prefix="/api/trips", tags=["Viajes"])

@router.get("/", response_model=List[schemas.TripResponse])
def search_trips(
    origin: Optional[str] = None,
    match_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Trip).filter(models.Trip.available_seats > 0)
    if origin:
        query = query.filter(models.Trip.origin_city.ilike(f"%{origin}%"))
    if match_id:
        query = query.filter(models.Trip.match_id == match_id)
    return query.all()

@router.post("/", response_model=schemas.TripResponse, status_code=status.HTTP_201_CREATED)
def publish_trip(
    trip_in: schemas.TripCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    # Validar que el partido existe
    match = db.query(models.Match).filter(models.Match.id == trip_in.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="El partido indicado no existe")

    trip = models.Trip(
        **trip_in.model_dump(),
        driver_id=current_user.id,
        available_seats=trip_in.total_seats
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

@router.post("/book", response_model=schemas.BookingResponse, status_code=status.HTTP_201_CREATED)
def book_trip(
    booking_in: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    trip = db.query(models.Trip).filter(models.Trip.id == booking_in.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="El viaje no existe")
    
    if trip.driver_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes reservar en tu propio viaje")
        
    if trip.available_seats < booking_in.seats_requested:
        raise HTTPException(status_code=400, detail="No hay suficientes plazas disponibles")

    booking = models.Booking(
        trip_id=trip.id,
        passenger_id=current_user.id,
        seats_requested=booking_in.seats_requested,
        message=booking_in.message,
        status=models.BookingStatus.PENDING
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.patch("/bookings/{booking_id}/status", response_model=schemas.BookingResponse)
def update_booking_status(
    booking_id: int,
    status_update: schemas.BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Solicitud de reserva no encontrada")

    # Solo el conductor del viaje puede aceptar o rechazar
    if booking.trip.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para gestionar esta reserva")

    previous_status = booking.status
    new_status = status_update.status

    # Si se acepta, restamos plazas
    if new_status == models.BookingStatus.ACCEPTED and previous_status != models.BookingStatus.ACCEPTED:
        if booking.trip.available_seats < booking.seats_requested:
            raise HTTPException(status_code=400, detail="No quedan plazas libres suficientes")
        booking.trip.available_seats -= booking.seats_requested

    # Si se cancela o rechaza habiendo estado aceptada, liberamos plazas
    elif previous_status == models.BookingStatus.ACCEPTED and new_status in (models.BookingStatus.REJECTED, models.BookingStatus.CANCELLED):
        booking.trip.available_seats += booking.seats_requested

    booking.status = new_status
    db.commit()
    db.refresh(booking)
    return booking



## el conductor revisa las reservas

@router.get("/driver/bookings", response_model=List[schemas.BookingResponse])
def get_driver_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    # Obtiene todas las solicitudes hechas a los viajes de este conductor
    return db.query(models.Booking).join(models.Trip).filter(models.Trip.driver_id == current_user.id).all()

## consultar reservas del pasajero

@router.get("/passenger/bookings", response_model=List[schemas.BookingResponse])
def get_passenger_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """Devuelve las solicitudes de reserva hechas por el usuario actual"""
    return db.query(models.Booking).filter(models.Booking.passenger_id == current_user.id).all()