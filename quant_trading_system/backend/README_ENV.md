# 환경 변수 설정 가이드

## .env 파일 생성

`backend/.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# App Settings
APP_NAME=Quant Trading System
DEBUG=True
API_VERSION=v1

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Upbit API
UPBIT_ACCESS_KEY=1LdkYb1Q3f1HhAm2jxn537waaV99xlDa7Cs2soHY
UPBIT_SECRET_KEY=cSh0MO7SG0tx6AMazHSQ1GXvvZfSyrJBMHVGfc7b
UPBIT_SERVER_URL=https://api.upbit.com
```

## Windows에서 .env 파일 생성 방법

### 방법 1: PowerShell 사용
```powershell
cd quant_trading_system/backend
@"
# App Settings
APP_NAME=Quant Trading System
DEBUG=True
API_VERSION=v1

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Upbit API
UPBIT_ACCESS_KEY=1LdkYb1Q3f1HhAm2jxn537waaV99xlDa7Cs2soHY
UPBIT_SECRET_KEY=cSh0MO7SG0tx6AMazHSQ1GXvvZfSyrJBMHVGfc7b
UPBIT_SERVER_URL=https://api.upbit.com
"@ | Out-File -FilePath .env -Encoding utf8
```

### 방법 2: 메모장 사용
1. `backend` 폴더에서 새 파일 생성
2. 파일 이름을 `.env`로 저장 (확장자 없음)
3. 위의 내용을 복사하여 붙여넣기
4. 저장

### 방법 3: env.example 복사
```bash
cd quant_trading_system/backend
copy env.example .env
# 그 다음 .env 파일을 열어서 Upbit API 키를 실제 값으로 수정
```

## 환경 변수 확인

환경 변수가 제대로 로드되었는지 확인:

```bash
cd quant_trading_system/backend
python scripts/check_env.py
```

## 주의사항

- `.env` 파일은 Git에 커밋되지 않습니다 (`.gitignore`에 포함됨)
- API 키는 절대 공개 저장소에 올리지 마세요
- 실제 운영 환경에서는 환경 변수로 관리하는 것을 권장합니다



