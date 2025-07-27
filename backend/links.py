from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from importlib import import_module
schemas = import_module('schemas')
crud = import_module('crud')
import re

router = APIRouter()

@router.get("/links/", response_model=list[schemas.YouTubeLink])
def read_links(db: Session = Depends(get_db)):
    return crud.get_all_youtube_links(db)

@router.post("/links/", response_model=schemas.YouTubeLink)
def create_link(link: schemas.YouTubeLinkCreate, db: Session = Depends(get_db)):
    # 유튜브 URL 유효성 검사 (채널, 동영상, shorts 등 다양한 형식 허용)
    youtube_regex = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
    if not re.match(youtube_regex, link.url):
        raise HTTPException(status_code=400, detail="유효한 유튜브 URL이 아닙니다.")
    return crud.create_youtube_link(db, link)

@router.get("/sejong-youtube-link")
def get_sejong_youtube_link():
    """
    세종시 공식 유튜브 링크를 반환하는 API
    """
    return {"url": "https://www.youtube.com/@sejongcity/featured"}