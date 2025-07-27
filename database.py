from dotenv import load_dotenv
load_dotenv()  # .env 파일 자동 로드

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# 환경 설정에서 DB URL 가져오기
DATABASE_URL = settings.DATABASE_URL

# SQLite인 경우 연결 문자열 수정
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL, MySQL 등 외부 DB용
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DB 의존성 (FastAPI용)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

