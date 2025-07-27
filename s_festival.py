import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from database import SessionLocal
from models import Festival

def clean_text(text):
    return re.sub(r"(아이콘|주소|\s+)", " ", text).strip()

def clean_date(text):
    text = re.sub(r"\s+", "", text)
    match = re.search(r"(20[0-9]{2}[./]?\d{1,2}[./]?\d{1,2}).*?(20[0-9]{2}[./]?\d{1,2}[./]?\d{1,2})", text)
    return f"{match.group(1)} ~ {match.group(2)}" if match else text.strip()

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def crawl_sjcf(driver):
    driver.get("https://www.sjcf.or.kr/content.do?key=2111060043")
    time.sleep(2)
    info = {}

    try:
        desc = driver.find_element(By.XPATH, "//span[contains(text(), '소개')]/following-sibling::ul")
        info["description"] = desc.text.strip()
    except: pass

    try:
        date = driver.find_element(By.XPATH, "//span[contains(text(), '기간')]/following-sibling::ul")
        info["date"] = clean_date(date.text)
    except: pass

    try:
        loc = driver.find_element(By.XPATH, "//span[contains(text(), '장소')]").find_element(By.XPATH, "./following::li")
        content = loc.text.strip()
        if any(k in content for k in ["세종호수공원", "세종중앙공원", "일원", "광장", "무대", "도로", "특별자치시"]):
            info["location"] = clean_text(content)
    except: pass

    try:
        tel = driver.find_element(By.CSS_SELECTOR, "a[href^='tel']")
        info["contact"] = tel.text.strip()
    except: pass

    try:
        img = driver.find_element(By.CSS_SELECTOR, "div.img_box img")
        src = img.get_attribute("src")
        info["image_url"] = src if src.startswith("http") else "https://www.sjcf.or.kr" + src
    except: pass

    return info

def crawl_sejong_tour(driver):
    driver.get("https://www.sejong.go.kr/tour/sub02_0101.do")
    time.sleep(2)
    info = {}

    try:
        desc = driver.find_element(By.CSS_SELECTOR, "div.info_txt > p")
        info["description"] = desc.text.strip()
    except: pass

    try:
        for li in driver.find_elements(By.CSS_SELECTOR, "ul li"):
            text = li.text.strip()
            if "장소" in text and "location" not in info:
                info["location"] = clean_text(text.replace("장소", ""))
            elif "기간" in text and "date" not in info:
                info["date"] = clean_date(text.replace("기간", ""))
            elif "연락처" in text and "contact" not in info:
                info["contact"] = text.replace("연락처", "")
    except: pass

    try:
        img = driver.find_element(By.CSS_SELECTOR, "div.img_box img")
        src = img.get_attribute("src")
        info["image_url"] = src if src.startswith("http") else "https://www.sejong.go.kr" + src
    except: pass

    return info

def crawl_sejong_festival():
    driver = get_driver()
    info = {
        "name": "세종축제",
        "url": "http://sjfestival.kr/",
        "time": "홈페이지 참고"
    }

    for data in [crawl_sjcf(driver), crawl_sejong_tour(driver)]:
        for k, v in data.items():
            if v and not info.get(k):
                info[k] = v

    info["programs"] = "http://sjfestival.kr/dh_product/prod_list"
    info["schedule"] = "http://sjfestival.kr/dh/program_schedule"

    if not info.get("description"):
        info["description"] = "세종축제 소개는 홈페이지 참고"

    driver.quit()
    return info

def save_to_db(info):
    try:
        db = SessionLocal()
        # 이름으로만 중복 체크 (더 유연한 방식)
        exists = db.query(Festival).filter(Festival.name == info["name"]).first()

        if not exists:
            # 새 데이터 생성
            save_data = {
                "name": info.get("name", ""),
                "date": info.get("date", ""),
                "time": info.get("time", ""),
                "location": info.get("location", ""),
                "description": info.get("description", ""),
                "contact": info.get("contact", ""),
                "image_url": info.get("image_url", ""),
                "programs": info.get("programs", ""),
                "schedule": info.get("schedule", ""),
                "url": info.get("url", "")
            }
            new_festival = Festival(**save_data)
            db.add(new_festival)
            db.commit()
            print(f"✅ 저장 완료: {info['name']} (ID: {new_festival.id})")
        else:
            # 기존 데이터 업데이트 (더 나은 정보가 있으면)
            updated = False
            for key, value in info.items():
                if key != 'id' and hasattr(exists, key) and value:
                    current_value = getattr(exists, key)
                    if not current_value or (isinstance(value, str) and len(value) > len(current_value)):
                        setattr(exists, key, value)
                        updated = True
            
            if updated:
                db.commit()
                print(f"🔄 업데이트 완료: {info['name']} (ID: {exists.id})")
            else:
                print(f"ℹ️ 기존 데이터가 더 우수함: {info['name']} (ID: {exists.id})")
        db.close()
        return True
    except Exception as e:
        print(f"❌ DB 저장 실패: {info['name']} - {e}")
        import traceback
        print(f"❌ 상세 오류: {traceback.format_exc()}")
        if 'db' in locals():
            db.close()
        return False

# ✅ 실행
if __name__ == "__main__":
    info = crawl_sejong_festival()
    save_to_db(info)
