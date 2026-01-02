# Upbit API 설정
# %%
import os
from pathlib import Path
from dotenv import load_dotenv

# env_upbit.txt 파일 경로
env_path = Path(__file__).parent.parent / 'env_upbit.txt'
print(f"📂 설정 파일 경로: {env_path}")
print(f"📂 파일 존재 여부: {env_path.exists()}")

# env_upbit.txt 파일 로드
load_dotenv(dotenv_path=env_path)

# 환경변수에서 읽기
access_key = os.getenv('UPBIT_ACCESS_KEY', '1234')
secret_key = os.getenv('UPBIT_SECRET_KEY', '1234')
server_url = os.getenv('UPBIT_SERVER_URL', 'www.google.com')