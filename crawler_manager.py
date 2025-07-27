"""
통합 크롤링 매니저
- 모든 크롤러를 통합 관리
- 스마트한 데이터 업데이트 및 중복 처리
- 사용자 요청에 따른 선택적 크롤링
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from enum import Enum
from database import SessionLocal
from models import Festival, Place, Course, CoursePlace
import logging

# 크롤러 모듈들 import
import s_festival
import s_light
import f_flower
import jcwpeach
import course_crawler
import s_place

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrawlerType(Enum):
    FESTIVAL = "festival"
    PLACE = "place"
    COURSE = "course"

class FestivalType(Enum):
    SEJONG = "sejong"
    LIGHT = "light"
    FIRE = "fire"
    PEACH = "peach"

class CrawlerManager:
    def __init__(self):
        self.crawler_status = {}
        self.last_update = {}
        
    def get_festival_info(self, festival_type: FestivalType) -> Dict[str, Any]:
        """축제별 기본 정보 반환"""
        festival_info = {
            FestivalType.SEJONG: {
                "name": "세종축제",
                "url": "https://sjfestival.kr",
                "crawler": s_festival
            },
            FestivalType.LIGHT: {
                "name": "세종 빛 축제", 
                "url": "https://sejong.go.kr/tour/sub02_0104.do",
                "crawler": s_light
            },
            FestivalType.FIRE: {
                "name": "세종낙화축제",
                "url": "https://sjcf.or.kr/content.do?key=2111060044",
                "crawler": f_flower
            },
            FestivalType.PEACH: {
                "name": "조치원복숭아축제",
                "url": "https://jcwpeach.kr",
                "crawler": jcwpeach
            }
        }
        return festival_info.get(festival_type, {})
    
    def smart_save_festival(self, festival_data: Dict[str, Any], force_update: bool = False) -> bool:
        """
        스마트 축제 데이터 저장
        - 기존 데이터가 있으면 업데이트
        - 새로운 데이터가 더 상세하면 교체
        - force_update=True면 무조건 업데이트
        """
        try:
            db = SessionLocal()
            
            # 기존 데이터 조회 (이름으로만)
            existing = db.query(Festival).filter(Festival.name == festival_data["name"]).first()
            
            if not existing:
                # 새 데이터 생성
                new_festival = Festival(**festival_data)
                db.add(new_festival)
                db.commit()
                logger.info(f"✅ 새 축제 등록: {festival_data['name']} (ID: {new_festival.id})")
                return True
            else:
                # 기존 데이터와 비교하여 업데이트 여부 결정
                should_update = force_update
                
                if not should_update:
                    # 데이터 품질 비교
                    existing_score = self._calculate_data_quality(existing)
                    new_score = self._calculate_data_quality(festival_data)
                    should_update = new_score > existing_score
                
                if should_update:
                    # 기존 데이터 업데이트
                    for key, value in festival_data.items():
                        if key != 'id' and hasattr(existing, key) and value:
                            setattr(existing, key, value)
                    db.commit()
                    logger.info(f"🔄 축제 정보 업데이트: {festival_data['name']} (ID: {existing.id})")
                    return True
                else:
                    logger.info(f"ℹ️ 기존 데이터가 더 우수함: {festival_data['name']}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 축제 저장 실패: {e}")
            return False
        finally:
            db.close()
    
    def _calculate_data_quality(self, data: Any) -> int:
        """데이터 품질 점수 계산 (높을수록 좋음)"""
        score = 0
        
        # Festival 객체인지 Dict인지 확인
        if hasattr(data, '__dict__'):
            # SQLAlchemy 객체
            fields = data.__dict__
        else:
            # Dict 객체
            fields = data
        
        # 필수 필드 점수
        if fields.get('name'):
            score += 10
        if fields.get('date'):
            score += 15
        if fields.get('location'):
            score += 10
        if fields.get('description'):
            score += 20
        if fields.get('contact'):
            score += 5
        if fields.get('image_url'):
            score += 10
        if fields.get('programs'):
            score += 5
        if fields.get('schedule'):
            score += 5
            
        # 설명 길이로 상세도 평가
        description = fields.get('description', '')
        if len(description) > 100:
            score += 10
        elif len(description) > 50:
            score += 5
            
        return score
    
    def crawl_specific_festival(self, festival_type: FestivalType, force_update: bool = False) -> Dict[str, Any]:
        """특정 축제만 크롤링"""
        festival_info = self.get_festival_info(festival_type)
        if not festival_info:
            return {"error": "지원하지 않는 축제 타입"}
        
        try:
            logger.info(f"🎪 {festival_info['name']} 크롤링 시작...")
            
            # 크롤러 실행
            if festival_type == FestivalType.SEJONG:
                data = festival_info['crawler'].crawl_sejong_festival()
            elif festival_type == FestivalType.LIGHT:
                festival_info['crawler'].crawl_sejong_light_festival()
                return {"success": f"{festival_info['name']} 크롤링 완료"}
            elif festival_type == FestivalType.FIRE:
                festival_info['crawler'].crawl_sejong_fire_festival()
                return {"success": f"{festival_info['name']} 크롤링 완료"}
            elif festival_type == FestivalType.PEACH:
                festival_info['crawler'].crawl_jcwpeach_final()
                return {"success": f"{festival_info['name']} 크롤링 완료"}
            
            # 스마트 저장
            if self.smart_save_festival(data, force_update):
                return {"success": f"{festival_info['name']} 크롤링 및 저장 완료"}
            else:
                return {"info": f"{festival_info['name']} - 기존 데이터가 더 우수함"}
                
        except Exception as e:
            logger.error(f"❌ {festival_info['name']} 크롤링 실패: {e}")
            return {"error": f"{festival_info['name']} 크롤링 실패: {str(e)}"}
    
    def crawl_all_festivals(self, force_update: bool = False) -> Dict[str, Any]:
        """모든 축제 크롤링"""
        results = {}
        
        for festival_type in FestivalType:
            result = self.crawl_specific_festival(festival_type, force_update)
            results[festival_type.value] = result
            
        return results
    
    def get_festival_status(self) -> Dict[str, Any]:
        """현재 DB에 저장된 축제 상태 확인"""
        try:
            db = SessionLocal()
            festivals = db.query(Festival).all()
            
            status = {}
            for festival in festivals:
                status[festival.name] = {
                    "id": festival.id,
                    "date": festival.date,
                    "location": festival.location,
                    "quality_score": self._calculate_data_quality(festival),
                    "has_image": bool(festival.image_url),
                    "has_description": bool(festival.description)
                }
            
            return status
        except Exception as e:
            logger.error(f"❌ 상태 확인 실패: {e}")
            return {"error": str(e)}
        finally:
            db.close()
    
    def clear_festival_data(self, festival_name: Optional[str] = None) -> bool:
        """축제 데이터 삭제"""
        try:
            db = SessionLocal()
            
            if festival_name:
                # 특정 축제만 삭제
                deleted = db.query(Festival).filter(Festival.name == festival_name).delete()
                logger.info(f"🗑️ {festival_name} 데이터 삭제: {deleted}개")
            else:
                # 모든 축제 데이터 삭제
                deleted = db.query(Festival).delete()
                logger.info(f"🗑️ 모든 축제 데이터 삭제: {deleted}개")
            
            db.commit()
            return True
        except Exception as e:
            logger.error(f"❌ 데이터 삭제 실패: {e}")
            return False
        finally:
            db.close()

# 전역 매니저 인스턴스
crawler_manager = CrawlerManager()

# 편의 함수들
def crawl_festival(festival_type: str, force_update: bool = False) -> Dict[str, Any]:
    """축제 크롤링 편의 함수"""
    try:
        festival_enum = FestivalType(festival_type)
        return crawler_manager.crawl_specific_festival(festival_enum, force_update)
    except ValueError:
        return {"error": f"지원하지 않는 축제 타입: {festival_type}"}

def get_festival_status() -> Dict[str, Any]:
    """축제 상태 확인 편의 함수"""
    return crawler_manager.get_festival_status()

def clear_festivals(festival_name: Optional[str] = None) -> bool:
    """축제 데이터 삭제 편의 함수"""
    return crawler_manager.clear_festival_data(festival_name) 