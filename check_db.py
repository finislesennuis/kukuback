from database import SessionLocal
from models import Festival

db = SessionLocal()
festivals = db.query(Festival).all()
for f in festivals:
    print(
        f"ID: {f.id}\n"
        f"이름: {f.name}\n"
        f"기간: {f.date}\n"
        f"시간: {f.time}\n"
        f"장소: {f.location}\n"
        f"설명: {f.description}\n"
        f"연락처: {f.contact}\n"
        f"포스터: {f.image_url}\n"
        f"프로그램: {f.programs}\n"
        f"행사 일정: {f.schedule}\n"
        f"홈페이지 주소: {f.url}\n"
        "-----------------------------"
    )
db.close()
