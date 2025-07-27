import requests
from database import SessionLocal
from models import Place

# 카카오 REST API 키 (사용자 본인의 키로 교체하세요)
KAKAO_API_KEY = "a5cc7b65ae5d251113eff578a56cd8f1"

# 축제 정보 (사용자가 원하는 축제 이름과 주소를 입력하세요)
festivals = {
    "세종축제": "세종특별자치시 세종동 1201",
    "조치원복숭아축제": "세종특별자치시 조치원읍 대첩로 98",
    "세종낙화축제": "세종특별자치시 세종동 1201",  # 예시 주소, 실제 주소로 변경 가능
    "세종 빛 축제": "세종특별자치시 보람동 623-1"   # 예시 주소, 실제 주소로 변경 가능
}

# 소상공인 기준 추천 카테고리 정의
recommendation_categories = {
    "맛집": {
        "keywords": ["맛집", "음식점", "한식", "중식", "일식", "양식", "분식", "치킨", "피자", "족발", "보쌈", "닭갈비", "삼겹살", "갈비", "국수", "칼국수", "냉면", "떡볶이", "순대", "김밥", "도시락", "백반", "정식"],
        "max_count": 15,
        "sort_by": "rating"  # 별점 위주
    },
    "카페": {
        "keywords": ["카페", "커피", "디저트", "베이커리", "빵집", "제과점", "아이스크림", "팥빙수", "빙수"],
        "max_count": 10,
        "sort_by": "rating"  # 별점 위주
    },
    "공원/휴식": {
        "keywords": ["공원", "휴식", "산책", "정원", "산책로"],
        "max_count": 3,
        "sort_by": "distance"  # 거리 위주
    },
    "문화/관광": {
        "keywords": ["박물관", "미술관", "전시관", "문화재", "관광지", "문화센터", "도서관"],
        "max_count": 5,
        "sort_by": "distance"  # 거리 위주
    }
}

# API 요청 헤더
headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}

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
        print("주소를 좌표로 변환할 수 없습니다. 주소를 확인하세요.")
        return None, None
    
    x = data["documents"][0]["x"]  # 경도
    y = data["documents"][0]["y"]  # 위도
    return x, y

