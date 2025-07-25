from pydantic import BaseModel

class FestivalBase(BaseModel):
    name: str
    date: str
    time: str
    location: str
    description: str
    contact: str
    image_url: str
    programs: str
    url: str

class FestivalCreate(FestivalBase):
    pass

class Festival(FestivalBase):
    id: int

    class Config:
        from_attributes = True  # <- ✅ pydantic v2 기준 변경
