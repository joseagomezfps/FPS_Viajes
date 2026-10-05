# 7. Endpoints Principales

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, security

router = APIRouter(prefix="/api/matches", tags=["Partidos"])

@router.get("/", response_model=List[schemas.MatchResponse])
def list_matches(team: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Match)
    if team:
        query = query.filter(
            (models.Match.home_team.ilike(f"%{team}%")) | 
            (models.Match.away_team.ilike(f"%{team}%"))
        )
    return query.order_by(models.Match.match_date.asc()).all()

@router.post("/", response_model=schemas.MatchResponse)
def create_match(
    match_in: schemas.MatchCreate, 
    db: Session = Depends(get_db),
    _: models.User = Depends(security.get_current_user)
):
    match = models.Match(**match_in.model_dump())
    db.add(match)
    db.commit()
    db.refresh(match)
    return match