def search_places_by_category(x, y, category_info, radius=2000):
    """카테고리별로 장소를 검색하는 함수"""
    search_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    all_places = []
    
    for keyword in category_info["keywords"]:
        params = {
            "query": keyword,
            "x": x,
            "y": y,
            "radius": radius,
            "size": 15  # 더 많은 결과를 가져와서 필터링
        }
        response = requests.get(search_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            for doc in data.get("documents", []):
                # 소상공인 기준 필터링 (대형 체인점 제외)
                place_name = doc.get("place_name", "")
                exclude_keywords = [
                    # 대형 마트/편의점
                    "롯데마트", "이마트", "홈플러스", "코스트코", "농협하나로마트",
                    # 대형 영화관
                    "메가박스", "CGV", "롯데시네마", "씨네Q",
                    # 대형 카페 체인
                    "스타벅스", "투썸플레이스", "할리스", "엔제리너스", "카페베네", "탐앤탐스",
                    # 대형 패스트푸드
                    "맥도날드", "KFC", "버거킹", "롯데리아", "맘스터치",
                    # 대형 치킨 체인
                    "교촌치킨", "BHC", "네네치킨", "BBQ", "처갓집", "호식이두마리치킨",
                    # 기타 대형 프랜차이즈
                    "올리브영", "다이소", "미니스톱", "세븐일레븐", "GS25", "CU"
                ]
                if any(exclude in place_name.lower() for exclude in exclude_keywords):
                    continue
                
                place = {
                    "name": place_name,
                    "address": doc.get("road_address_name", doc.get("address_name", "주소 없음")),
                    "phone": doc.get("phone", "전화번호 없음"),
                    "url": doc.get("place_url", "URL 없음"),
                    "distance": doc.get("distance", "0"),
                    "category": keyword,
                    "category_type": next((cat for cat, info in recommendation_categories.items() if keyword in info["keywords"]), "기타"),
                    "rating": doc.get("rating", "0"),  # 별점 정보
                    "review_count": doc.get("review_count", "0")  # 리뷰 수
                }
                all_places.append(place)
    
    # 중복 제거 (이름 기준)
    unique_places = []
    seen_names = set()
    for place in all_places:
        if place["name"] not in seen_names:
            unique_places.append(place)
            seen_names.add(place["name"])
    
    # 정렬 기준에 따라 정렬
    if category_info["sort_by"] == "rating":
        # 별점 순 정렬 (별점이 높은 순, 같으면 리뷰 수 많은 순)
        unique_places.sort(key=lambda x: (
            float(x["rating"]) if x["rating"] != "0" else 0,
            int(x["review_count"]) if x["review_count"].isdigit() else 0
        ), reverse=True)
    else:  # distance
        # 거리 순 정렬
        unique_places.sort(key=lambda x: int(x["distance"]) if x["distance"].isdigit() else float('inf'))
    
    return unique_places[:category_info["max_count"]]

def display_recommendations(festival_name, recommendations):
    """추천 결과를 카테고리별로 출력하는 함수"""
    if not recommendations:
        print(f"\n[{festival_name}] 반경 2km 내에 추천할 만한 곳이 없습니다.")
        return
    
    print(f"\n🎉 [{festival_name}] 반경 2km 내 소상공인 추천 장소 {len(recommendations)}곳:")
    print("=" * 70)
    
    # 카테고리별로 그룹화
    categorized = {}
    for place in recommendations:
        cat_type = place["category_type"]
        if cat_type not in categorized:
            categorized[cat_type] = []
        categorized[cat_type].append(place)
    
    # 카테고리별 출력
    for category, places in categorized.items():
        print(f"\n📍 {category} ({len(places)}곳)")
        print("-" * 50)
        for i, place in enumerate(places, 1):
            print(f"{i}. {place['name']}")
            print(f"   📍 {place['address']}")
            print(f"   📞 {place['phone']}")
            print(f"   🚶‍♂️ 거리: {place['distance']}m")
            
            # 별점 정보 표시 (맛집, 카페인 경우)
            if category in ["맛집", "카페"] and place["rating"] != "0":
                rating = float(place["rating"])
                stars = "⭐" * int(rating) + "☆" * (5 - int(rating))
                print(f"   ⭐ 평점: {rating} ({stars})")
                if place["review_count"] != "0":
                    print(f"   💬 리뷰: {place['review_count']}개")
            
            print(f"   🏷️ {place['category']}")
            if i < len(places):
                print()

def save_places_to_db(festival=None, address=None):
    """주변 장소 크롤링 후 Place 테이블에 저장"""
    if not address and festival:
        address = festivals.get(festival)
    if not address:
        print("축제 이름 또는 주소가 필요합니다.")
        return
    x, y = get_coordinates_from_address(address)
    if x is None or y is None:
        print("좌표 변환 실패")
        return
    all_recommendations = []
    for category_name, category_info in recommendation_categories.items():
        places = search_places_by_category(x, y, category_info, radius=2000)
        for place in places:
            place["category"] = category_name
        all_recommendations.extend(places)
    # 중복 제거 (이름+주소 기준)
    unique_recommendations = []
    seen = set()
    for place in all_recommendations:
        key = (place["name"], place["address"])
        if key not in seen:
            unique_recommendations.append(place)
            seen.add(key)
    # DB 저장
    db = SessionLocal()
    for place in unique_recommendations:
        exists = db.query(Place).filter(Place.name == place["name"], Place.address == place["address"]).first()
        if not exists:
            new_place = Place(
                name=place["name"],
                category=place["category"],
                address=place["address"],
                lat=float(place.get("x", 0)),
                lng=float(place.get("y", 0)),
                description=place.get("category_type", ""),
                homepage=None,
                url=place.get("url", None)
            )
            db.add(new_place)
    db.commit()
    db.close()
    print(f"✅ {festival or address} 주변 장소 DB 저장 완료")

def main():
    # 사용자에게 축제 선택 요청
    print("🎪 사용 가능한 축제:")
    for i, festival in enumerate(festivals.keys(), 1):
        print(f"{i}. {festival}")
    
    selected_festival = input("\n축제를 선택하세요 (번호 또는 이름): ").strip()
    
    # 번호로 선택한 경우 처리
    if selected_festival.isdigit():
        festival_list = list(festivals.keys())
        try:
            selected_festival = festival_list[int(selected_festival) - 1]
        except IndexError:
            print("잘못된 번호입니다.")
            return
    
    # 선택한 축제의 주소 가져오기
    address = festivals.get(selected_festival)
    if not address:
        print("잘못된 축제 이름입니다. 사용 가능한 축제를 확인하세요.")
        return
    
    print(f"\n🔍 {selected_festival} 주변 소상공인 장소를 검색 중입니다...")
    
    # 주소를 좌표로 변환
    x, y = get_coordinates_from_address(address)
    if x is None or y is None:
        return
    
    # 모든 카테고리의 장소 검색
    all_recommendations = []
    for category_name, category_info in recommendation_categories.items():
        print(f"   {category_name} 검색 중...")
        places = search_places_by_category(x, y, category_info, radius=2000)
        all_recommendations.extend(places)
    
    # 중복 제거
    unique_recommendations = []
    seen_names = set()
    for place in all_recommendations:
        if place["name"] not in seen_names:
            unique_recommendations.append(place)
            seen_names.add(place["name"])
    
    # 결과 출력
    display_recommendations(selected_festival, unique_recommendations)
    
    print(f"   축제 위치: {address}")

if __name__ == "__main__":
    main()