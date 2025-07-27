from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

from database import SessionLocal
from models import Festival

def crawl_sejong_fire_festival():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    festival_info = {
        "name": "세종낙화축제",
        "date": "",
        "time": "",
        "location": "",
        "description": "",
        "contact": "",
        "image_url": "",
        "programs": "",
        "schedule": "",
        "url": "https://www.sjcf.or.kr/content.do?key=2111060044"
    }

    def update_if_better(key, new_val):
        if not new_val:
            return
        if key == "description" and new_val in festival_info[key]:
            return
        if not festival_info[key] or len(new_val.strip()) > len(festival_info[key]):
            festival_info[key] = new_val.strip()

    # 1. 세종시청 공식 홈페이지
    try:
        driver.get("https://www.sejong.go.kr/tour/sub02_0103.do")
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        desc_el = soup.select_one(".info_txt p")
        if desc_el:
            update_if_better("description", desc_el.get_text())

        img_tag = soup.select_one(".photo_wrap02 .img_box img")
        if img_tag:
            update_if_better("image_url", "https://www.sejong.go.kr" + img_tag["src"])

        for li in soup.select(".photo_wrap02 .txt_box li"):
            text = li.get_text(strip=True)
            if "장소" in text:
                update_if_better("location", text.split("장소")[-1].strip())
            elif "연락처" in text:
                update_if_better("contact", text.split("연락처")[-1].strip())
            elif "기간" in text:
                update_if_better("date", text.split("기간")[-1].strip())
    except Exception as e:
        print(f"[sejong.go.kr] 오류: {e}")

    # 2. 세종문화재단
    try:
        driver.get("https://www.sjcf.or.kr/content.do?key=2111060044")
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        img_tag = soup.select_one(".img_box img")
        if img_tag and not festival_info["image_url"]:
            update_if_better("image_url", "https://www.sjcf.or.kr" + img_tag["src"])

        ul_tags = soup.select("ul.info_ul li")
        guide_text = []
        for li in ul_tags:
            title = li.select_one("span.stit")
            if not title:
                continue
            title_text = title.get_text(strip=True)
            content = li.get_text(strip=True).replace(title_text, "")
            if "소개" in title_text:
                update_if_better("description", content)
            elif "기간" in title_text:
                sub_li = li.select("ul.list1 li")
                if sub_li:
                    update_if_better("date", sub_li[0].get_text(strip=True))
                else:
                    update_if_better("date", content)
            elif "장소" in title_text:
                update_if_better("location", content)
            elif "문의" in title_text:
                update_if_better("contact", content)
            elif "축제가이드" in title_text:
                for g in li.select("ul.list1 li"):
                    guide_text.append("- " + g.get_text(strip=True))

        if guide_text:
            guide_section = "\n\n[축제가이드]\n" + "\n".join(guide_text)
            update_if_better("description", festival_info["description"] + guide_section)
    except Exception as e:
        print(f"[sjcf.or.kr] 오류: {e}")

    # 3. 시간 처리
    if not festival_info["time"]:
        if "19:30" in festival_info["description"]:
            festival_info["time"] = "2025년 4월 26일 19:30 ~"
        else:
            festival_info["time"] = "홈페이지 참고"

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
    crawl_sejong_fire_festival()
