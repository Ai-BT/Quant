# 안정성 및 신뢰성 기능

24시간 무중단 운영을 위한 안정성 기능들입니다.

## 구현된 기능

### 1. 로깅 시스템 (`app/core/logging.py`)

**기능:**
- 파일 로그 (RotatingFileHandler) - 로그 파일 자동 로테이션
- DB 로그 - Mock 데이터 저장소에 로그 기록
- 콘솔 로그 - 개발 시 확인용
- 로그 레벨별 분류 (INFO, WARNING, ERROR, DEBUG)
- 로그 타입별 분류 (system, strategy, order)

**사용법:**
```python
from app.core.logging import get_logger

logger = get_logger(__name__, "strategy")
logger.info("전략 시작")
logger.error("에러 발생", exc_info=True)
```

**로그 파일 위치:**
- `logs/app.log` - 메인 로그 파일
- `logs/app.log.1`, `logs/app.log.2`, ... - 백업 파일 (최대 5개)

### 2. 프로세스 상태 모니터링 (`app/core/monitoring.py`)

**기능:**
- CPU 사용률 모니터링
- 메모리 사용량 모니터링 (프로세스 + 시스템)
- 디스크 사용량 모니터링
- 프로세스 정보 (PID, 상태, 스레드 수 등)
- 시스템 정보 (플랫폼, 아키텍처 등)
- 업타임 추적

**API:**
- `GET /api/v1/health/metrics` - 시스템 메트릭 조회
- `GET /api/v1/monitoring/system` - 시스템 메트릭 조회

### 3. 전략 자동 재시작 (`app/core/strategy_manager.py`)

**기능:**
- 전략 상태 관리 (실행 중인 전략 추적)
- 하트비트 모니터링 (5분 이상 응답 없으면 재시작)
- 자동 재시작 로직 (최대 5회 시도)
- 에러 카운트 및 기록
- 재시작 간격 제어 (1분 대기)

**동작 방식:**
1. 전략 시작 시 StrategyManager에 등록
2. 백그라운드 작업이 1분마다 모든 전략 상태 확인
3. 하트비트 타임아웃(5분) 또는 에러 발생 시 자동 재시작
4. 최대 재시작 횟수(5회) 초과 시 중지

**API:**
- `GET /api/v1/monitoring/strategies` - 실행 중인 전략 상태 조회
- `GET /api/v1/monitoring/strategies/{strategy_id}` - 특정 전략 상태 조회

### 4. 작업 상태 저장 및 재개 (`app/core/job_state.py`)

**기능:**
- 작업 상태를 JSON 파일로 저장
- 서버 재시작 후 작업 상태 복구 가능
- 작업 재개 기능
- 작업 상태 조회 및 관리

**저장 위치:**
- `state/{job_id}.json` - 각 작업별 상태 파일

**API:**
- `GET /api/v1/monitoring/jobs` - 작업 상태 목록 조회
- `GET /api/v1/monitoring/jobs/{job_id}` - 특정 작업 상태 조회
- `POST /api/v1/monitoring/jobs/{job_id}/resume` - 작업 재개

### 5. 향상된 헬스 체크 (`app/api/v1/health.py`)

**기능:**
- 기본 헬스 체크: 서버 상태, 업타임, 버전
- 상세 헬스 체크: 시스템 메트릭, 전략 상태, 작업 상태
- 자동 상태 판단 (healthy, degraded)

**API:**
- `GET /api/v1/health` - 기본 헬스 체크
- `GET /api/v1/health/detailed` - 상세 헬스 체크
- `GET /api/v1/health/metrics` - 시스템 메트릭

### 6. 전역 예외 처리 (`app/core/exception_handler.py`)

**기능:**
- 모든 예외를 로그에 기록
- 일관된 에러 응답 형식
- 요청 검증 에러 처리
- HTTP 예외 처리

## 백그라운드 작업

애플리케이션 시작 시 자동으로 시작되는 백그라운드 작업:

1. **전략 모니터링 작업**
   - 1분마다 실행 중인 전략 상태 확인
   - 하트비트 타임아웃 감지
   - 자동 재시작 트리거

## 사용 예시

### 전략 시작 (자동 재시작 포함)
```python
# API 호출
POST /api/v1/strategies/strategy_1/start

# StrategyManager가 자동으로:
# 1. 전략 시작
# 2. 상태 추적 시작
# 3. 작업 상태 저장
# 4. 백그라운드 모니터링에 등록
```

### 작업 재개
```python
# 서버 재시작 후 작업 재개
POST /api/v1/monitoring/jobs/strategy_strategy_1/resume

# 저장된 상태 파일에서 복구하여 작업 재개
```

### 시스템 상태 확인
```python
# 상세 헬스 체크
GET /api/v1/health/detailed

# 응답 예시:
{
  "status": "healthy",
  "version": "v1",
  "uptime": {...},
  "system": {
    "cpu": {...},
    "memory": {...},
    "disk": {...}
  },
  "strategies": {
    "total_running": 2,
    "strategies": [...]
  },
  "jobs": {
    "total": 2,
    "running": 2,
    "paused": 0,
    "failed": 0
  }
}
```

## 모니터링 권장사항

1. **헬스 체크 주기적 호출**
   - 외부 모니터링 도구에서 `/api/v1/health` 주기적 호출
   - 상태가 "degraded"일 때 알림

2. **로그 모니터링**
   - `logs/app.log` 파일 모니터링
   - ERROR 레벨 로그 알림 설정

3. **시스템 리소스 모니터링**
   - 메모리 사용률 90% 이상 시 알림
   - 디스크 사용률 90% 이상 시 알림

4. **전략 상태 모니터링**
   - 실행 중인 전략의 하트비트 확인
   - 재시작 횟수 모니터링

## 다음 단계

실제 운영 환경에서는:
1. Supervisor 또는 Systemd로 프로세스 자동 재시작
2. Docker Health Check 설정
3. 외부 모니터링 도구 연동 (Prometheus, Grafana 등)
4. 알림 시스템 연동 (Slack, Email 등)


