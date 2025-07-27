from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from importlib import import_module
schemas = import_module('schemas')
crud = import_module('crud')
from models import Festival
from utils import haversine  # ✅ 새로 추가한 유틸 함수

router = APIRouter()

# ✅ 기존 기능: 전체 조회
@router.get("/festivals/")
def read_festivals(db: Session = Depends(get_db)):
    try:
        festivals = crud.get_all_festivals(db)
        result = []
        for f in festivals:
            result.append({
                "id": f.id,
                "name": f.name,
                "date": f.date,
                "time": f.time,
                "location": f.location,
                "description": f.description
            })
        return result
    except Exception as e:
        return {"error": str(e)}

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
