# 🚀 스마트 크롤러 사용 가이드

## 📋 개요

기존 크롤러의 중복 데이터 문제를 해결하기 위해 **스마트 크롤링 시스템**을 구축했습니다.

### 🎯 주요 특징

1. **데이터 품질 기반 스마트 업데이트**
   - 기존 데이터와 새 데이터의 품질을 비교
   - 더 상세한 정보가 있을 때만 업데이트

2. **선택적 크롤링**
   - 특정 축제만 크롤링 가능
   - 사용자 요청에 따른 유연한 대응

3. **실시간 상태 모니터링**
   - 현재 데이터 상태 확인
   - 업데이트 필요 여부 자동 판단

## 🔧 API 사용법

### 1. 특정 축제 크롤링

```bash
# 세종축제만 크롤링
POST /api/smart/crawl/festival/sejong

# 강제 업데이트 (기존 데이터 덮어쓰기)
POST /api/smart/crawl/festival/sejong?force_update=true
```

**지원하는 축제 타입:**
- `sejong` - 세종축제
- `light` - 세종 빛 축제  
- `fire` - 세종낙화축제
- `peach` - 조치원복숭아축제

### 2. 모든 축제 크롤링

```bash
# 모든 축제 스마트 크롤링
POST /api/smart/crawl/all

# 강제 업데이트
POST /api/smart/crawl/all?force_update=true
```

### 3. 데이터 상태 확인

```bash
# 현재 축제 데이터 상태
GET /api/smart/status
```

응답 예시:
```json
{
  "message": "축제 데이터 상태",
  "status": {
    "세종축제": {
      "id": 1,
      "date": "2025.04.26 ~ 2025.04.27",
      "location": "세종호수공원",
      "quality_score": 85,
      "has_image": true,
      "has_description": true
    }
  },
  "total_festivals": 1
}
```

### 4. 스마트 권장사항

```bash
# 업데이트가 필요한 축제 확인
GET /api/smart/recommendations
```

응답 예시:
```json
{
  "message": "스마트 크롤링 권장사항",
  "recommendations": [
    {
      "festival": "세종 빛 축제",
      "action": "update",
      "reason": "이미지 정보 없음",
      "current_score": 65
    }
  ],
  "total_recommendations": 1
}
```

### 5. 자동 업데이트

```bash
# 권장사항에 따라 자동 업데이트
POST /api/smart/auto-update
```

### 6. 데이터 삭제

```bash
# 특정 축제 데이터 삭제
DELETE /api/smart/clear?festival_name=세종축제

# 모든 축제 데이터 삭제
DELETE /api/smart/clear
```

## 🎯 사용 시나리오

### 시나리오 1: 사용자가 특정 축제 정보 요청
```bash
# 1. 현재 상태 확인
GET /api/smart/status

# 2. 필요한 축제만 크롤링
POST /api/smart/crawl/festival/sejong

# 3. 결과 확인
GET /api/smart/status
```

### 시나리오 2: 데이터 품질 개선
```bash
# 1. 권장사항 확인
GET /api/smart/recommendations

# 2. 자동 업데이트 실행
POST /api/smart/auto-update
```

### 시나리오 3: 전체 데이터 새로고침
```bash
# 1. 모든 데이터 삭제
DELETE /api/smart/clear

# 2. 모든 축제 크롤링
POST /api/smart/crawl/all
```

## 🔍 데이터 품질 점수 시스템

각 축제 데이터는 다음 기준으로 품질 점수를 계산합니다:

- **기본 필드 (70점)**
  - 이름: 10점
  - 기간: 15점
  - 장소: 10점
  - 설명: 20점
  - 연락처: 5점
  - 이미지: 10점

- **추가 필드 (10점)**
  - 프로그램: 5점
  - 일정: 5점

- **상세도 보너스 (20점)**
  - 설명 길이 > 100자: 10점
  - 설명 길이 > 50자: 5점

**총점: 100점 만점**

## ⚡ 성능 최적화

1. **선택적 크롤링**: 필요한 축제만 크롤링하여 시간 단축
2. **스마트 업데이트**: 기존 데이터가 우수하면 크롤링 생략
3. **품질 기반 판단**: 데이터 품질을 자동으로 평가하여 업데이트 여부 결정

## 🛠️ 문제 해결

### 문제: 크롤링이 실행되지 않음
**해결책:**
```bash
# 1. 상태 확인
GET /api/smart/status

# 2. 강제 업데이트 시도
POST /api/smart/crawl/festival/sejong?force_update=true
```

### 문제: 데이터가 중복으로 저장됨
**해결책:**
```bash
# 1. 기존 데이터 삭제
DELETE /api/smart/clear?festival_name=세종축제

# 2. 다시 크롤링
POST /api/smart/crawl/festival/sejong
```

### 문제: 크롤링 속도가 느림
**해결책:**
```bash
# 1. 권장사항 확인 (불필요한 크롤링 방지)
GET /api/smart/recommendations

# 2. 필요한 축제만 선택적 크롤링
POST /api/smart/crawl/festival/sejong
```

## 📊 모니터링

실시간으로 다음 정보를 모니터링할 수 있습니다:

- 각 축제의 데이터 품질 점수
- 업데이트 필요 여부
- 크롤링 성공/실패 상태
- 데이터 완성도 (이미지, 설명 등)

이 시스템을 통해 효율적이고 스마트한 크롤링이 가능합니다! 🎉 