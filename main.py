from fastapi import FastAPI
from routes import festivals

from models import Festival
from database import Base, engine  
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(festivals.router)


@app.get("/")
def root():
    return {"message": "세종 축제 미니맵 백엔드입니다"}
