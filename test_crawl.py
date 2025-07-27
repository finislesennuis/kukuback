import requests
import json

# ngrok URL
NGROK_URL = "https://60722f2d718d.ngrok-free.app"

def test_local_crawler():
    """로컬 크롤러 테스트"""
    
    # 1. 상태 확인
    print("=== 로컬 크롤러 상태 확인 ===")
    try:
        response = requests.get(f"{NGROK_URL}/")
        print(f"상태: {response.status_code}")
        print(f"응답: {response.json()}")
    except Exception as e:
        print(f"연결 실패: {e}")
        return
    
    # 2. 축제 크롤링 테스트
    print("\n=== 축제 크롤링 테스트 ===")
    try:
        payload = {
            "type": "festival",
            "url": "https://sjfestival.kr"
        }
        response = requests.post(f"{NGROK_URL}/crawl", json=payload)
        print(f"상태: {response.status_code}")
        print(f"응답: {response.json()}")
    except Exception as e:
        print(f"크롤링 실패: {e}")

if __name__ == "__main__":
    test_local_crawler() 