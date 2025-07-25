from sqlalchemy import Column, Integer, String, Text
from database import Base

class Festival(Base):
    __tablename__ = "festivals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(String)
    time = Column(String)
    location = Column(String)
    description = Column(Text)
    contact = Column(String)
    image_url = Column(String)
    programs = Column(Text)
    schedule = Column(String)        
    url = Column(String)
