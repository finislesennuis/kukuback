from fastapi import FastAPI, Request
import uvicorn
import requests
import os
from dotenv import load_dotenv

# 크롤링 함수 import
import s_festival
import s_light
import f_flower
import jcwpeach
import course_crawler
import s_place

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import CrawledData, Base

# .env에서 DB URL 불러오기
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "로컬 크롤러 서버가 실행 중입니다.", "status": "running"}

@app.post("/crawl")
async def crawl(request: Request):
    data = await request.json()
    req_type = data.get("type")
    url = data.get("url")
    festival = data.get("festival")
    address = data.get("address")
    
    print(f"🔍 크롤링 요청 받음: type={req_type}, url={url}, festival={festival}, address={address}")
    print(f"🔍 요청 데이터: {data}")

    # 축제 크롤링 (festival 타입)
    if req_type == "festival":
        try:
            print(f"🎪 축제 크롤링 시작: {url}")
            
            if "sjfestival.kr" in url or "sjcf.or.kr/content.do?key=2111060043" in url or "sejong.go.kr/tour/sub02_0101.do" in url:
                print("   - 세종축제 크롤링 중...")
                info = s_festival.crawl_sejong_festival()
                success = s_festival.save_to_db(info)
                if success:
                    print("   ✅ 세종축제 완료")
                    return {"status": "success", "detail": "세종축제 크롤링 및 DB 저장 완료"}
                else:
                    print("   ❌ 세종축제 DB 저장 실패")
                    return {"status": "error", "detail": "세종축제 DB 저장 실패"}
            elif "sejong.go.kr/tour/sub02_0104.do" in url:
                print("   - 세종 빛 축제 크롤링 중...")
                s_light.crawl_sejong_light_festival()
                print("   ✅ 세종 빛 축제 완료")
                return {"status": "success", "detail": "세종 빛 축제 크롤링 및 DB 저장 완료"}
            elif "sjcf.or.kr/content.do?key=2111060044" in url or "sejong.go.kr/tour/sub02_0103.do" in url:
                print("   - 세종 낙화축제 크롤링 중...")
                f_flower.crawl_sejong_fire_festival()
                print("   ✅ 세종 낙화축제 완료")
                return {"status": "success", "detail": "세종 낙화축제 크롤링 및 DB 저장 완료"}
            elif "jcwpeach.kr" in url:
                print("   - 조치원복숭아축제 크롤링 중...")
                jcwpeach.crawl_jcwpeach_final()
                print("   ✅ 조치원복숭아축제 완료")
                return {"status": "success", "detail": "조치원복숭아축제 크롤링 및 DB 저장 완료"}
            else:
                print(f"   ❌ 지원하지 않는 URL: {url}")
                return {"status": "error", "detail": "지원하지 않는 축제 URL입니다."}
        except Exception as e:
            import traceback
            print(f"❌ 축제 크롤링 오류: {e}")
            print(f"❌ 상세 오류: {traceback.format_exc()}")
            return {"status": "error", "detail": f"축제 크롤링 실패: {str(e)}"}

    # 여행코스 크롤링 (course 타입)
    elif req_type == "course":
        if "sejong.go.kr/tour/sub02_020" in url:
            course_crawler.run_course_crawler()
            return {"status": "success", "detail": "여행코스 크롤링 및 DB 저장 완료"}
        else:
            return {"status": "error", "detail": "지원하지 않는 여행코스 URL입니다."}

    # 주변 장소 크롤링 (places 타입)
    elif req_type == "places":
        s_place.save_places_to_db(festival=festival, address=address)
        return {"status": "success", "detail": "주변 장소 크롤링 및 DB 저장 완료"}

    # 기존 url 기반 분기 (하위 호환성)
    elif url:
        if "sjfestival.kr" in url or "sjcf.or.kr/content.do?key=2111060043" in url or "sejong.go.kr/tour/sub02_0101.do" in url:
            info = s_festival.crawl_sejong_festival()
            s_festival.save_to_db(info)
            return {"status": "success", "detail": "세종축제 크롤링 및 DB 저장 완료"}
        elif "sejong.go.kr/tour/sub02_0104.do" in url:
            s_light.crawl_sejong_light_festival()
            return {"status": "success", "detail": "세종 빛 축제 크롤링 및 DB 저장 완료"}
        elif "sjcf.or.kr/content.do?key=2111060044" in url or "sejong.go.kr/tour/sub02_0103.do" in url:
            f_flower.crawl_sejong_fire_festival()
            return {"status": "success", "detail": "세종 낙화축제 크롤링 및 DB 저장 완료"}
        elif "jcwpeach.kr" in url:
            jcwpeach.crawl_jcwpeach_final()
            return {"status": "success", "detail": "조치원복숭아축제 크롤링 및 DB 저장 완료"}
        elif "sejong.go.kr/tour/sub02_020" in url:
            course_crawler.run_course_crawler()
            return {"status": "success", "detail": "여행코스 크롤링 및 DB 저장 완료"}
        else:
            response = requests.get(url)
            result = response.text
            db = SessionLocal()
            crawled = CrawledData(url=url, data=result)
            db.add(crawled)
            db.commit()
            db.close()
            return {"status": "success", "url": url, "detail": "일반 URL 크롤링 및 CrawledData 저장 완료"}
    
    return {"status": "error", "detail": "지원하지 않는 요청입니다."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
