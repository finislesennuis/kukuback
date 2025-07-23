import requests
from bs4 import BeautifulSoup

urls = [
    # 관광명소 10선 (10개 모두 반영)
    {"url": "https://www.sejong.go.kr/shrUrl/R7lm5XtqhBU98H4MRAZ2.do", "category": "관광명소 10선"},  # 세종호수공원
    {"url": "https://www.sejong.go.kr/shrUrl/ygD8suG5gdkxNNavhLII.do", "category": "관광명소 10선"},  # 국립세종수목원
    {"url": "https://www.sejong.go.kr/shrUrl/1936KMxA08.do", "category": "관광명소 10선"},  # 세종이응다리
    {"url": "https://www.sejong.go.kr/shrUrl/sy2RfOxYtF.do", "category": "관광명소 10선"},  # 베어트리파크
    {"url": "https://www.sejong.go.kr/shrUrl/28fXgyA58G.do", "category": "관광명소 10선"},  # 세종중앙공원
    {"url": "https://www.sejong.go.kr/shrUrl/721mPnu929.do", "category": "관광명소 10선"},  # 국립세종도서관
    {"url": "https://www.sejong.go.kr/shrUrl/eA1jG1A841.do", "category": "관광명소 10선"},  # 대통령기록관
    {"url": "https://www.sejong.go.kr/shrUrl/OE1uHK15j2.do", "category": "관광명소 10선"},  # 정부세종청사 옥상정원
    {"url": "https://www.sejong.go.kr/shrUrl/6GP1sAS15dEsOwY3bts1.do", "category": "관광명소 10선"},  # 조천 벚꽃길
    {"url": "https://www.sejong.go.kr/shrUrl/h5fWF1p560.do", "category": "관광명소 10선"},  # 고복자연공원
    # 한글여행
    {"url": "https://www.sejong.go.kr/shrUrl/24G2VXMi9C.do", "category": "한글여행"},
    # 정원여행
    {"url": "https://www.sejong.go.kr/shrUrl/uXMRv9v5Hg.do", "category": "정원여행"},
    {"url": "https://www.sejong.go.kr/shrUrl/fiv9r7dgoA.do", "category": "정원여행"},
    {"url": "https://www.sejong.go.kr/shrUrl/Z7k9e2O3EZ.do", "category": "정원여행"},
    {"url": "https://www.sejong.go.kr/shrUrl/5cqaBoqZ0y.do", "category": "정원여행"},
    {"url": "https://www.sejong.go.kr/shrUrl/V5RUJ7Ubs1.do", "category": "정원여행"},
    # 박물관여행
    {"url": "https://www.sejong.go.kr/shrUrl/iuiq5Bl8G2.do", "category": "박물관여행"},
    {"url": "https://www.sejong.go.kr/shrUrl/OR5RLo663E.do", "category": "박물관여행"},
    {"url": "https://www.sejong.go.kr/shrUrl/AtkChdx746.do", "category": "박물관여행"},
    {"url": "https://www.sejong.go.kr/shrUrl/OZuUSLL83q.do", "category": "박물관여행"},
    {"url": "https://www.sejong.go.kr/shrUrl/FP52cIoWt3.do", "category": "박물관여행"},
]

def crawl_sejong_place(url, category):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    name = soup.select_one("h2").text.strip() if soup.select_one("h2") else ""
    address = ""
    address_tag = soup.find(text="주소")
    if address_tag:
        next_tag = address_tag.find_next()
        if next_tag:
            address = next_tag.text.strip()
    description = soup.select_one(".cont_txt").text.strip() if soup.select_one(".cont_txt") else ""
    homepage = ""
    homepage_tag = soup.find("a", href=True, text="홈페이지")
    if homepage_tag:
        homepage = homepage_tag["href"]
    return {
        "name": name,
        "category": category,
        "address": address,
        "description": description,
        "homepage": homepage,
        "url": url,
    }

places = []
for item in urls:
    try:
        data = crawl_sejong_place(item["url"], item["category"])
        places.append(data)
    except Exception as e:
        print(f"Error crawling {item['url']}: {e}")

for place in places:
    print(place) 