from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import schemas, crud

router = APIRouter()

@router.get("/places/", response_model=list[schemas.Place])
def read_places(category: str = None, db: Session = Depends(get_db)):
    if category:
        return crud.get_places_by_category(db, category)
    return crud.get_all_places(db)

@router.post("/places/", response_model=schemas.Place)
def create_place(place: schemas.PlaceCreate, db: Session = Depends(get_db)):
    return crud.create_place(db, place) 