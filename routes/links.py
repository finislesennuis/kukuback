from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import schemas, crud

router = APIRouter()

@router.get("/links/", response_model=list[schemas.YouTubeLink])
def read_links(db: Session = Depends(get_db)):
    return crud.get_all_youtube_links(db)

@router.post("/links/", response_model=schemas.YouTubeLink)
def create_link(link: schemas.YouTubeLinkCreate, db: Session = Depends(get_db)):
    return crud.create_youtube_link(db, link)
