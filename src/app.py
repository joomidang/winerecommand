from fastapi import FastAPI
import uvicorn
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.wines import router as wines_router
from database.setup import create_tables, load_sample_data

app = FastAPI(title="와인 추천 API", description="와인 추천 시스템 API")

# API 라우터 등록
app.include_router(wines_router)

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 데이터베이스 초기화"""
    try:
        print("데이터베이스 초기화를 시작합니다...")
        create_tables()
        load_sample_data()
        print("데이터베이스 초기화가 완료되었습니다!")
    except Exception as e:
        print(f"데이터베이스 초기화 중 오류 발생: {e}")

@app.get("/")
def read_root():
    """헬스체크 API"""
    return {"message": "와인 추천 API에 오신 것을 환영합니다!", "status": "healthy"}

@app.get("/health")
def health_check():
    """헬스체크 API"""
    return {"status": "healthy", "message": "API 서버가 정상적으로 작동 중입니다."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
