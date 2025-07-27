from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class Festival(Base):
    __tablename__ = "festivals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(String)
    time = Column(String)
    location = Column(String)
    description = Column(Text)  # 실제 DB 테이블 구조에 맞게 수정
    contact = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    programs = Column(Text, nullable=True)
    schedule = Column(String, nullable=True)        
    url = Column(String, nullable=True)
    lat = Column(Float, nullable=True)  # 위도
    lng = Column(Float, nullable=True)  # 경도

class YouTubeLink(Base):
    __tablename__ = "youtube_links"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)        # 영상 제목
    url = Column(String, nullable=False)           # 유튜브 URL
    description = Column(Text)                     # 설명 (선택)
    created_at = Column(String)                    # 등록일자 문자열로 (예: 2025-07-22)

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    img = Column(String)
    detail_url = Column(String)

class CoursePlace(Base):
    __tablename__ = "course_places"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer)
    place_name = Column(String, nullable=False)

class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # 카테고리(필수)
    address = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    description = Column(Text)
    homepage = Column(String)
    url = Column(String)  # 원본 세종시 홈페이지 URL

class RequestStatus(enum.Enum):
    pending = "pending"
    done = "done"
    failed = "failed"

class CrawlRequest(Base):
    __tablename__ = "crawl_requests"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CrawledData(Base):
    __tablename__ = "crawled_data"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
