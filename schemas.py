from pydantic import BaseModel
from typing import List

class PlaceBase(BaseModel):
    name: str
    category: str
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    description: str | None = None
    homepage: str | None = None
    url: str | None = None

class PlaceCreate(PlaceBase):
    pass

class Place(PlaceBase):
    id: int
    class Config:
        from_attributes = True

class FestivalBase(BaseModel):
    name: str
    date: str
    time: str
    location: str
    description: str | None = None  # 실제 DB 테이블 구조에 맞게 수정
    contact: str | None = None
    image_url: str | None = None
    programs: str | None = None
    url: str | None = None
    lat: float | None = None
    lng: float | None = None

class FestivalCreate(FestivalBase):
    pass

class Festival(FestivalBase):
    id: int

    class Config:
        from_attributes = True

class YouTubeLinkBase(BaseModel):
    title: str
    url: str
    description: str
    created_at: str

class YouTubeLinkCreate(YouTubeLinkBase):
    pass

class YouTubeLink(YouTubeLinkBase):
    id: int

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    name: str
    img: str | None = None
    detail_url: str | None = None

class CourseCreate(CourseBase):
    places: List[str]

class Course(CourseBase):
    id: int
    class Config:
        from_attributes = True

class CoursePlaceBase(BaseModel):
    course_id: int
    place_name: str

class CoursePlaceCreate(CoursePlaceBase):
    pass

class CoursePlace(CoursePlaceBase):
    id: int
    class Config:
        from_attributes = True
