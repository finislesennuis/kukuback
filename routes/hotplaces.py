from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import crud, schemas

router = APIRouter()

@router.get("/hotplaces/", response_model=list[schemas.HotPlace])
def read_hotplaces(db: Session = Depends(get_db)):
    return crud.get_all_hotplaces(db)

@router.post("/hotplaces/", response_model=schemas.HotPlace)
def create_hotplace(hotplace: schemas.HotPlaceCreate, db: Session = Depends(get_db)):
    return crud.create_hotplace(db, hotplace)

@router.post("/hotplaces/{hotplace_id}/like", response_model=schemas.HotPlace)
def like_hotplace(hotplace_id: int, db: Session = Depends(get_db)):
    hotplace = crud.like_hotplace(db, hotplace_id)
    if not hotplace:
        raise HTTPException(status_code=404, detail="존재하지 않는 핫플입니다")
    return hotplace
