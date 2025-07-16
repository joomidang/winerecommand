# Dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 SQLite 설치
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 데이터베이스 및 모델 디렉토리 생성
RUN mkdir -p /app/data
RUN mkdir -p /app/models

# 시작 스크립트 실행 권한 부여
RUN chmod +x start.sh

# 포트 노출 (FastAPI/Flask용)
EXPOSE 8000

# 기본 명령어 설정 (시작 스크립트 사용)
CMD ["./start.sh"]