from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

from database import SessionLocal
from models import Festival
from models import Base
from database import engine

Base.metadata.create_all(bind=engine)

def crawl_jcwpeach_final():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    festival_info = {
        "id": 2,
        "name": "조치원복숭아축제",
        "date": "",
        "time": "",
        "location": "",
        "description": "",
        "contact": "",
        "image_url": "",
        "programs": "http://www.jcwpeach.kr/dh_product/prod_list",
        "schedule": "http://www.jcwpeach.kr/dh/2025_schedule",
        "url": "http://www.jcwpeach.kr/"
    }

    def update_if_better(key, new_val):
        if not new_val:
            return
        if key == "description" and new_val in festival_info[key]:
            return
        if not festival_info[key] or len(new_val.strip()) > len(festival_info[key]):
            festival_info[key] = new_val.strip()

    # 1. 조치원복숭아축제 메인(history)
    try:
        driver.get("http://www.jcwpeach.kr/dh/history")
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        intro_txt = soup.select_one(".festival-intro_txt")
        info_txt = soup.select_one(".info_txt")
        if intro_txt:
            update_if_better("description", intro_txt.get_text(separator="\n"))
        if info_txt:
            update_if_better("description", info_txt.get_text(separator="\n"))

        img_tag = soup.select_one("img[src*='common/quickPop_close.png']")
        if img_tag:
            update_if_better("image_url", "http://www.jcwpeach.kr" + img_tag["src"])

        li_tags = soup.select("div.txt_box ul li")
        for li in li_tags:
            text = li.get_text()
            if "장소" in text:
                update_if_better("location", text.split("장소")[-1].strip())
            elif "연락처" in text:
                update_if_better("contact", text.split("연락처")[-1].strip())
            elif "기간" in text:
                update_if_better("date", text.split("기간")[-1].strip())
    except Exception as e:
        print(f"[history] 오류: {e}")

    # 2. 문화재단 페이지
    try:
        driver.get("https://www.sjcf.or.kr/content.do?key=2305020001")
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        ul_tags = soup.select("ul.info_ul li")
        for li in ul_tags:
            title = li.select_one("span.stit")
            if not title:
                continue
            title_text = title.get_text(strip=True)
            body = li.get_text(strip=True).replace(title_text, "")
            if "소개" in title_text:
                update_if_better("description", body)
            elif "기간" in title_text:
                update_if_better("date", body)
            elif "장소" in title_text:
                update_if_better("location", body)
            elif "문의" in title_text:
                update_if_better("contact", body)

        img_tag = soup.select_one(".img_box img")
        if img_tag and not festival_info["image_url"]:
            update_if_better("image_url", "https://www.sjcf.or.kr" + img_tag["src"])
    except Exception as e:
        print(f"[sjcf.or.kr] 오류: {e}")

    # 3. 시간 (2025 일정)
    try:
        driver.get("http://www.jcwpeach.kr/dh/2025_schedule")
        time.sleep(1)
        text = driver.find_element(By.TAG_NAME, "body").text
        found_time = False
        for line in text.splitlines():
            if "시간" in line and ("오전" in line or "오후" in line or ":" in line or "~" in line):
                update_if_better("time", line.strip())
                found_time = True
                break
        if not found_time:
            festival_info["time"] = "홈페이지 참고"
    except Exception as e:
        print("[schedule] 시간 추출 실패:", e)
        festival_info["time"] = "홈페이지 참고 (http://www.jcwpeach.kr/dh/2025_schedule)"

    driver.quit()

    # ✅ DB 저장
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
    crawl_jcwpeach_final()
