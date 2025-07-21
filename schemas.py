from pydantic import BaseModel

class HotPlaceBase(BaseModel):
    name: str
    category: str
    lat: float
    lng: float
    description: str
    is_official: bool = False

class HotPlaceCreate(HotPlaceBase):
    pass

class HotPlace(HotPlaceBase):
    id: int
    likes: int

    class Config:
        orm_mode = True

class FestivalBase(BaseModel):
    name: str
    date: str
    location: str
    lat: float
    lng: float
    description: str
    is_university: bool = False

class FestivalCreate(FestivalBase):
    pass

class Festival(FestivalBase):
    id: int

    class Config:
        orm_mode = True

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
        orm_mode = True
