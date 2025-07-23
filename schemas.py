from pydantic import BaseModel

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
        orm_mode = True

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
