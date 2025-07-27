from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from importlib import import_module
crud = import_module('crud')
from models import Festival, Place, Course

router = APIRouter()

@router.get("/search")
def search_all(
    q: str = Query(..., description="검색어"),
    db: Session = Depends(get_db)
):
    """
    축제, 장소, 코스에서 검색어를 포함하는 항목들을 검색
    """
    results = {
        "festivals": [],
        "places": [],
        "courses": []
    }
    
    # 축제 검색
    festivals = db.query(Festival).filter(
        Festival.name.contains(q) | 
        Festival.description.contains(q) |
        Festival.location.contains(q)
    ).all()
    results["festivals"] = [
        {
            "id": f.id,
            "name": f.name,
            "date": f.date,
            "location": f.location,
            "image_url": f.image_url,
            "type": "festival"
        }
        for f in festivals
    ]
    
    # 장소 검색
    places = db.query(Place).filter(
        Place.name.contains(q) | 
        Place.description.contains(q) |
        Place.category.contains(q)
    ).all()
    results["places"] = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "address": p.address,
            "type": "place"
        }
        for p in places
    ]
    
    # 코스 검색
    courses = db.query(Course).filter(
        Course.name.contains(q)
    ).all()
    results["courses"] = [
        {
            "id": c.id,
            "name": c.name,
            "img": c.img,
            "type": "course"
        }
        for c in courses
    ]
    
    return results 