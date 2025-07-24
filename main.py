from fastapi import FastAPI
from routes import festivals, hotplaces, links
from routes.places import router as places_router

from models import HotPlace, Festival
from database import Base, engine
from models import YouTubeLink  
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(festivals.router)
app.include_router(hotplaces.router)
app.include_router(links.router)
app.include_router(places_router)

@app.get("/")
def root():
    return {"message": "세종 축제 미니맵 백엔드입니다"}
