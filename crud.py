from sqlalchemy.orm import Session
from models import HotPlace
from schemas import HotPlaceCreate

def create_hotplace(db: Session, hotplace: HotPlaceCreate):
    db_hotplace = HotPlace(**hotplace.dict())
    db.add(db_hotplace)
    db.commit()
    db.refresh(db_hotplace)
    return db_hotplace

def get_all_hotplaces(db: Session):
    return db.query(HotPlace).all()

def like_hotplace(db: Session, hotplace_id: int):
    hotplace = db.query(HotPlace).filter(HotPlace.id == hotplace_id).first()
    if hotplace:
        hotplace.likes += 1
        db.commit()
        return hotplace
    return None

from models import Festival
from schemas import FestivalCreate

def create_festival(db: Session, festival: FestivalCreate):
    db_festival = Festival(**festival.dict())
    db.add(db_festival)
    db.commit()
    db.refresh(db_festival)
    return db_festival

def get_all_festivals(db: Session):
    return db.query(Festival).all()

from models import YouTubeLink
from schemas import YouTubeLinkCreate

def create_youtube_link(db: Session, link: YouTubeLinkCreate):
    db_link = YouTubeLink(**link.dict())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

def get_all_youtube_links(db: Session):
    return db.query(YouTubeLink).all()

from models import Place
import schemas

# 전체 장소 조회

def get_all_places(db: Session):
    return db.query(Place).all()

# 카테고리별 장소 조회

def get_places_by_category(db: Session, category: str):
    return db.query(Place).filter(Place.category == category).all()

# 장소 생성

def create_place(db: Session, place: schemas.PlaceCreate):
    db_place = Place(**place.dict())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

