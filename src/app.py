from fastapi import FastAPI
import uvicorn
import os
import sys
import time
import sqlite3

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.wines import router as wines_router
from database.setup import get_db
from models.recommendation_model import recommendation_model

app = FastAPI(title="와인 추천 API", description="와인 추천 시스템 API")

# API 라우터 등록
app.include_router(wines_router)

def wait_for_database(max_retries=30, retry_interval=2):
    """데이터베이스가 준비될 때까지 기다림"""
    print("데이터베이스 준비 상태를 확인합니다...")
    
    for attempt in range(max_retries):
        try:
            # 데이터베이스 파일 존재 확인
            db_path = os.path.join(os.getcwd(), "wine_recommendation.db")
            if not os.path.exists(db_path):
                print(f"데이터베이스 파일을 찾을 수 없습니다. 재시도 {attempt + 1}/{max_retries}")
                time.sleep(retry_interval)
                continue
            
            # 데이터베이스 연결 및 데이터 확인
            db = next(get_db())
            from database.setup import Wine
            wine_count = db.query(Wine).count()
            db.close()
            
            if wine_count > 0:
                print(f"데이터베이스 준비 완료! 총 {wine_count}개의 와인 데이터가 있습니다.")
                return True
            else:
                print(f"데이터베이스에 데이터가 없습니다. 재시도 {attempt + 1}/{max_retries}")
                time.sleep(retry_interval)
                
        except Exception as e:
            print(f"데이터베이스 연결 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            time.sleep(retry_interval)
    
    print("데이터베이스 준비 시간 초과. init-db 서비스가 완료되었는지 확인해주세요.")
    return False

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 데이터베이스 연결 확인 및 모델 로드"""
    if not wait_for_database():
        print("경고: 데이터베이스가 준비되지 않았습니다. API는 제한적으로 작동할 수 있습니다.")
    
    # 추천 모델 로드 시도
    print("추천 모델을 로드합니다...")
    if recommendation_model.is_model_available():
        if recommendation_model.load_model():
            print("추천 모델 로드 완료!")
        else:
            print("경고: 추천 모델 로드에 실패했습니다.")
    else:
        print("경고: 추천 모델 파일을 찾을 수 없습니다. models/ 디렉토리에 모델 파일을 추가해주세요.")

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
