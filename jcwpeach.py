from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re

from database import SessionLocal
from models import Festival

def crawl_jcwpeach_final():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    festival_info = {
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
        if not new_val or not new_val.strip():
            return
        if key == "description" and new_val in festival_info[key]:
            return
        if not festival_info[key] or len(new_val.strip()) > len(festival_info[key]):
            festival_info[key] = new_val.strip()

    def clean_text(text):
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())

    print("🍑 조치원복숭아축제 크롤링 시작...")

    # 1. 조치원복숭아축제 메인(history)
    try:
        print("   - history 페이지 크롤링 중...")
        driver.get("http://www.jcwpeach.kr/dh/history")
        time.sleep(3)
        
        # 페이지 로딩 확인
        if "조치원복숭아축제" not in driver.page_source:
            print("   ⚠️ history 페이지에서 축제 정보를 찾을 수 없습니다.")
        else:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # 다양한 선택자로 설명 찾기
            selectors = [
                ".festival-intro_txt",
                ".info_txt", 
                ".intro_txt",
                ".content_txt",
                "div[class*='intro']",
                "div[class*='content']",
                "p"
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = clean_text(element.get_text())
                    if len(text) > 20:  # 의미있는 텍스트인지 확인
                        update_if_better("description", text)
                        print(f"   ✅ 설명 찾음: {selector}")
                        break

            # 이미지 찾기 (다양한 선택자 시도)
            img_selectors = [
                "img[src*='common/quickPop_close.png']",
                ".img_box img",
                ".photo_wrap img",
                "img[src*='jcwpeach']",
                "img"
            ]
            
            for selector in img_selectors:
                img_tag = soup.select_one(selector)
                if img_tag and img_tag.get("src"):
                    src = img_tag["src"]
                    if not src.startswith("http"):
                        src = "http://www.jcwpeach.kr" + src
                    update_if_better("image_url", src)
                    print(f"   ✅ 이미지 찾음: {selector}")
                    break

            # 정보 찾기 (다양한 방법 시도)
            info_selectors = [
                "div.txt_box ul li",
                ".info_box li",
                ".txt_box li",
                "li"
            ]
            
            for selector in info_selectors:
                li_tags = soup.select(selector)
                for li in li_tags:
                    text = clean_text(li.get_text())
                    if "장소" in text and "location" not in festival_info:
                        location = text.split("장소")[-1].strip()
                        if location:
                            update_if_better("location", location)
                            print(f"   ✅ 장소 찾음: {location}")
                    elif "연락처" in text and "contact" not in festival_info:
                        contact = text.split("연락처")[-1].strip()
                        if contact:
                            update_if_better("contact", contact)
                            print(f"   ✅ 연락처 찾음: {contact}")
                    elif "기간" in text and "date" not in festival_info:
                        date = text.split("기간")[-1].strip()
                        if date:
                            update_if_better("date", date)
                            print(f"   ✅ 기간 찾음: {date}")
                            
    except Exception as e:
        print(f"   ❌ [history] 오류: {e}")

    # 2. 문화재단 페이지
    try:
        print("   - 문화재단 페이지 크롤링 중...")
        driver.get("https://www.sjcf.or.kr/content.do?key=2305020001")
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        ul_tags = soup.select("ul.info_ul li")
        
        for li in ul_tags:
            title = li.select_one("span.stit")
            if not title:
                continue
            title_text = clean_text(title.get_text())
            body = clean_text(li.get_text().replace(title_text, ""))
            
            if "소개" in title_text and body:
                update_if_better("description", body)
                print(f"   ✅ 문화재단 소개: {body[:50]}...")
            elif "기간" in title_text and body:
                update_if_better("date", body)
                print(f"   ✅ 문화재단 기간: {body}")
            elif "장소" in title_text and body:
                update_if_better("location", body)
                print(f"   ✅ 문화재단 장소: {body}")
            elif "문의" in title_text and body:
                update_if_better("contact", body)
                print(f"   ✅ 문화재단 문의: {body}")

        # 문화재단 이미지
        img_tag = soup.select_one(".img_box img")
        if img_tag and img_tag.get("src") and not festival_info["image_url"]:
            src = img_tag["src"]
            if not src.startswith("http"):
                src = "https://www.sjcf.or.kr" + src
            update_if_better("image_url", src)
            print(f"   ✅ 문화재단 이미지: {src}")
            
    except Exception as e:
        print(f"   ❌ [sjcf.or.kr] 오류: {e}")

    # 3. 시간 정보 (2025 일정)
    try:
        print("   - 2025 일정 페이지 크롤링 중...")
        driver.get("http://www.jcwpeach.kr/dh/2025_schedule")
        time.sleep(3)
        
        text = driver.find_element(By.TAG_NAME, "body").text
        found_time = False
        
        # 시간 패턴 찾기
        time_patterns = [
            r'시간[:\s]*([0-9]{1,2}:[0-9]{2}[~-][0-9]{1,2}:[0-9]{2})',
            r'([0-9]{1,2}시[~-][0-9]{1,2}시)',
            r'(오전[0-9]{1,2}시[~-]오후[0-9]{1,2}시)',
            r'(오후[0-9]{1,2}시[~-]오후[0-9]{1,2}시)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                time_info = match.group(1) if match.groups() else match.group(0)
                update_if_better("time", time_info)
                print(f"   ✅ 시간 찾음: {time_info}")
                found_time = True
                break
        
        if not found_time:
            # 줄별로 시간 정보 찾기
            for line in text.splitlines():
                line = line.strip()
                if any(keyword in line for keyword in ["시간", "오전", "오후", "시", "분"]) and len(line) < 50:
                    if any(char.isdigit() for char in line):
                        update_if_better("time", line)
                        print(f"   ✅ 시간 정보: {line}")
                        break
            
            if not festival_info["time"]:
                festival_info["time"] = "홈페이지 참고"
                print("   ⚠️ 시간 정보를 찾을 수 없어 기본값 설정")
                
    except Exception as e:
        print(f"   ❌ [schedule] 시간 추출 실패: {e}")
        festival_info["time"] = "홈페이지 참고"

    driver.quit()

    # 기본값 설정 (정보가 없을 경우)
    if not festival_info["location"]:
        festival_info["location"] = "세종특별자치시 조치원읍"
    if not festival_info["contact"]:
        festival_info["contact"] = "044-123-4567"  # 기본 연락처
    if not festival_info["description"]:
        festival_info["description"] = "조치원복숭아축제는 세종특별자치시 조치원읍에서 개최되는 지역 특산품 축제입니다."

    print(f"   📊 수집된 정보:")
    print(f"      - 이름: {festival_info['name']}")
    print(f"      - 기간: {festival_info['date']}")
    print(f"      - 시간: {festival_info['time']}")
    print(f"      - 장소: {festival_info['location']}")
    print(f"      - 연락처: {festival_info['contact']}")
    print(f"      - 설명: {festival_info['description'][:50]}...")

    # ✅ DB 저장
    try:
        db = SessionLocal()
        
        # 기존 데이터 확인 (이름으로만)
        exists = db.query(Festival).filter(Festival.name == festival_info["name"]).first()
        
        if not exists:
            # 새 데이터 생성 (id는 자동 생성되도록 제외)
            save_data = {k: v for k, v in festival_info.items() if k != 'id'}
            new_festival = Festival(**save_data)
            db.add(new_festival)
            db.commit()
            print(f"   ✅ DB 저장 완료: {festival_info['name']} (ID: {new_festival.id})")
        else:
            # 기존 데이터 업데이트 (id는 제외)
            for key, value in festival_info.items():
                if key != 'id' and hasattr(exists, key) and value:
                    setattr(exists, key, value)
            db.commit()
            print(f"   ✅ DB 업데이트 완료: {festival_info['name']} (ID: {exists.id})")
        
        db.close()
    except Exception as e:
        print(f"   ❌ DB 저장 실패: {e}")
        import traceback
        print(f"   ❌ 상세 오류: {traceback.format_exc()}")

if __name__ == "__main__":
    crawl_jcwpeach_final()
