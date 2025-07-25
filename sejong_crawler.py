import requests
from bs4 import BeautifulSoup

urls = [
    # 관광명소 10선 (10개 모두 반영)
    {"url": "https://www.sejong.go.kr/shrUrl/R7lm5XtqhBU98H4MRAZ2.do", "category": "관광명소 10선"},
    {"url": "https://www.sejong.go.kr/shrUrl/ygD8suG5gdkxNNavhLII.do", "category": "관광명소 10선"},
    {"url": "https://www.sejong.go.kr/shrUrl/1936KMxA08.do", "category": "관광명소 10선"},
    {"url": "https://www.sejong.go.kr/shrUrl/sy2RfOxYtF.do", "category": "관광명소 10선"},
    {"url": "https://www.sejong.go.kr/shrUrl/28fXgyA58G.do", "category": "관광명소 10선"},
    {"url": "https://www.sejong.go.kr/shrUrl/721mPnu929.do", "category": "관광명소 10선"},
    {"url": "https://www.sejong.go.kr/shrUrl/eA1jG1A841.do", "category": "관광명소 10선"},
    {"url": "https://www.sejong.go.kr/shrUrl/OE1uHK15j2.do", "category": "관광명소 10선"},
    {"url": "https://www.sejong.go.kr/shrUrl/6GP1sAS15dEsOwY3bts1.do", "category": "관광명소 10선"},
    {"url": "https://www.sejong.go.kr/shrUrl/h5fWF1p560.do", "category": "관광명소 10선"},
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
    # 이름
    name = soup.select_one("strong.caption-title.h2")
    name = name.text.strip() if name else ""
    # 정보 리스트
    info_list = soup.select("div.caption-inner ul li")
    address = info_list[0].get_text(strip=True) if len(info_list) > 0 else ""
    contact = info_list[1].get_text(strip=True) if len(info_list) > 1 else ""
    homepage = ""
    if len(info_list) > 2:
        a_tag = info_list[2].find("a")
        if a_tag:
            homepage = a_tag["href"]
    return {
        "name": name,
        "category": category,
        "address": address,
        "contact": contact,
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
