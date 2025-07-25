from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import schemas, crud
from models import Festival
from utils import haversine  # ✅ 새로 추가한 유틸 함수

router = APIRouter()

# ✅ 기존 기능: 전체 조회
@router.get("/festivals/", response_model=list[schemas.Festival])
def read_festivals(db: Session = Depends(get_db)):
    return crud.get_all_festivals(db)

# ✅ 기존 기능: 축제 등록
@router.post("/festivals/", response_model=schemas.Festival)
def create_festival(festival: schemas.FestivalCreate, db: Session = Depends(get_db)):
    return crud.create_festival(db, festival)

@router.get("/festivals/map")
def get_festivals_for_map(db: Session = Depends(get_db)):
    festivals = crud.get_all_festivals(db)  # DB에서 모든 축제 불러오기
    return [
        {
            "id": f.id,
            "name": f.name,
            "lat": f.lat,
            "lng": f.lng,
            "date": f.date
        }
        for f in festivals
    ]

@router.delete("/festivals/clear")
def delete_all_festivals(db: Session = Depends(get_db)):
    db.query(Festival).delete()
    db.commit()
    return {"message": "모든 축제 데이터 삭제 완료"}
