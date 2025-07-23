import requests
from bs4 import BeautifulSoup

urls = [
    "https://www.sejong.go.kr/shrUrl/R7lm5XtqhBU98H4MRAZ2.do",
    "https://www.sejong.go.kr/shrUrl/ygD8suG5gdkxNNavhLII.do",
    "https://www.sejong.go.kr/shrUrl/1936KMxA08.do",
    "https://www.sejong.go.kr/shrUrl/sy2RfOxYtF.do",
    "https://www.sejong.go.kr/shrUrl/28fXgyA58G.do",
    "https://www.sejong.go.kr/shrUrl/721mPnu929.do",
    "https://www.sejong.go.kr/shrUrl/eA1jG1A841.do",
    "https://www.sejong.go.kr/shrUrl/OE1uHK15j2.do",
    "https://www.sejong.go.kr/shrUrl/6GP1sAS15dEsOwY3bts1.do",
    "https://www.sejong.go.kr/shrUrl/h5fWF1p560.do",
]

def crawl_sejong_place(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    # 임시 selector, 실제 구조에 맞게 조정 필요
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
        "address": address,
        "description": description,
        "homepage": homepage,
        "url": url,
    }

places = []
for url in urls:
    try:
        data = crawl_sejong_place(url)
        places.append(data)
    except Exception as e:
        print(f"Error crawling {url}: {e}")

for place in places:
    print(place) 
