"""
스마트 크롤링 API
- 사용자 요청에 따른 선택적 크롤링
- 데이터 품질 기반 스마트 업데이트
- 실시간 상태 모니터링
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from crawler_manager import crawler_manager, crawl_festival, get_festival_status, clear_festivals
from FestivalType import FestivalType
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/smart/crawl/festival/{festival_type}")
async def smart_crawl_festival(
    festival_type: str,
    force_update: bool = Query(False, description="강제 업데이트 여부")
):
    """
    특정 축제 스마트 크롤링
    
    - festival_type: sejong, light, fire, peach
    - force_update: True면 기존 데이터를 무조건 덮어씀
    """
    try:
        result = crawl_festival(festival_type, force_update)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "message": "스마트 크롤링 완료",
            "festival_type": festival_type,
            "force_update": force_update,
            "result": result
        }
    except Exception as e:
        logger.error(f"스마트 크롤링 실패: {e}")
        raise HTTPException(status_code=500, detail=f"크롤링 실패: {str(e)}")

@router.post("/smart/crawl/all")
async def smart_crawl_all_festivals(
    force_update: bool = Query(False, description="모든 축제 강제 업데이트 여부")
):
    """
    모든 축제 스마트 크롤링
    """
    try:
        results = crawler_manager.crawl_all_festivals(force_update)
        
        return {
            "message": "모든 축제 스마트 크롤링 완료",
            "force_update": force_update,
            "results": results
        }
    except Exception as e:
        logger.error(f"전체 크롤링 실패: {e}")
        raise HTTPException(status_code=500, detail=f"전체 크롤링 실패: {str(e)}")

@router.get("/smart/status")
async def get_smart_status():
    """
    현재 축제 데이터 상태 확인
    - 각 축제의 데이터 품질 점수
    - 업데이트 필요 여부
    """
    try:
        status = get_festival_status()
        
        return {
            "message": "축제 데이터 상태",
            "status": status,
            "total_festivals": len(status) if isinstance(status, dict) else 0
        }
    except Exception as e:
        logger.error(f"상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {str(e)}")

@router.delete("/smart/clear")
async def smart_clear_festivals(
    festival_name: Optional[str] = Query(None, description="삭제할 축제 이름 (없으면 전체 삭제)")
):
    """
    축제 데이터 삭제
    """
    try:
        success = clear_festivals(festival_name)
        
        if not success:
            raise HTTPException(status_code=500, detail="데이터 삭제 실패")
        
        message = f"{festival_name} 축제 데이터 삭제 완료" if festival_name else "모든 축제 데이터 삭제 완료"
        
        return {
            "message": message,
            "deleted_festival": festival_name
        }
    except Exception as e:
        logger.error(f"데이터 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=f"데이터 삭제 실패: {str(e)}")

@router.get("/smart/recommendations")
async def get_smart_recommendations():
    """
    스마트 크롤링 권장사항
    - 어떤 축제를 업데이트해야 하는지 제안
    """
    try:
        status = get_festival_status()
        
        recommendations = []
        
        if isinstance(status, dict):
            for festival_name, data in status.items():
                quality_score = data.get("quality_score", 0)
                
                if quality_score < 50:
                    recommendations.append({
                        "festival": festival_name,
                        "action": "update",
                        "reason": "데이터 품질이 낮음",
                        "current_score": quality_score
                    })
                elif not data.get("has_image"):
                    recommendations.append({
                        "festival": festival_name,
                        "action": "update",
                        "reason": "이미지 정보 없음",
                        "current_score": quality_score
                    })
                elif not data.get("has_description"):
                    recommendations.append({
                        "festival": festival_name,
                        "action": "update", 
                        "reason": "설명 정보 없음",
                        "current_score": quality_score
                    })
        
        return {
            "message": "스마트 크롤링 권장사항",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
    except Exception as e:
        logger.error(f"권장사항 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"권장사항 생성 실패: {str(e)}")

@router.post("/smart/auto-update")
async def smart_auto_update():
    """
    자동 스마트 업데이트
    - 권장사항에 따라 자동으로 필요한 축제만 업데이트
    """
    try:
        # 권장사항 확인
        recommendations_response = await get_smart_recommendations()
        recommendations = recommendations_response.get("recommendations", [])
        
        if not recommendations:
            return {
                "message": "업데이트가 필요한 축제가 없습니다",
                "updated_festivals": []
            }
        
        # 권장사항에 따라 업데이트
        updated_festivals = []
        for rec in recommendations:
            if rec["action"] == "update":
                festival_name = rec["festival"]
                
                # 축제 이름을 타입으로 변환
                festival_type_map = {
                    "세종축제": "sejong",
                    "세종 빛 축제": "light", 
                    "세종낙화축제": "fire",
                    "조치원복숭아축제": "peach"
                }
                
                festival_type = festival_type_map.get(festival_name)
                if festival_type:
                    result = crawl_festival(festival_type, force_update=False)
                    if "success" in result or "info" in result:
                        updated_festivals.append({
                            "festival": festival_name,
                            "result": result
                        })
        
        return {
            "message": "자동 스마트 업데이트 완료",
            "updated_festivals": updated_festivals,
            "total_updated": len(updated_festivals)
        }
    except Exception as e:
        logger.error(f"자동 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"자동 업데이트 실패: {str(e)}") 