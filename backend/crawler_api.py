from fastapi import APIRouter, BackgroundTasks
from backend import s_festival, s_light, f_flower, jcwpeach, course_crawler, s_place

router = APIRouter()

@router.post("/crawl/festivals")
async def crawl_festivals(background_tasks: BackgroundTasks):
    """축제 정보 크롤링 실행"""
    background_tasks.add_task(s_festival.run_crawler)
    background_tasks.add_task(s_light.run_crawler)
    background_tasks.add_task(f_flower.run_crawler)
    background_tasks.add_task(jcwpeach.run_crawler)
    return {"message": "축제 크롤링이 시작되었습니다."}

@router.post("/crawl/courses")
async def crawl_courses(background_tasks: BackgroundTasks):
    """여행코스 크롤링 실행"""
    background_tasks.add_task(course_crawler.run_course_crawler)
    return {"message": "여행코스 크롤링이 시작되었습니다."}

@router.post("/crawl/places")
async def crawl_places(background_tasks: BackgroundTasks):
    """주변 장소 크롤링 실행"""
    background_tasks.add_task(s_place.main)
    return {"message": "주변 장소 크롤링이 시작되었습니다."}

@router.post("/crawl/all")
async def crawl_all(background_tasks: BackgroundTasks):
    """모든 크롤링 실행"""
    background_tasks.add_task(s_festival.run_crawler)
    background_tasks.add_task(s_light.run_crawler)
    background_tasks.add_task(f_flower.run_crawler)
    background_tasks.add_task(jcwpeach.run_crawler)
    background_tasks.add_task(course_crawler.run_course_crawler)
    background_tasks.add_task(s_place.main)
    return {"message": "모든 크롤링이 시작되었습니다."} 