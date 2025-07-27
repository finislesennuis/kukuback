import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv     # <<< 추가: python-dotenv 임포트
from typing import Optional

# .env 파일 로드 (이 줄을 추가하는 것이 핵심입니다)
# 이 함수는 `.env` 파일이 존재하는 경우 해당 파일의 내용을 환경 변수로 로드합니다.
# 애플리케이션 시작 시 한 번만 실행되면 됩니다.
load_dotenv()

class Settings(BaseSettings):
    # 데이터베이스 설정
    # Pydantic 1.x의 BaseSettings는 환경 변수가 설정되어 있지 않으면 기본값을 사용합니다.
    DATABASE_URL: str = "sqlite:///./sejong.db"
    
    # 카카오맵 API 설정
    # 환경 변수 KAKAO_API_KEY가 있다면 그것을 사용하고, 없다면 기본값을 사용합니다.
    KAKAO_API_KEY: str = "a5cc7b65ae5d251113eff578a56cd8f1"
    
    # CORS 설정 (프론트엔드 연동용)
    # 환경 변수 CORS_ORIGINS가 있다면 그것을 사용하고, 없다면 기본값을 사용합니다.
    # 환경 변수에서 리스트를 파싱하려면 추가적인 처리가 필요할 수 있습니다.
    # 만약 환경 변수에 CSV 형태로 설정한다면, 파싱 로직을 추가해야 합니다.
    # 예: CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
    # 지금은 기본값을 그대로 사용한다고 가정하고, 환경 변수에서 로드 시 CSV 파싱 예시를 아래에 추가합니다.
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # React 개발 서버
        "http://localhost:5173",  # Vite 개발 서버
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # 앱 설정
    APP_NAME: str = "세모(세종에서 모하지)"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        # Pydantic 1.x BaseSettings의 Config
        # env_file 설정은 load_dotenv()가 이미 처리했으므로 필수는 아니지만,
        # BaseSettings가 환경 변수를 찾는 방식에 명시성을 더해줄 수 있습니다.
        # 즉, BaseSettings는 기본적으로 환경 변수를 보지만, 이 설정을 통해 특정 파일도 확인하도록 합니다.
        env_file = ".env"
        # env_file_encoding = 'utf-8' # 필요한 경우 인코딩 지정
        # case_sensitive = False # 대소문자 구분 설정 (pydantic-settings에 있던 설정)
                               # Pydantic 1.x BaseSettings도 기본적으로 환경 변수 이름을 대소문자 구분하지 않고 매칭 시도함.
                               # 정확히 일치하는 것을 찾고 없으면 대소문자 무시하고 찾음.

# 전역 설정 인스턴스
settings = Settings()

# CORS_ORIGINS를 환경 변수에서 리스트로 파싱하는 예시 (선택 사항)
# 만약 .env 파일에 CORS_ORIGINS="http://url1, http://url2" 와 같이 설정한다면,
# 아래와 같이 추가적인 파싱 로직이 필요할 수 있습니다.
if os.getenv("CORS_ORIGINS"):
    settings.CORS_ORIGINS = [url.strip() for url in os.getenv("CORS_ORIGINS").split(',')]