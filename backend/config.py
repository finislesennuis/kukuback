import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./sejong.db"
    
    # 카카오맵 API 설정
    KAKAO_API_KEY: str = "a5cc7b65ae5d251113eff578a56cd8f1"
    
    # CORS 설정 (프론트엔드 연동용)
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
        env_file = ".env"

# 전역 설정 인스턴스
settings = Settings() 