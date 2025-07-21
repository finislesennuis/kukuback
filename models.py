from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from database import Base

class HotPlace(Base):
    __tablename__ = "hotplaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)  # 예: 음식점, 카페
    lat = Column(Float)
    lng = Column(Float)
    description = Column(Text)
    likes = Column(Integer, default=0)
    is_official = Column(Boolean, default=False)  # 공식 등록 여부

class Festival(Base):
    __tablename__ = "festivals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(String)  # 나중에 date 형식으로 바꿔도 됨
    location = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    description = Column(Text)
    is_university = Column(Boolean, default=False)  # 대학교 축제 여부

class YouTubeLink(Base):
    __tablename__ = "youtube_links"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)        # 영상 제목
    url = Column(String, nullable=False)           # 유튜브 URL
    description = Column(Text)                     # 설명 (선택)
    created_at = Column(String)                    # 등록일자 문자열로 (예: 2025-07-22)
