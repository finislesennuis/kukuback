from database import SessionLocal
from models import Festival, Course, CoursePlace, Place

db = SessionLocal()

print("🎪 축제 정보:")
print("=" * 50)
festivals = db.query(Festival).all()
for f in festivals:
    print(
        f"ID: {f.id}\n"
        f"이름: {f.name}\n"
        f"기간: {f.date}\n"
        f"시간: {f.time}\n"
        f"장소: {f.location}\n"
        f"설명: {f.description}\n"
        f"연락처: {f.contact}\n"
        f"포스터: {f.image_url}\n"
        f"프로그램: {f.programs}\n"
        f"행사 일정: {f.schedule}\n"
        f"홈페이지 주소: {f.url}\n"
        "-----------------------------"
    )

print("\n🗺️ 여행 코스별 정보:")
print("=" * 50)
courses = db.query(Course).all()
for c in courses:
    print(f"📍 코스: {c.name}")
    print(f"   코스 ID: {c.id}")
    print(f"   상세URL: {c.detail_url}")
    print(f"   이미지: {c.img}")
    print()
    
    # 이 코스에 포함된 장소들 조회
    course_places = db.query(CoursePlace).filter(CoursePlace.course_id == c.id).all()
    
    if course_places:
        print(f"   🎯 포함된 장소들 ({len(course_places)}개):")
        for i, cp in enumerate(course_places, 1):
            # 장소 상세 정보 조회
            place = db.query(Place).filter(Place.name == cp.place_name).first()
            if place:
                print(f"   {i}. {place.name}")
                print(f"      📍 주소: {place.address}")
                print(f"      🗺️ 좌표: {place.lat}, {place.lng}")
                print(f"      📝 설명: {place.description}")
                print()
            else:
                print(f"   {i}. {cp.place_name} (상세정보 없음)")
                print()
    else:
        print("   ⚠️ 포함된 장소가 없습니다.")
        print()
    
    print("=" * 50)

print(f"\n📊 총계:")
print(f"축제: {len(festivals)}개")
print(f"코스: {len(courses)}개")

# 전체 장소 수 계산
total_places = db.query(Place).count()
print(f"전체 장소: {total_places}개")

db.close()
