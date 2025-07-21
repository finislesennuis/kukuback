import requests
from bs4 import BeautifulSoup
from database import SessionLocal
from models import Festival
import re

# 크롤링할 축제 URL 목록 (이름 + 상세페이지)
festival_pages = [
    {
        "name": "조치원복숭아축제",
        "url": "https://www.sejong.go.kr/tour/sub02_0102.do"
    },
    {
        "name": "세종낙화축제",
        "url": "https://www.sejong.go.kr/tour/sub02_0103.do"
    },
    {
        "name": "세종빛축제",
        "url": "https://www.sejong.go.kr/tour/sub02_0104.do"
    }
]

# ✅ 크롤링 및 DB 저장 함수
def crawl_and_save():
    db = SessionLocal()

    for fest in festival_pages:
        print(f"🔍 {fest['name']} 크롤링 시작")
        response = requests.get(fest["url"])
        soup = BeautifulSoup(response.text, "html.parser")

        # 🎯 설명
        desc_el = soup.select_one("div.view_cont") or soup.select_one("div.tour_summary") or soup.select_one("div.info")
        description = desc_el.get_text(separator="\n").strip() if desc_el else "설명 없음"

        # 📍 장소
        location = "세종시 일원"
        for li in soup.select("div.info li"):
            if "장소" in li.get_text():
                location = li.get_text().replace("장소", "").strip()
                break

        # 🕒 날짜
        date = "날짜 미정"
        for li in soup.select("div.info li"):
            if "기간" in li.get_text():
                date = li.get_text().replace("기간", "").strip()
                break

        # 📌 세종시 중심 좌표 (테스트용, 이후 위치 좌표화 필요)
        lat, lng = 36.504, 127.259

        # ✅ 중복 체크: 이름 + 날짜가 같은 경우 등록하지 않음
        exists = db.query(Festival).filter(
            Festival.name == fest["name"],
            Festival.date == date
        ).first()

        if not exists:
            new_festival = Festival(
                name=fest["name"],
                date=raw_date,
                location=location,
                lat=lat,
                lng=lng,
                description=description,
                is_university=False
            )
            db.add(new_festival)
            print(f"✅ 등록됨: {fest['name']}")

    db.commit()
    db.close()
    print("✅ 모든 축제 저장 완료")

# 실행
if __name__ == "__main__":
    crawl_and_save()
