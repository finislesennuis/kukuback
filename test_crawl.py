
import requests

# ngrok이 만들어준 주소를 여기에 붙여넣으세요!
ngrok_url = "https://26d5dbdbff2b.ngrok-free.app/crawl"

# 크롤링할 실제 URL
data = {
    "url": "http://sjfestival.kr/"
}

# POST 요청 보내기
response = requests.post(ngrok_url, json=data)

# 결과 출력
print("응답 코드:", response.status_code)
print("응답 내용:", response.json())