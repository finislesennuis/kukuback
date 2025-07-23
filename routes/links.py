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

@router.get("/sejong-youtube-link")
def get_sejong_youtube_link():
    """
    세종시 공식 유튜브 링크를 반환하는 API
    """
    return {"url": "https://www.youtube.com/@sejongcity/featured"}