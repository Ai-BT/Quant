# 💰 Upbit Balance Checker

Upbit 거래소의 계좌 잔고를 조회하는 간단한 스크립트

## 📋 기능

- Upbit API를 통한 계좌 잔고 조회
- 보유 중인 암호화폐 목록 출력
- 주요 통화 (BTC, ETH, XRP 등) 필터링

## 🚀 사용 방법

### 1. 환경 설정

```bash
# 필요한 패키지 설치
pip install PyJWT requests python-dotenv
```

### 2. API 키 설정

1. `env.example` 파일을 `.env` 로 복사
2. Upbit에서 발급받은 API 키를 입력

```bash
cp env.example .env
```

`.env` 파일 내용:
```
UPBIT_ACCESS_KEY=your_actual_access_key
UPBIT_SECRET_KEY=your_actual_secret_key
UPBIT_SERVER_URL=https://api.upbit.com
```

### 3. 실행

```bash
python check_balance.py
```

## 📊 출력 예시

```
============================================================
💰 Upbit 계좌 잔고
============================================================
  KRW:    1,234,567.00000000
  BTC:         0.12345678
  ETH:         1.50000000
============================================================
```

## ⚠️ 주의사항

- API 키는 절대 공개하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다
- 조회 권한만 있는 API 키를 사용하는 것을 권장합니다

## 📝 라이선스

MIT License

