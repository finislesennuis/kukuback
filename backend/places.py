from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from importlib import import_module
schemas = import_module('schemas')
crud = import_module('crud')

router = APIRouter()

@router.get("/places/", response_model=list[schemas.Place])
def read_places(category: str = None, db: Session = Depends(get_db)):
    if category:
        return crud.get_places_by_category(db, category)
    return crud.get_all_places(db)

@router.post("/places/", response_model=schemas.Place)
def create_place(place: schemas.PlaceCreate, db: Session = Depends(get_db)):
    return crud.create_place(db, place)

@router.get("/courses/", response_model=list[schemas.Course])
def read_courses(db: Session = Depends(get_db)):
    return crud.get_all_courses(db)

@router.post("/courses/", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    return crud.create_course(db, course)

@router.get("/courses/{course_id}/places", response_model=list[schemas.CoursePlace])
def read_course_places(course_id: int, db: Session = Depends(get_db)):
    return crud.get_places_by_course(db, course_id) 