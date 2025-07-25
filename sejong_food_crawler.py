import requests

# 카카오 REST API 키 (사용자 본인의 키로 교체하세요)
KAKAO_API_KEY = "a5cc7b65ae5d251113eff578a56cd8f1"

# 축제 정보 (사용자가 원하는 축제 이름과 주소를 입력하세요)
festivals = {
    "세종축제": "세종특별자치시 세종동 1201",
    "조치원복숭아축제": "세종특별자치시 조치원읍 대첩로 98",
    "세종낙화축제": "세종특별자치시 세종동 1201",  # 예시 주소, 실제 주소로 변경 가능
    "세종 빛 축제": "세종특별자치시 보람동 623-1"   # 예시 주소, 실제 주소로 변경 가능
}

# API 요청 헤더
headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}

# 사용자에게 축제 선택 요청
print("사용 가능한 축제: " + ", ".join(festivals.keys()))
selected_festival = input("축제를 선택하세요: ")

# 선택한 축제의 주소 가져오기
address = festivals.get(selected_festival)
if not address:
    print("잘못된 축제 이름입니다. 사용 가능한 축제를 확인하세요.")
    exit()

# 주소를 좌표로 변환 (Kakao Geocoding API)
geo_url = "https://dapi.kakao.com/v2/local/search/address.json"
params = {"query": address}
response = requests.get(geo_url, headers=headers, params=params)

if response.status_code != 200:
    print(f"주소 변환 API 요청 실패 (상태 코드: {response.status_code})")
    exit()

data = response.json()
if not data.get("documents"):
    print("주소를 좌표로 변환할 수 없습니다. 주소를 확인하세요.")
    exit()

x = data["documents"][0]["x"]  # 경도
y = data["documents"][0]["y"]  # 위도

# 좌표를 중심으로 반경 2km 내 맛집 검색 (Kakao Local API)
search_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
params = {"query": "맛집", "x": x, "y": y, "radius": 2000, "size": 15}
response = requests.get(search_url, headers=headers, params=params)

if response.status_code != 200:
    print(f"맛집 검색 API 요청 실패 (상태 코드: {response.status_code})")
    exit()

data = response.json()
places = []
for doc in data.get("documents", []):
    places.append({
        "name": doc.get("place_name", "이름 없음"),
        "address": doc.get("road_address_name", "주소 없음"),
        "phone": doc.get("phone", "전화번호 없음"),
        "url": doc.get("place_url", "URL 없음"),
        "distance": doc.get("distance", "0")  # 거리 정보는 반경 검색 시 항상 제공됨
    })

# 결과 출력
if not places:
    print(f"[{selected_festival}] 반경 2km 내에 맛집이 없습니다.")
else:
    print(f"[{selected_festival}] 반경 2km 맛집 {len(places)}곳:")
    for place in places:
        print(f"{place['name']} - {place['address']} (거리: {place['distance']}m)")