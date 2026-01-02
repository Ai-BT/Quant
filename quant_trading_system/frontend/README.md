# Quant Trading System Frontend

Vue 3 기반 퀀트 트레이딩 시스템 프론트엔드

## 기능

- ✅ 서버 상태 표시
- ✅ 전략 ON/OFF 버튼
- ✅ 현재 포지션 표
- ✅ 최근 거래 로그 테이블
- ✅ 자동 새로고침 (30초)

## 설치

```bash
cd frontend
npm install
```

## 실행

```bash
npm run dev
```

브라우저에서 http://localhost:5173 접속

## 빌드

```bash
npm run build
```

## 환경 변수

`.env` 파일을 생성하여 API 서버 주소를 설정할 수 있습니다:

```env
VITE_API_BASE_URL=http://localhost:8000
```

기본값은 `http://localhost:8000`입니다.

## 기술 스택

- Vue 3
- Vite
- Axios
- CSS3



