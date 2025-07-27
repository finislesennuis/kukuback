"""
여행 코스 크롤링 모듈
- 세종시 공식 홈페이지에서 추천 여행코스 크롤링
"""

import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from database import SessionLocal
from models import Course, CoursePlace, Place

# 카카오 REST API 키 (주소를 좌표로 변환하기 위해 필요)
KAKAO_API_KEY = "a5cc7b65ae5d251113eff578a56cd8f1"
headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}

# 여행 추천 코스 URL들
course_urls = [
    {
        "name": "가족나들이 코스",
        "url": "https://www.sejong.go.kr/tour/sub02_0205.do",
        "description": "자연과 동물, 전통문화를 체험할 수 있는 가족 친화적 코스"
    },
    {
        "name": "도시탐방 코스", 
        "url": "https://www.sejong.go.kr/tour/sub02_0206.do",
        "description": "세종시의 대표적인 도시 명소들을 둘러보는 코스"
    },
    {
        "name": "역사문화 코스",
        "url": "https://www.sejong.go.kr/tour/sub02_0207.do", 
        "description": "세종시의 역사와 문화를 체험할 수 있는 코스"
    },
    {
        "name": "원도심걷기 코스",
        "url": "https://www.sejong.go.kr/tour/sub02_0208.do",
        "description": "조치원 원도심의 전통과 현대가 어우러진 걷기 코스"
    }
]

def get_driver():
    """Selenium 드라이버 설정"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_coordinates_from_address(address):
    """주소를 좌표로 변환하는 함수"""
    geo_url = "https://dapi.kakao.com/v2/local/search/address.json"
    params = {"query": address}
    response = requests.get(geo_url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"주소 변환 API 요청 실패 (상태 코드: {response.status_code})")
        return None, None
    
    data = response.json()
    if not data.get("documents"):
        print(f"주소를 좌표로 변환할 수 없습니다: {address}")
        return None, None
    
    x = data["documents"][0]["x"]  # 경도
    y = data["documents"][0]["y"]  # 위도
    return float(x), float(y)

def crawl_travel_course(driver, course_info):
    """여행 코스 크롤링 함수"""
    print(f"🔍 {course_info['name']} 크롤링 중...")
    
    driver.get(course_info["url"])
    time.sleep(2)
    
    # 코스 정보 저장
    db = SessionLocal()
    
    # 기존 코스 삭제 (중복 방지)
    existing_course = db.query(Course).filter(Course.name == course_info["name"]).first()
    if existing_course:
        # 기존 코스와 연결된 장소들도 삭제
        db.query(CoursePlace).filter(CoursePlace.course_id == existing_course.id).delete()
        db.delete(existing_course)
        db.commit()
        print(f"🔄 기존 코스 삭제: {course_info['name']}")
    
    # 새 코스 생성
    new_course = Course(
        name=course_info["name"],
        detail_url=course_info["url"]
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    course_id = new_course.id
    
    print(f"✅ 코스 생성 완료: {course_info['name']} (ID: {course_id})")
    
    # 코스에 포함된 장소들 크롤링
    course_elements = driver.find_elements(By.CSS_SELECTOR, "div.course")
    
    for i, element in enumerate(course_elements):
        try:
            # 장소명 추출
            title_element = element.find_element(By.CSS_SELECTOR, ".txt_box .tit span")
            place_name = title_element.text.strip()
            
            # 설명 추출
            desc_element = element.find_element(By.CSS_SELECTOR, ".txt_box p")
            description = desc_element.text.strip()
            
            # 주소 추출
            address_element = element.find_element(By.CSS_SELECTOR, ".f_wrap p")
            address_text = address_element.text.strip()
            # "주소" 텍스트 제거
            address = address_text.replace("주소", "").strip()
            
            print(f"   📍 {place_name} - {address}")
            
            # 주소를 위도/경도로 변환
            lat, lng = get_coordinates_from_address(address)
            if lat is None or lng is None:
                print(f"   ⚠️ 좌표 변환 실패: {place_name}")
                lat, lng = 0.0, 0.0
            else:
                print(f"   🗺️ 좌표 변환 완료: {lat}, {lng}")
            
            # Place 테이블에 저장 (중복 체크)
            existing_place = db.query(Place).filter(Place.name == place_name).first()
            if not existing_place:
                new_place = Place(
                    name=place_name,
                    category=course_info["name"],
                    address=address,
                    lat=lat,
                    lng=lng,
                    description=description
                )
                db.add(new_place)
                db.commit()
                print(f"   ✅ 장소 저장 완료: {place_name}")
            else:
                # 기존 장소 정보 업데이트
                existing_place.category = course_info["name"]
                existing_place.address = address
                existing_place.lat = lat
                existing_place.lng = lng
                existing_place.description = description
                db.commit()
                print(f"   🔄 장소 정보 업데이트: {place_name}")
            
            # CoursePlace 테이블에 저장 (코스-장소 연결)
            new_course_place = CoursePlace(
                course_id=course_id,
                place_name=place_name
            )
            db.add(new_course_place)
            print(f"   🔗 코스-장소 연결 완료: {place_name}")
            
        except Exception as e:
            print(f"   ❌ 장소 크롤링 오류: {e}")
            continue
    
    db.commit()
    db.close()
    print(f"🎉 {course_info['name']} 크롤링 완료!")
    return course_id

def run_course_crawler():
    """여행 코스 크롤링 실행"""
    print("🚀 세종시 여행 추천 코스 크롤링 시작!")
    print("=" * 50)
    
    # Selenium 드라이버 초기화
    driver = get_driver()
    
    try:
        # 여행 코스 크롤링
        print("\n🗺️ 여행 추천 코스 크롤링 중...")
        for course_info in course_urls:
            try:
                course_id = crawl_travel_course(driver, course_info)
                print(f"   코스 ID: {course_id}")
            except Exception as e:
                print(f"❌ {course_info['name']} 크롤링 실패: {e}")
        
        print("\n" + "=" * 50)
        print("✅ 모든 여행 코스 크롤링 완료!")
        
    finally:
        driver.quit()
        print("\n🎯 크롤링 작업 완료!")

if __name__ == "__main__":
    run_course_crawler()
