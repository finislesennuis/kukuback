from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

from database import SessionLocal
from models import Festival

def crawl_sejong_light_festival():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    festival_info = {
        "name": "세종 빛 축제",
        "date": "",
        "time": "홈페이지 참고",
        "location": "",
        "description": "",
        "contact": "정보 없음",
        "image_url": "",
        "programs": "",
        "schedule": "",
        "url": "https://www.sejong.go.kr/tour/sub02_0104.do"
    }

    def update_if_better(key, new_val):
        if not new_val:
            return
        if key == "description" and new_val in festival_info[key]:
            return
        if not festival_info[key] or len(new_val.strip()) > len(festival_info[key]):
            festival_info[key] = new_val.strip()

    try:
        driver.get(festival_info["url"])
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 설명
        desc_el = soup.select_one("div.info_txt p")
        if desc_el:
            update_if_better("description", desc_el.get_text())

        # 대표 이미지
        img_tag = soup.select_one(".photo_wrap02 .img_box img")
        if img_tag:
            update_if_better("image_url", "https://www.sejong.go.kr" + img_tag["src"])

        # 장소 및 기간
        li_tags = soup.select(".photo_wrap02 .txt_box li")
        for li in li_tags:
            text = li.get_text(strip=True)
            if "주소" in text:
                update_if_better("location", text.split("주소")[-1].strip())
            elif "기간" in text:
                update_if_better("date", text.split("기간")[-1].strip())
    except Exception as e:
        print(f"[sejong.go.kr 빛축제] 오류: {e}")

    driver.quit()

    # DB 저장
    db = SessionLocal()
    exists = db.query(Festival).filter(Festival.name == festival_info["name"], Festival.date == festival_info["date"]).first()
    if not exists:
        new_festival = Festival(**festival_info)
        db.add(new_festival)
        db.commit()
        print(f"✅ 등록 완료: {festival_info['name']}")
    else:
        print(f"⚠️ 이미 존재: {festival_info['name']}")
    db.close()


if __name__ == "__main__":
    crawl_sejong_light_festival()
