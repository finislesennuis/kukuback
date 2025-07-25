from sqlalchemy.orm import Session

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

